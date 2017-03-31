FROM node:latest
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y mongodb
RUN apt-get install redis-server
RUN apt-get install python-pip python-dev build-essential tcl -y
RUN pip install --upgrade pip
COPY . /root/Conformance_Backend
WORKDIR /root/Conformance_Backend
RUN pip instal -r requirements.txt
RUN pip install -U "celery[redis]"
RUN npm install
EXPOSE 3000
CMD ["./run.sh"]
