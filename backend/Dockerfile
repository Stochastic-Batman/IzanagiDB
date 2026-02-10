FROM python:3.14-slim
WORKDIR /app
COPY python_requirements.txt .
RUN pip install --no-cache-dir -r python_requirements.txt
COPY generate_keys.py .
RUN python3 generate_keys.py
COPY ./backend/app /app
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
