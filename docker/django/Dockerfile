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
  libdbus-glib-1-2 \
  python-yaml \
  binutils \
  libproj-dev \
  gdal-bin

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
RUN pip install pip==21.0.1
RUN pip install --upgrade -r /code/requirements/common.txt

RUN mkdir /var/log/celery && touch /var/log/celery/celery.log
RUN mkdir /var/log/gunicorn && touch /var/log/gunicorn/gunicorn.log
RUN mkdir /code/src

WORKDIR /code/src

ENV PYTHONPATH "$PYTHONPATH:/code/src/doctocnet:/code/src"
ENV DJANGO_SETTINGS_MODULE doctocnet.settings

FROM prod AS dev

RUN apt-get clean && apt-get update && apt-get install -y \
  postgresql-client \
  gettext

RUN pip install --upgrade -r /code/requirements/development.txt