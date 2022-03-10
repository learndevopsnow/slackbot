## Modules
import csv
import re
import slack
import os
import json
import shutil
import sys
import threading
import time
from api.cs_api import *
from pathlib import Path
from slackeventsapi import SlackEventAdapter
from threading import Thread

## Functions
def crowdstrike_validation(
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
  slack_ts,
):

  validation_response_list = []

  slack_host_list = [i.split('|')[0].replace('<http://', '').replace('```', '') for i in slack_text_object]
  len_of_slack_host_list = len(slack_host_list)

  if len_of_slack_host_list == 0:
    client.chat_postMessage(
      channel=slack_channel_id,
      thread_ts=slack_ts,
      blocks=[
        {
          'type': 'section',
          'text': {
	  'type': 'plain_text',
	  'text': 'Asset list is empty or not in the right format. Requests should be in below format'
	  }
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
    sys.exit()

  if len_of_slack_host_list > 150:
    client.chat_postMessage(
      channel=slack_channel_id,
      thread_ts=slack_ts,
      text='Asset list has more than 150 hosts. Request list should be less than 150'
    )
    sys.exit()

### Check if Crowdstrike inventory file exist, if not make the API call
  if os.path.exists(crowdstrike_mainfile_dir):
    crowdstrike_mainfile_dir_mtime = os.path.getmtime(crowdstrike_mainfile_dir)
    mtime_diff = (time.time() - crowdstrike_mainfile_dir_mtime)/60
    if mtime_diff > 1.5:
      if os.path.exists(crowdstrike_prefile_dir):
        crowdstrike_wait_message(
          client,
          slack_channel_id,
          slack_ts
        )
        crowdstrike_prefile_dir_mtime = os.path.getmtime(crowdstrike_prefile_dir)
        prefile_mtime_diff = (time.time() - crowdstrike_prefile_dir_mtime)/60
        if prefile_mtime_diff > 4:
          shutil.rmtree(crowdstrike_prefile_dir)
          crowdstrike_api_call(
            cf_http_proxy,
            cf_https_proxy,
            crowdstrike_api_domain,
            crowdstrike_client_id,
            crowdstrike_client_secret,
            crowdstrike_mainfile_dir,
            crowdstrike_prefile_dir
          )
        else:
          time.sleep(180) 
      else:
        crowdstrike_wait_message(
          client,
          slack_channel_id,
          slack_ts
        )
        crowdstrike_api_call(
          cf_http_proxy,
          cf_https_proxy,
          crowdstrike_api_domain,
          crowdstrike_client_id,
          crowdstrike_client_secret,
          crowdstrike_mainfile_dir,
          crowdstrike_prefile_dir
        )

  elif os.path.exists(crowdstrike_prefile_dir):
    crowdstrike_wait_message(
      client,
      slack_channel_id,
      slack_ts
      )
    time.sleep(180)

  else:
    crowdstrike_wait_message(
      client,
      slack_channel_id,
      slack_ts
    )
    crowdstrike_api_call(
      cf_http_proxy,
      cf_https_proxy,
      crowdstrike_api_domain,
      crowdstrike_client_id,
      crowdstrike_client_secret,
      crowdstrike_mainfile_dir,
      crowdstrike_prefile_dir
    )

### Check API health
  if os.path.exists(crowdstrike_mainfile_dir):
    crowdstrike_mainfile_dir_mtime = os.path.getmtime(crowdstrike_mainfile_dir)
    mtime_diff = (time.time() - crowdstrike_mainfile_dir_mtime)/60
    if mtime_diff > 8:
      crowdstrike_error_message(
        client,
        slack_channel_id,
        slack_ts
      )
      sys.exit()
  else:
    crowdstrike_error_message(
      client,
      slack_channel_id,
      slack_ts
    )
    sys.exit()

### Validate Crowdstrike request
  if len_of_slack_host_list < 40:
    for host in slack_host_list:
      text_response = host+ ' - No'
      if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host) != None:
        for cs_file in os.listdir(crowdstrike_mainfile_dir):
          crowdstrike_main_file = crowdstrike_mainfile_dir+ '/' +cs_file
          with open(crowdstrike_main_file) as crowdstrike_asset_list:
            if re.search(r'\b{0}\b'.format(host),crowdstrike_asset_list.read()):
              text_response = host+ ' - Yes - '+cs_file
        validation_response_list.append(text_response)
      else:
        if host:
          for cs_file in os.listdir(crowdstrike_mainfile_dir):
            crowdstrike_main_file = crowdstrike_mainfile_dir+ '/' +cs_file
            with open(crowdstrike_main_file) as crowdstrike_asset_list2:
              if host.lower() in crowdstrike_asset_list2.read().lower():
                text_response = host+ ' - Yes - '+cs_file
                break
              else:
                if '.' in host.lower():
                  get_shortname = host.lower().split('.')[0]
                  with open(crowdstrike_main_file) as crowdstrike_asset_list3:
                    if get_shortname in crowdstrike_asset_list3.read().lower():
                      text_response = host+ ' - Yes - '+cs_file
                      break
          validation_response_list.append(text_response)

    slackbot_response_list = "\n".join(validation_response_list)
    client.chat_postMessage(
      channel=slack_channel_id,
      thread_ts=slack_ts,
      text=slackbot_response_list
    )

  else:
    crowdstrike_csv_filename = slack_client_msg_id+ '.csv'
    create_csv_file = open(crowdstrike_csv_filename, "x")
    short_host_list = list(crowdstrike_divide_chunks(slack_host_list, 25))
    for cs_list in short_host_list:
      with open(crowdstrike_csv_filename, 'a', newline='') as crowdstrike_csv_file:
        for host in cs_list:
          csv_response = [host, 'No', 'NA']
          if re.match('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', host) != None:
            for cs_file in os.listdir(crowdstrike_mainfile_dir):
              crowdstrike_main_file = crowdstrike_mainfile_dir+ '/' +cs_file
              with open(crowdstrike_main_file) as crowdstrike_asset_list:
                if re.search(r'\b{0}\b'.format(host),crowdstrike_asset_list.read()):
                  csv_response = [host, 'Yes', cs_file]
            wr = csv.writer(crowdstrike_csv_file, dialect='excel')
            wr.writerow(csv_response)
          else:
            for cs_file in os.listdir(crowdstrike_mainfile_dir):
              crowdstrike_main_file = crowdstrike_mainfile_dir+ '/' +cs_file
              with open(crowdstrike_main_file) as crowdstrike_asset_list2:
                if host.lower() in crowdstrike_asset_list2.read().lower():
                  csv_response = [host, 'Yes', cs_file]
                  break
                else:
                  if '.' in host.lower():
                    get_shortname = host.lower().split('.')[0]
                    with open(crowdstrike_main_file) as crowdstrike_asset_list3:
                      if get_shortname in crowdstrike_asset_list3.read().lower():
                        csv_response = [host, 'Yes', cs_file]
                        break
            wr = csv.writer(crowdstrike_csv_file, dialect='excel')
            wr.writerow(csv_response)
      time.sleep(2)

    client.files_upload(
      channels=slack_channel_id,
      thread_ts=slack_ts,
      file=crowdstrike_csv_filename,
      title=crowdstrike_csv_filename
    )
    os.remove(crowdstrike_csv_filename)

def crowdstrike_wait_message(
  client,
  slack_channel_id,
  slack_ts
):
  slack_wait_response = 'Waiting for data refresh, will update this thread in 3 min'
  client.chat_postMessage(
    channel=slack_channel_id,
    thread_ts=slack_ts,
    text=slack_wait_response
  )

def crowdstrike_error_message(
  client,
  slack_channel_id,
  slack_ts
):
  slack_error_response = 'Please reachout to @bhanu_vuyyuru as Crowdstrike api is not responsive'
  client.chat_postMessage(
    channel=slack_channel_id,
    thread_ts=slack_ts,
    text=slack_error_response
  )

def crowdstrike_divide_chunks(l, n):
    for i in range(0, len(l), n):  
        yield l[i:i + n]

def crowdstrike_api_call(
  cf_http_proxy,
  cf_https_proxy,
  crowdstrike_api_domain,
  crowdstrike_client_id,
  crowdstrike_client_secret,
  crowdstrike_prefile_dir,
  crowdstrike_mainfile_dir
):
  crowdstrikeapicall_thr = Thread(
                        target=crowdstrike_api_pull,
                        args=[
                          cf_http_proxy,
                          cf_https_proxy,
                          crowdstrike_api_domain,
                          crowdstrike_client_id,
                          crowdstrike_client_secret,
                          crowdstrike_prefile_dir,
                          crowdstrike_mainfile_dir
                        ]
                      )
  crowdstrikeapicall_thr.start()
  crowdstrikeapicall_thr.join()
