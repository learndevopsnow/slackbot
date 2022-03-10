import json
import os
from flask import Flask
app = Flask(__name__)

## Load environment variables
### Crowdstrike api variables
app.config['CROWDSTRIKE_API_DOMAIN'] = os.environ.get('CROWDSTRIKE_API_DOMAIN')
app.config['CROWDSTRIKE_CLIENT_ID'] = os.environ.get('CROWDSTRIKE_CLIENT_ID')
app.config['CROWDSTRIKE_CLIENT_SECRET'] = os.environ.get('CROWDSTRIKE_CLIENT_SECRET')

### Crowdstrike slackbot variables
app.config['BOT_ID'] = os.environ.get('BOT_ID')
app.config['SIGNING_SECRET'] = os.environ.get('SIGNING_SECRET')
app.config['SLACK_TOKEN'] = os.environ.get('SLACK_TOKEN')
app.config['VERIFICATION_TOKEN'] = os.environ.get('VERIFICATION_TOKEN')

### Common variables
crowdstrike_cf_proxy = os.environ.get('VCAP_SERVICES')
crowdstrike_cf_proxy_json =  json.loads(crowdstrike_cf_proxy)
app.config['CF_HTTP_PROXY'] = crowdstrike_cf_proxy_json['c-proxy'][0]['credentials']['uri']
app.config['CF_HTTPS_PROXY'] = crowdstrike_cf_proxy_json['c-proxy'][0]['credentials']['uri']
#app.config['CF_HTTP_PROXY'] = 'http://cfrepo-as-a1p.sys.comcast.net:3128'
#app.config['CF_HTTPS_PROXY'] = 'http://cfrepo-as-a1p.sys.comcast.net:3128'
app.config['CROWDSTRIKE_PREFILE_DIR'] = '/tmp/crowdstrike-slackbot-inv-freshpull'
app.config['CROWDSTRIKE_MAINFILE_DIR'] = '/tmp/crowdstrike-slackbot-inv'

## Trigger apps
from bot import cs_slackbot
