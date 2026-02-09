FROM python:3.14-slim
WORKDIR /app
COPY python_requirements.txt .
RUN pip install --no-cache-dir -r python_requirements.txt
COPY ./backend/app /app
EXPOSE 8000
