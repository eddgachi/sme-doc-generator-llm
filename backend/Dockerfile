FROM python:3.12-slim

# Set working directory and install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Run migrations and start the application
CMD ["sh", "-c", "alembic upgrade head && if [ \"$ENV\" = \"development\" ]; then uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload; else uvicorn app.main:app --host 0.0.0.0 --port 8000; fi"]