FROM python:3.13-slim
RUN pip install --no-cache-dir Flask==3.1.3
COPY runner.py /runner.py
COPY supervisor.py /supervisor.py
LABEL cyber.build.protocol="ready-v1"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
USER 65534:65534
ENTRYPOINT ["python", "-I", "/supervisor.py"]
