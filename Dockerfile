#FROM python:3.10-alpine3.19
#LABEL authors="jorgejr568"
#
## install postgresql-client, sqlite3, bash, curl and nano
#RUN apk add --no-cache postgresql-client postgresql-libs sqlite bash curl nano
#RUN apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
## set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#
## set working directory
#WORKDIR /app
#COPY requirements.txt .
#
## install dependencies
#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt
#
## copy project
#COPY . .
#
#CMD ["uvicorn", "main:app", "--host", "0.0.0.0:8000"]


# Convert the previous Dockerfile to debian slim

FROM python:3.10-slim
LABEL authors="jorgejr568"

# install postgresql-client, sqlite3, bash, curl and nano
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    sqlite3 \
    bash \
    curl \
    nano \
    libpq-dev \
    gcc \
    python3-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# set environment variables \
ENV PYTHONDONTWRITEBYTECODE 1

# set working directory
WORKDIR /app

COPY requirements.txt .

# install dependencies
RUN pip install --upgrade pip

RUN pip install -r requirements.txt

# copy project
COPY . .

CMD ["uvicorn", "main:app", "--port", "8000", "--host", "0.0.0.0"]