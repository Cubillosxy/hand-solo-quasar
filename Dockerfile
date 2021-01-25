FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

COPY ./ /app
ENV PORT=8080

RUN pip install -r /app/requirements.txt
