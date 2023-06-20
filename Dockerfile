FROM python:3.11-slim as build

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 5000
CMD [ "python", "./s2.py" ]

