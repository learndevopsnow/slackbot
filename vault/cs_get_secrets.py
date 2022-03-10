import hvac
import json
import os
import requests
import datetime
import subprocess
import time

## Authenticate to Hashicorp Vault
vault_client = hvac.Client(url=os.environ['VAULT_ADDR'], token=os.environ['VAULT_TOKEN'])

## Get Crowdstrike slackbot and api secrets from vault
crowdstrike_api_secrets = vault_client.read('secret/securityendpointtoolsteam/concourse-ci/crowdstrike/prod')
crowdstrike_slack_secrets = vault_client.read('secret/securityendpointtoolsteam/concourse-ci/slack/crowdstrike/prod')

### Slack variables
VT_BOT_ID = crowdstrike_slack_secrets['data']['BOT_ID']
VT_SIGNING_SECRET = crowdstrike_slack_secrets['data']['SIGNING_SECRET']
VT_SLACK_TOKEN = crowdstrike_slack_secrets['data']['SLACK_TOKEN']
VT_VERIFICATION_TOKEN = crowdstrike_slack_secrets['data']['VERIFICATION_TOKEN']

### Crowdstrike variables
VT_CROWDSTRIKE_API_DOMAIN = crowdstrike_api_secrets['data']['CROWDSTRIKE_API_DOMAIN']
VT_CROWDSTRIKE_CLIENT_ID = crowdstrike_api_secrets['data']['CROWDSTRIKE_CLIENT_ID']
VT_CROWDSTRIKE_CLIENT_SECRET = crowdstrike_api_secrets['data']['CROWDSTRIKE_CLIENT_SECRET']

### Cloud Foundry variables
CF_APP = os.environ['CF_APP']

## POST variables to CF
subprocess.run(['cf', 'set-env', CF_APP, 'BOT_ID', VT_BOT_ID])
subprocess.run(['cf', 'set-env', CF_APP, 'SIGNING_SECRET', VT_SIGNING_SECRET])
subprocess.run(['cf', 'set-env', CF_APP, 'SLACK_TOKEN', VT_SLACK_TOKEN])
subprocess.run(['cf', 'set-env', CF_APP, 'VERIFICATION_TOKEN', VT_VERIFICATION_TOKEN])
subprocess.run(['cf', 'set-env', CF_APP, 'CROWDSTRIKE_API_DOMAIN', VT_CROWDSTRIKE_API_DOMAIN])
subprocess.run(['cf', 'set-env', CF_APP, 'CROWDSTRIKE_CLIENT_ID', VT_CROWDSTRIKE_CLIENT_ID])
subprocess.run(['cf', 'set-env', CF_APP, 'CROWDSTRIKE_CLIENT_SECRET', VT_CROWDSTRIKE_CLIENT_SECRET])
