FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies first
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files and install as editable package
COPY . .
RUN pip install --no-cache-dir -e .

EXPOSE 8000
CMD ["uvicorn", "src.glpi_dashboard.services.worker_api:app", "--host", "0.0.0.0", "--port", "8000"]
