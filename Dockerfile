FROM python:3.13.4-slim-bookworm AS builder

ARG TZ=America/New_York

RUN apt update && DEBIAN_FRONTEND=noninteractive apt -yq install gcc make
RUN \
    pip install requests python-kasa==0.6.2.1 python-telegram-bot \
    && pip cache purge

FROM python:3.13.4-slim-bookworm

ARG TZ=America/New_York
ARG PYVER=3.13

COPY --from=builder /usr/local/lib/python$PYVER/site-packages/ /usr/local/lib/python$PYVER/site-packages/

RUN mkdir /app
COPY ./washerbot.py /app
RUN chmod 755 /app/washerbot.py

ENTRYPOINT [ "python3", "-u", "/app/washerbot.py" ]
