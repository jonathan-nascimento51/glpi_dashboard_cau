FROM python:3.11-slim
WORKDIR /app
COPY ./backend ./backend
RUN pip install fastapi uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
