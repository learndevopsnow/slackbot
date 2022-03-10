## Docker info
FROM centos:7
MAINTAINER "Sathya Bhanu Vuyyuru"

## Environment variables
ENV container docker
ENV PORT=8080
EXPOSE ${PORT}
ENV LANG=en_US.UTF-8

## App setup
### Worker directory
RUN mkdir /root/crowdstrike-slackbot

### Copying code
COPY api /root/crowdstrike-slackbot/api/
COPY bot /root/crowdstrike-slackbot/bot/
COPY entrypoint.sh /usr/local/bin
COPY requirements.txt /root/requirements.txt
COPY run_bot.py /root/crowdstrike-slackbot/run_bot.py

## Package prerequisite
RUN yum update -y &&\
    yum install gcc python3 python3-pip python3-devel unzip -y &&\
    pip3 install -r /root/requirements.txt

## Entrypoint
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["entrypoint.sh"]
