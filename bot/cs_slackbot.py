#!/usr/bin/python3
## Modules
import slack
import os
import json
from bot import app
from slackeventsapi import SlackEventAdapter
from threading import Thread
from bot.cs_distributor import *

## Variables
### Slack variables
bot_id = app.config['BOT_ID']
slack_event_adapter = SlackEventAdapter(app.config['SIGNING_SECRET'], '/crowdstrikeslack/events', app)
client = slack.WebClient(token=app.config['SLACK_TOKEN'], proxy=app.config['CF_HTTPS_PROXY'])
verification_token = app.config['VERIFICATION_TOKEN']

### Cloud Foundry variables
cf_http_proxy = app.config['CF_HTTP_PROXY']
cf_https_proxy = app.config['CF_HTTPS_PROXY']

### Crowdstrike API variables
crowdstrike_api_domain = app.config['CROWDSTRIKE_API_DOMAIN']
crowdstrike_client_id = app.config['CROWDSTRIKE_CLIENT_ID']
crowdstrike_client_secret = app.config['CROWDSTRIKE_CLIENT_SECRET']
crowdstrike_prefile_dir = app.config['CROWDSTRIKE_PREFILE_DIR']
crowdstrike_mainfile_dir = app.config['CROWDSTRIKE_MAINFILE_DIR']

@slack_event_adapter.on('app_mention')
## Functions
def message(payload):
  slack_event = payload.get('event', {})
  slack_client_msg_id = slack_event.get('client_msg_id')
  slack_channel_id = slack_event.get('channel')
  slack_request_token = payload['token']
  slack_ts = slack_event.get('ts')
  slack_user_id = slack_event.get('user')
  slack_text = slack_event.get('text')
  slack_text_object = slack_text.split('\n')
  slack_text_task = slack_text_object.pop(0)

  if verification_token != slack_request_token:
    return False
  else:
    if bot_id != slack_user_id:
      client.chat_postMessage(
        channel=slack_channel_id,
        thread_ts=slack_ts,
        text='Request received'
      )
      crowdstrike_distributor_thr = Thread(
                                 target=crowdstrike_distributor,
                                 args=[
                                   cf_http_proxy,
                                   cf_https_proxy,
                                   client,
                                   crowdstrike_api_domain,
                                   crowdstrike_client_id,
                                   crowdstrike_client_secret,
                                   crowdstrike_mainfile_dir,
                                   crowdstrike_prefile_dir,
                                   slack_channel_id,
                                   slack_client_msg_id,
                                   slack_event_adapter,
                                   slack_text_object,
                                   slack_text_task,
                                   slack_ts
                                 ]
                               )
      crowdstrike_distributor_thr.start()

### Slackbot healthcheck
@app.route('/crowdstrikeslack/health')
def crowdstrike_healthcheck():
    return 'I am alive'
