FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
COPY requirements-core.txt /requirements-core.txt
RUN pip install -U -r /requirements-core.txt pip
COPY image_processor /app/image_processor
