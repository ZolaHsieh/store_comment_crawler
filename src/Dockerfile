FROM python:3.9.7

WORKDIR /usr/app

RUN  apt-get update && apt-get install -y \ 
    libsasl2-dev \
    python-dev \
    libldap2-dev \
    libssl-dev \
    apt-transport-https \
    mariadb-client

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN groupadd -r python && useradd -r -g python python

USER python

ENTRYPOINT ["tail", "-f", "/dev/null"]