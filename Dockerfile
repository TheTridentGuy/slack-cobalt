FROM python:3.13-slim
WORKDIR /
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install --no-cache-dir cobalt_api/
RUN rm -rf cobalt_api
CMD ["python3", "app.py"]