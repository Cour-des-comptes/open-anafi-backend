FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN pip install --upgrade pip
RUN apt update
RUN apt -y install rabbitmq-server
RUN service rabbitmq-server start
COPY local_config.ini /opt/local_config.ini
RUN mkdir /code
RUN mkdir /home/vagrant/
WORKDIR /code
ADD . /code/
RUN pip install -r requirements.txt
EXPOSE 8000
#RUN bash start.sh