FROM python:3.6-stretch
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV ORIGIN="127.0.0.1:80" PORT="80" PREFIX="" LOG_LEVEL="info"
COPY ./app /app

ENTRYPOINT ["./entrypoint.sh"]