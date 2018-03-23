FROM python:3.6.4-alpine3.7
MAINTAINER tsu-shiuan@zappistore.com

WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ADD snapshooter.py .
ADD helper_methods.py .
ADD config.yml .

CMD ["/bin/sh"]
