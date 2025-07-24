FROM python:3.11-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt
COPY . .
RUN pip install .

FROM python:3.11-slim
RUN useradd -m appuser
WORKDIR /app
COPY --from=builder /usr/local /usr/local
COPY --from=builder /app /app
USER appuser
EXPOSE 80
CMD ["uvicorn", "src.backend.api.worker_api:app", "--host", "0.0.0.0", "--port", "80"]
