FROM python:3.6.4-alpine3.7
MAINTAINER tsu-shiuan@zappistore.com

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt

ADD snapshooter.py /usr/src/app/snapshooter.py
ADD helper_methods.py /usr/src/app/helper_methods.py
ADD config.yml /usr/src/app/config.yml

CMD ["/bin/sh"]
