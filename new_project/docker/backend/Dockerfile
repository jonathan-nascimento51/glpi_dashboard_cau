FROM python:3.11-slim
WORKDIR /app
COPY ../../requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt
USER non-root
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
