import logging

from tira.authentication import auth
from tira.checks import check_permissions, check_resources_exist, check_conditional_permissions
from tira.forms import *
from django.http import HttpResponse, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from http import HTTPStatus
import json

import tira.tira_model as model

logger = logging.getLogger("tira")
logger.info("ajax_routes: Logger active")


def handle_get_model_exceptions(func):
    def decorate(request, *args, **kwargs):
        if request.method == 'GET':
            try:
                msg = func(*args, **kwargs)
                return JsonResponse({'status': 0, 'message': msg}, status=HTTPStatus.OK)
            except Exception as e:
                logger.exception(f"{func.__name__} failed with {e}", e)
                return JsonResponse({'status': 1, 'message': f"{func.__name__} failed with {e}"},
                                    status=HTTPStatus.INTERNAL_SERVER_ERROR)

        return JsonResponse({'status': 1, 'message': f"{request.method} is not allowed."}, status=HTTPStatus.FORBIDDEN)

    return decorate


@check_permissions
@handle_get_model_exceptions
def admin_reload_data():
    model.build_model()
    if auth.get_auth_source() == 'legacy':
        auth.load_legacy_users()
    return "Model data was reloaded successfully"


@check_permissions
@handle_get_model_exceptions
def admin_reload_vms():
    model.reload_vms()
    return "VM data was reloaded successfully"


@check_permissions
@handle_get_model_exceptions
def admin_reload_datasets():
    model.reload_datasets()
    return "Dataset data was reloaded successfully"


@check_permissions
@handle_get_model_exceptions
def admin_reload_tasks():
    model.reload_tasks()
    return "Task data was reloaded successfully"


@check_conditional_permissions(restricted=True)
@handle_get_model_exceptions
def admin_reload_runs(vm_id):
    model.reload_runs(vm_id)
    return "Runs data was reloaded for {} on {} successfully"


@check_permissions
def admin_create_vm(request):  # TODO implement
    """ Hook for create_vm posts. Responds with json objects indicating the state of the create process. """

    if request.method == "POST":
        print(json.loads(request.body))

        return JsonResponse({'status': 0, 'message': f"Creating VM with TransactionId: dummyId"})

    return JsonResponse({'status': 1, 'message': f"GET is not implemented for vm create"},
                        status=HTTPStatus.NOT_IMPLEMENTED)


@check_permissions
def admin_archive_vm():
    return JsonResponse({'status': 1, 'message': f"Not implemented"}, status=HTTPStatus.NOT_IMPLEMENTED)


@check_permissions
def admin_modify_vm():
    return JsonResponse({'status': 1, 'message': f"Not implemented"}, status=HTTPStatus.NOT_IMPLEMENTED)


@check_permissions
def admin_create_task(request):
    """ Create an entry in the model for the task. Use data supplied by a model.
     Return a json status message. """

    if request.method == "POST":
        data = json.loads(request.body)

        master_vm_id = data["master_id"]
        task_id = data["task_id"]
        organizer = data["organizer"]

        if not model.vm_exists(master_vm_id):
            return JsonResponse({'status': 1, 'message': f"Master VM with ID {master_vm_id} does not exist"})
        if not model.organizer_exists(organizer):
            return JsonResponse({'status': 1, 'message': f"Organizer with ID {organizer} does not exist"})
        if model.task_exists(task_id):
            return JsonResponse({'status': 1, 'message': f"Task with ID {task_id} already exist"})

        new_task = model.create_task(task_id, data["name"], data["description"], data["master_id"],
                                     data["organizer"], data["website"],
                                     help_command=data["help_command"], help_text=data["help_text"])
        new_task = json.dumps(new_task, cls=DjangoJSONEncoder)
        return JsonResponse({'status': 0, 'context': new_task,
                             'message': f"Created Task with Id: {data['task_id']}"})

    return JsonResponse({'status': 1, 'message': f"GET is not implemented for vm create"},
                        status=HTTPStatus.NOT_IMPLEMENTED)


@check_permissions
def admin_add_dataset(request):
    """ Create an entry in the model for the task. Use data supplied by a model.
     Return a json status message. """

    context = {}

    if request.method == "POST":
        form = AddDatasetForm(request.POST)
        if form.is_valid():
            # TODO should be calculated from dataset_name
            dataset_id_prefix = form.cleaned_data["dataset_id_prefix"]
            dataset_name = form.cleaned_data["dataset_name"]
            master_vm_id = form.cleaned_data["master_vm_id"]
            task_id = form.cleaned_data["task_id"]
            command = form.cleaned_data["command"]
            working_directory = form.cleaned_data["working_directory"]
            measures = [line.split(',') for line in form.cleaned_data["measures"].split('\n')]

            # sanity checks
            context["status"] = "fail"
            try:
                model.get_vm(master_vm_id)
            except KeyError as e:
                logger.error(e)
                context["add_dataset_form_error"] = f"Master VM with ID {master_vm_id} does not exist"
                return JsonResponse(context)

            try:
                model.get_task(task_id)
            except KeyError as e:
                logger.error(e)
                context["add_dataset_form_error"] = f"Task with ID {task_id} does not exist"
                return JsonResponse(context)

            try:
                new_paths = []
                if form.cleaned_data["create_training"]:
                    new_paths += model.add_dataset(task_id, dataset_id_prefix, "training", dataset_name)
                    model.add_evaluator(master_vm_id, task_id, dataset_id_prefix, "training", command,
                                        working_directory, measures)

                if form.cleaned_data["create_test"]:
                    new_paths += model.add_dataset(task_id, dataset_id_prefix, "test", dataset_name)
                    model.add_evaluator(master_vm_id, task_id, dataset_id_prefix, "test", command, working_directory,
                                        measures)

                if form.cleaned_data["create_dev"]:
                    new_paths += model.add_dataset(task_id, dataset_id_prefix, "dev", dataset_name)
                    model.add_evaluator(master_vm_id, task_id, dataset_id_prefix, "dev", command, working_directory,
                                        measures)

                context["status"] = "success"
                context["created"] = {"dataset_id": dataset_id_prefix, "new_paths": new_paths}

            except KeyError as e:
                logger.error(e)
                context["create_task_form_error"] = f"Could not create {dataset_id_prefix}: {e}"
                return JsonResponse(context)
        else:
            context["create_task_form_error"] = "Form Invalid (check formatting)"
            return JsonResponse(context)
    else:
        HttpResponse("Permission Denied")

    return JsonResponse(context)


# @check_conditional_permissions(restricted=True)
# @check_resources_exist('json')
# def admin_create_group(request, vm_id):
#     """ This is the form endpoint to grant a user permissions on a vm"""
#     context = {"status": 0, "message": ""}
#     if request.method == "POST":
#         form = AdminCreateGroupForm(request.POST)
#         if form.is_valid():
#             vm_id = form.cleaned_data["vm_id"]
#         else:
#             context["create_vm_form_error"] = "Form Invalid (check formatting)"
#             return JsonResponse(context)
#
#     vm = model.get_vm(vm_id)
#     context = auth.create_group(vm)
#
#     return JsonResponse(context)


@check_conditional_permissions(restricted=True)
@check_resources_exist('json')
def admin_create_group(request, vm_id):
    """ this is a rest endpoint to grant a user permissions on a vm"""
    if not model.vm_exists(vm_id):
        return JsonResponse({'status': 1, 'message': f"VM with ID {vm_id} does not exist."})

    vm = model.get_vm(vm_id)
    print(vm)
    message = auth.create_group(vm)
    return JsonResponse({'status': 0, 'message': message})
