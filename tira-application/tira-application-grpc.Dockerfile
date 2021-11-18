FROM python:3-alpine
# 1. setup user and system software

RUN apk update &&\
    apk add linux-headers &&\
    apk add --no-cache --virtual .build-deps gcc linux-headers make musl-dev python3-dev &&\
    apk add --no-cache g++ &&\
    apk add --update --no-cache python3 zip py3-virtualenv
# NOTE: We'll install it here, so rebuilding the image when testing application code is faster.
# If we install requirements after copying the code, the install layer has to be redone every time.
RUN python3 -m pip install --no-cache-dir grpcio==1.36.1 protobuf Django pyyaml grpcio-tools==1.36.1

RUN addgroup --gid 1010 tira && \
	adduser --disabled-password --uid 1010 --ingroup tira tira && \
	adduser tira root

# 2. copy sources
RUN mkdir /tira
RUN mkdir -p /mnt/ceph/tira

COPY tira-application /tira/tira-application
COPY tira-protocol/build/python/* /tira/tira-application/src/tira/proto/
COPY tira-model/src/* /mnt/ceph/tira/model/
COPY tira-application/config/settings-deploy.yml /tira/tira-application/src/config/settings.yml

RUN chown -R tira:tira /usr/local && \
	chmod 777 /var/run/ && \
	echo "tira ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers &&\
	touch /var/log/tira_debug.txt &&\
	touch /tira/tira-application/src/debug.log &&\
	chown tira:tira /var/log/tira_debug.txt &&\
	chown tira:tira  /tira/tira-application/src/debug.log &&\
	mkdir -p /home/tira/.tira &&\
	mkdir -p /mnt/ceph/tira/log/tira-application &&\
	mkdir /home/tira/.ssh &&\
	mkdir /mnt/ceph/tira/state &&\
	touch /mnt/ceph/tira/state/tira_vm_states.sqlite3 &&\
	chown tira:tira -R /home/tira &&\
	chown tira:tira -R /tira

# 4. make the sources
WORKDIR /tira/tira-application

RUN apk del .build-deps

CMD python3 src/run_grpc_server.py