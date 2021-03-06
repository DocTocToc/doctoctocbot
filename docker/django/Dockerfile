FROM python:3.8 AS prod

ENV PYTHONUNBUFFERED 1
ENV DOCKER_CONTAINER 1

RUN apt-get clean && apt-get update && apt-get install -y \
  locales \
  python-pygraphviz \
  libgraphviz-dev \
  build-essential \
  libgl1-mesa-glx \
  libgtk-3-dev \
  libdbus-glib-1-2
#  python3-dev \
#  python3-pip \
#  python3-setuptools \
#  python3-wheel \
#  python3-cffi \
#  libcairo2 \
#  libpango-1.0-0 \
#  libpangocairo-1.0-0 \
#  libgdk-pixbuf2.0-0 \
#  libffi-dev \
#  shared-mime-info

RUN echo "Europe/Paris" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
#    sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    sed -i -e 's/# fr_FR.UTF-8 UTF-8/fr_FR.UTF-8 UTF-8/' /etc/locale.gen && \
    echo 'LANG="fr_FR.UTF-8"'>/etc/default/locale && \
    dpkg-reconfigure --frontend=noninteractive locales && \
    update-locale LANG=fr_FR.UTF-8

RUN locale -a
ENV LANG fr_FR.UTF-8
ENV LANGUAGE fr_FR
ENV LC_ALL fr_FR.UTF-8

ADD ./requirements /code/requirements
RUN pip install --upgrade pip
RUN pip install --upgrade -r /code/requirements/common.txt

RUN mkdir /var/log/celery && touch /var/log/celery/celery.log
RUN mkdir /var/log/gunicorn && touch /var/log/gunicorn/gunicorn.log
RUN mkdir /code/src

WORKDIR /code/src

ENV PYTHONPATH "$PYTHONPATH:/code/src/doctocnet:/code/src"
ENV DJANGO_SETTINGS_MODULE doctocnet.settings

ARG FIREFOX_VERSION=78.0.2esr
RUN wget --no-verbose -O /tmp/firefox.tar.bz2 https://ftp.mozilla.org/pub/firefox/releases/$FIREFOX_VERSION/linux-x86_64/en-US/firefox-78.0.2esr.tar.bz2 \
   && rm -rf /opt/firefox \
   && tar -C /opt -xjf /tmp/firefox.tar.bz2 \
   && rm /tmp/firefox.tar.bz2 \
   && mv /opt/firefox /opt/firefox-$FIREFOX_VERSION \
   && ln -fs /opt/firefox-$FIREFOX_VERSION/firefox /usr/bin/firefox

RUN mkdir /geckodriver
ADD https://github.com/mozilla/geckodriver/releases/download/v0.26.0/geckodriver-v0.26.0-linux64.tar.gz /geckodriver
RUN cd /geckodriver && tar -xzf *.tar.gz && rm geckodriver-v0.26.0-linux64.tar.gz
ENV PATH "$PATH:/geckodriver"

FROM prod AS dev

RUN apt-get clean && apt-get update && apt-get install -y \
  postgresql-client \
  gettext

RUN pip install --upgrade -r /code/requirements/development.txt