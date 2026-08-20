FROM python:3.11-slim

# Install system dependencies and Microsoft ODBC Driver 17
RUN apt-get update && apt-get install -y curl gnupg2 apt-utils build-essential unixodbc-dev
RUN curl https://microsoft.com | apt-key add -
RUN curl https://microsoft.com > /etc/apt/sources.list.p/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
