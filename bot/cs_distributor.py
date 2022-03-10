#!/usr/bin/python3
## Modules
import slack
import os
import json
from slackeventsapi import SlackEventAdapter
from threading import Thread
from bot.cs_validation import *
from bot.cs_help import *

## Functions
def crowdstrike_distributor(
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
):

  if 'validate' in slack_text_task.lower():
    client.chat_postMessage(
      channel=slack_channel_id,
      thread_ts=slack_ts,
      text='validating'
    )
    crowdstrike_validation_thr = Thread(
                              target=crowdstrike_validation,
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
                                slack_ts
                              ]
                            )
    crowdstrike_validation_thr.start()

  else:
    crowdstrike_help_thr = Thread(
                        target=crowdstrike_help,
                        args=[
                          client,
                          slack_channel_id,
                          slack_client_msg_id,
                          slack_event_adapter,
                          slack_ts
                        ]
                      )
    crowdstrike_help_thr.start()
