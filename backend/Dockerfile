# Use Python 3.11 slim base
FROM python:3.11-slim

# Set workdir
WORKDIR /app

# Ensure pip is up-to-date
RUN python -m pip install --upgrade pip

# Copy requirements first to leverage Docker layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Expose port
EXPOSE 8000

# Run uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
