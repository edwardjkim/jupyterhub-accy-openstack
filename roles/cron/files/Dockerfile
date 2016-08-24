FROM ubuntu:14.04
MAINTAINER Edward J Kim <edward.junhyung.kim@gmail.com>

ENV TZ America/Chicago

RUN apt-get update && \
    apt-get -y install \
        git \
        moreutils \
        python

ADD crontab /etc/cron.d/crontab
ADD release_assignment.py /tmp/release_assignment.py
RUN chmod +x /tmp/release_assignment.py

RUN chmod 0644 /etc/cron.d/crontab
RUN touch /var/log/cron.log

CMD cron && tail -f /var/log/cron.log
