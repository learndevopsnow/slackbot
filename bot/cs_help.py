## Modules
import slack
import os
import json
from slackeventsapi import SlackEventAdapter

## Functions
def crowdstrike_help(
  client,
  slack_channel_id,
  slack_client_msg_id,
  slack_event_adapter,
  slack_ts
):
  client.chat_postMessage(
    channel=slack_channel_id,
    thread_ts=slack_ts,
    blocks=[
      {
        'type': 'section',
	'text': {
	  'type': 'plain_text',
	  'text': 'Hi, I am eps_crowdstrike bot'
	}
      },
      {
	'type': 'section',
	'fields': [
	  {
            'type': 'mrkdwn',
            'text': '*Intro:*\nI am here to help you with asset reporting, you can send me a request using below template. The request has to be in a new message.\n\n*`Please don\'t reply to this thread`*'
	  }
	]
      },
      {
        'type': 'section',
	'fields': [
	  {
            'type': 'mrkdwn',
	    'text': '*Example Template:*\n@eps_crowdstrike validate\n```example1.comcast.com\nexample2.comcast.com\nexample3.comcast.com```'
	  }
	]
      }
    ]
  )
