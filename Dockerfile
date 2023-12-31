FROM python:3.10.12
USER root
RUN apt-get -y update && apt-get install -y vim

RUN useradd -m fastapi
USER fastapi
WORKDIR /home/fastapi

ENV DEBUG=0

COPY . .
RUN pip install --no-cache-dir --disable-pip-version-check --upgrade pip
RUN pip install --no-cache-dir --disable-pip-version-check -r requirements/prod.txt
EXPOSE 8000
ENV PATH="/home/fastapi/.local/bin:${PATH}"
CMD ["gunicorn", "src.main:app", "--workers", "4", "--threads", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120", "--preload"]
