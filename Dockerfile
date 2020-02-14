FROM lukauskas/bokeh:latest
RUN apk --update add bash nano
COPY ./app /app