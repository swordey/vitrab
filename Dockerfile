FROM python:3.6-stretch

RUN apt-get update &&  apt-get install libjpeg-dev zlib1g-dev \
  && apt-get -yq autoremove \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Install nodejs (see: https://askubuntu.com/a/720814)
RUN curl -sL https://deb.nodesource.com/setup_8.x | bash \
    && apt-get install nodejs \
    && apt-get -yq autoremove \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG VERSION

COPY ./requirements.txt /var/www/requirements.txt
RUN pip install -r /var/www/requirements.txt

ENV ORIGIN="vitrab.swordey.duckdns.org:80" PORT="80" PREFIX="" LOG_LEVEL="info"
COPY ./app /app

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
