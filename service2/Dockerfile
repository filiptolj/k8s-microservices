FROM ghcr.io/openfaas/classic-watchdog:0.3.7@sha256:79dfbda2f09392335e1b19f1030c4797db3adce841ff744a089d636eeb205a1f AS watchdog

FROM python:3.12-slim@sha256:9e01bf1ae5db7649a236da7be1e94ffbbbdd7a93f867dd0d8d5720d9e1f89fab

RUN useradd --no-create-home --shell /bin/false --uid 1001 appuser

COPY --from=watchdog --chmod=555 /fwatchdog /usr/bin/fwatchdog

RUN pip install --no-cache-dir requests

ENV fprocess="python /entrypoint.py"

COPY --chmod=444 entrypoint.py /entrypoint.py

USER appuser

EXPOSE 8080
CMD ["fwatchdog"]