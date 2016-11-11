FROM ubuntu:latest
MAINTAINER Dmitriy Wild

RUN sed -i 's/archive.ubuntu.com/mirror.us.leaseweb.net/' /etc/apt/sources.list \
    && sed -i 's/deb-src/#deb-src/' /etc/apt/sources.list \
    && apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    net-tools \
    ca-certificates \
    gcc \
    git \
    libpq-dev \
    make \
    pkg-config \
    python3 \
    python3-dev \
    python3-pip \
    && apt-get autoremove -y \
    && apt-get clean

RUN git clone https://github.com/shemsu/stronghold_paste_scraper.git
RUN pip3 install --upgrade pip && pip3 install -r /stronghold_paste_scraper/conf/requirements.txt

RUN mkdir -p /stronghold_paste_scraper/data

WORKDIR /stronghold_paste_scraper/src

RUN python3 scraper_tool.py createdb -c ../conf/settings.ini

CMD python3 scraper_tool.py pastes -c ../conf/settings.ini -th `netstat -nr | grep '^0\.0\.0\.0' | awk '{print $2}'`

