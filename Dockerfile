FROM docker.io/python:3.9.7-buster
MAINTAINER Computer Science House Drink Admins <drink@csh.rit.edu>

RUN apt-get update && \
    apt-get install -y libldap-dev libsasl2-dev libpq-dev && \
    apt-get autoremove --yes && \
    apt-get clean autoclean && \
    mkdir -p /opt/mizu /var/lib/mizu

WORKDIR /opt/mizu
ADD . /opt/mizu

RUN pip install \
    --no-warn-script-location \ 
    --no-cache-dir \
    pipenv

RUN pipenv install --system

RUN groupadd -r mizu && \
    useradd -l -r -u 1001 -d /var/lib/mizu -g mizu mizu && \
    chown -R mizu:mizu /opt/mizu /var/lib/mizu && \
    chmod -R og+wrx /var/lib/mizu

USER mizu

CMD gunicorn "wsgi:app" \
    --workers 1 \
    --threads 8 \
    --timeout 30 \
    --capture-output \
    --bind=0.0.0.0:8080 \
    --access-logfile=-

