FROM python:slim

ARG TZ=America/New_York

RUN \
    pip install python-kasa \
    && pip install python-telegram-bot \
    && pip cache purge

RUN mkdir /app
COPY ./washerbot.py /app
RUN chmod 755 /app/washerbot.py

ENTRYPOINT [ "python3", "-u", "/app/washerbot.py" ]