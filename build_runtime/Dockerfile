FROM python:3.13-slim
RUN pip install --no-cache-dir Flask==3.1.3
COPY runner.py /runner.py
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /workspace
USER 65534:65534
ENTRYPOINT ["python", "-I", "/runner.py"]
