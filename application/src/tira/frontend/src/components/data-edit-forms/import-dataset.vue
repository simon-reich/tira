<template>
<span v-if="this.importDatasetError !== ''" class="uk-text-danger uk-margin-small-left">{{ this.importDatasetError }}</span>
<div class="uk-card uk-card-small uk-card-default uk-card-body uk-width-1-1">
  <div class="uk-grid-small uk-margin-small" uk-grid>

    <h3 class="uk-card-title uk-width-1-1">
      <div class="uk-grid-small uk-margin-small" uk-grid>
        <span class="uk-text-muted">ID: {{ this.datasetId }}</span>
        <div class="uk-width-expand"></div>
        <div>
          <div class="uk-button uk-button-primary uk-button-small" @click="addDataset">import dataset <font-awesome-icon icon="fas fa-play" /></div>
        </div>
      </div>
    </h3>
    <div class="uk-width-2-5">
          <label>Dataset Name*
          <input class="uk-input" type="text" placeholder="Name of the Dataset"
                 :class="{'uk-form-danger': (this.importDatasetError !== '' && this.datasetNameInput === '')}"
                 v-model="datasetNameInput"></label>
      </div>
      <div class="uk-width-1-5">
          <label>Task*
          <select class="uk-select" v-model="this.selectedTask"
                 :class="{'uk-form-danger': (this.importDatasetError !== '' && this.selectedTask === '')}">
              <option disabled value="">Please select a task</option>
              <option v-for="task in this.taskList" :value="task">{{ task.task_id }}</option>
          </select></label>
      </div>
      <div class="uk-width-1-5 uk-margin-remove-bottom uk-padding-small">
          <div>
              <label><input class="uk-radio" type="radio" name="radio2" value="training" v-model="type"> training</label>
          </div>
          <div>
              <label><input class="uk-radio" type="radio" name="radio2" value="test" v-model="type"> test</label>
          </div>
      </div>

  </div>
</div>
</template>
<script charset="utf-8">
import { get, submitPost } from "../../utils/getpost";
import { slugify } from "../../utils/stringprocessing";

export default {
  data() {
      return {
            importDatasetError: '',
            datasetNameInput: '',
            datasetId: '',
            selectedTask: '',
            type: 'training',
            taskList: [],
      }
  },
  emits: ['addnotification', 'adddataset'],
  props: ['csrf', 'task_id'],
  methods: {
      addDataset() {
          console.log('add dataset')
          this.importDatasetError = ''
          if (this.selectedTask === '') {
              this.importDatasetError += 'Please select a Task;\n'
          }
          if (this.datasetNameInput === '') {
              this.importDatasetError += 'Please provide a name for the new Dataset;\n'
          }
          if (this.importDatasetError !== '') {
              return
          }
          submitPost('/tira-admin/import-irds-dataset', this.csrf, {
              'dataset_id': this.datasetId,
              'name': this.datasetNameInput,
              'task': this.selectedTask.task_id,
              'type': this.type,
          }).then(message => {
              this.$emit('addnotification', 'success', message.message)
              this.$emit('adddataset', message.context)
          }).catch(error => {
              console.log(error)
              this.importDatasetError = error
              this.$emit('addnotification', 'error', error.message)
          })
      },
      getTaskById(task_id){
          for (const task of this.taskList) {
              if (task.task_id === task_id){
                  return task
              }
          }
          return {}
      }
  },
  beforeMount() {
      get(`/api/task-list`).then(message => {
          this.taskList = message.context.task_list
          this.selectedTask = this.getTaskById(this.task_id, this.taskList)
          this.evaluatorWorkingDirectory = '/home/' + this.selectedTask.master_vm_id
      }).catch(error => {
          this.$emit('addnotification', 'error', `Error loading task list: ${error}`)
      })
  },
  watch: {
      datasetNameInput(newName, oldName) {
          this.datasetId = slugify(newName)
      },
      evaluatorWorkingDirectory(newName, oldName) {
          if(newName === ""){
              this.evaluatorWorkingDirectory = '/home/' + this.selectedTask.master_vm_id + '/'
          }
      }
  }
}
</script>
