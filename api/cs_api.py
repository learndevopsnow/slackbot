## Import python modules
import json
import os
import re
import requests
import sys
import socket
import shutil
from datetime import datetime, timedelta

## Functions in python
### Validate host
def crowdstrike_api_pull(
  cf_http_proxy,
  cf_https_proxy,
  crowdstrike_api_domain,
  crowdstrike_client_id,
  crowdstrike_client_secret,
  crowdstrike_mainfile_dir,
  crowdstrike_prefile_dir
  ):

  os.mkdir(crowdstrike_prefile_dir)

  proxyDict = {
    'http': cf_http_proxy,
    'https': cf_https_proxy
  }
### Get Crowdstrike API token
  crowdstrike_token = crowdstrike_api_token(
                        crowdstrike_api_domain,
                        crowdstrike_client_id,
                        crowdstrike_client_secret,
                        proxyDict
                      )

### Get Crowdstrike Host list
  asset_list = []
  device_headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer {}'.format(crowdstrike_token)
  }
  two_hours_ago = datetime.now() + timedelta(hours=-2)
  two_hours_ago_timestamp = two_hours_ago.strftime('%Y-%m-%dT%H:%M:%SZ')
  
  device_url = 'https://' +crowdstrike_api_domain+ '/devices/queries/devices-scroll/v1?limit=5000&filter=last_seen:>="' +two_hours_ago_timestamp+ '"'
  device_response = requests.get(device_url, headers=device_headers, proxies=proxyDict)
  device_resource_ids = device_response.json()['resources']
  offset = device_response.json()['meta']['pagination']['offset']

  while offset:
    device_params = (
      ('offset', offset),
      ('limit', '5000'),
    )
    device_url = 'https://' +crowdstrike_api_domain+ '/devices/queries/devices-scroll/v1?offset=' +offset+ '&limit=5000&filter=last_seen:>="' +two_hours_ago_timestamp+ '"'
    device_response = requests.get(device_url, headers=device_headers, proxies=proxyDict)
    device_resource_ids.extend(device_response.json()['resources'])
    offset = device_response.json()['meta']['pagination']['offset']

  x = list(crowdstrike_divide_chunks(device_resource_ids, 5000))
  for chunk in x:
    entities_response = crowdstrike_host_info(
                          crowdstrike_api_domain,
                          crowdstrike_token,
                          chunk,
                          proxyDict
                        )
    result = entities_response.json()
    if 'resources' not in result:
      break
    else:
      for hostentry in result['resources']:
        if 'agent_version' in hostentry:
          crowdstrike_file_name = crowdstrike_prefile_dir+ '/' +str(hostentry['agent_version'])
        else:
          crowdstrike_file_name = crowdstrike_prefile_dir+ '/unknown'

        savefile = open(crowdstrike_file_name, 'a')

        if 'hostname' in hostentry:
          host_name = hostentry['hostname']
          savefile.write(host_name+'\n')
        if 'local_ip' in hostentry:
          ip_address = hostentry['local_ip']
          savefile.write(ip_address+'\n')
      savefile.close()

  if os.path.isdir(crowdstrike_mainfile_dir):
    shutil.rmtree(crowdstrike_mainfile_dir)
  shutil.move(crowdstrike_prefile_dir, crowdstrike_mainfile_dir)

### Get Crowdstrike API token
def crowdstrike_api_token(
  crowdstrike_api_domain,
  crowdstrike_client_id,
  crowdstrike_client_secret,
  proxyDict
):
  auth_data = 'client_id='+crowdstrike_client_id+'&client_secret='+crowdstrike_client_secret
  auth_headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  auth_url = 'https://' +crowdstrike_api_domain+ '/oauth2/token'
  print("Getting API token")
  auth_response = requests.post(auth_url, headers=auth_headers, data=auth_data, proxies=proxyDict)
  crowdstrike_token = auth_response.json()['access_token']
  return crowdstrike_token

def crowdstrike_divide_chunks(l, n):
    for i in range(0, len(l), n):  
        yield l[i:i + n] 

def crowdstrike_host_info(
  crowdstrike_api_domain,
  crowdstrike_token,
  ids,
  proxyDict
):
  entities_headers = {
      'Accept': 'application/json',
      'Authorization': 'Bearer {}'.format(crowdstrike_token)
  }
  entities_params = (
      ('ids', ids),
  )
  entities_url = 'https://' +crowdstrike_api_domain+ '/devices/entities/devices/v1'
  entities_response = requests.get(entities_url, headers=entities_headers, params=entities_params, proxies=proxyDict)
  print('Adding Lines')
  return entities_response
