FROM python:3.12-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Scalingo requirement)
EXPOSE 5000

# Use Procfile for process management
# Scalingo will use Procfile to determine processes
# CMD is set in Procfile

