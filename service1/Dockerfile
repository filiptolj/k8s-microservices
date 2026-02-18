FROM ghcr.io/openfaas/classic-watchdog:0.3.7@sha256:79dfbda2f09392335e1b19f1030c4797db3adce841ff744a089d636eeb205a1f AS watchdog

FROM python:3.12-slim
COPY --from=watchdog /fwatchdog /usr/bin/fwatchdog

ENV fprocess="python /entrypoint.py"
COPY entrypoint.py /entrypoint.py

EXPOSE 8080
CMD ["fwatchdog"]
