# Crowdstrike Slackbot
Python code for Crowdstrike slackbot

This bot helps customers with
- Asset Reporting (To validate if asset is reporting to console or not)

- Future goals
  - Agent Installation Steps
  - Agent Troubleshooting
  - FAQ's

## Prerequisite
### Applications
- Org space in [Cloud Foundry](https://apa.comcast.net/cf/index/)
- Org space in [Hashicorp Vault](https://github.comcast.com/TP-PSP/VaultPolicies)

| Secrets                     | Description                                  |
|-----------------------------|----------------------------------------------|
| `BOT_ID`                    | Slackbot ID                                  |
| `SIGNING_SECRET`            | Slackbot signing secret                      |
| `SLACK_TOKEN`               | Slack OAuth token                            |
| `VERIFICATION_TOKEN`        | Slack verfication token to validate requests |
| `CROWDSTRIKE_API_DOMAIN`    | Crowdstrike API url                          |
| `CROWDSTRIKE_CLIENT_ID`     | Crowdstrike client id                        |
| `CROWDSTRIKE_CLIENT_SECRET` | Crowdstrike client secret                    |

- Repository in [Comcast dockerhub](https://docker.hub.comcast.net)
- [Slackbot](https://api.slack.com/apps) in your org
  - Add below scopes under `OAuth & Permissions`
    - app_mention:read
    - chat:write
    - files:write

  - Add below scopes under `Event Subscriptions` >> `Subscribe to bot events`
    - app_mention

### Deployment Packages
- Python3
- hvac
- Cloud Foundry [CLI](https://github.com/cloudfoundry/cli/releases)
- docker
- Hashicorp vault [CLI](https://www.vaultproject.io/downloads)

### Development packages
Addition to deployment packages you need to have below for development
- Flask
- requests
- slackclient
- slackeventsapi
- urllib3

## Usage
### Docker
- Build docker image
```
cd crowdstrike-slackbot
docker build -t crowdstrike-slackbot .
```
- Tag the docker image
```
docker tag crowdstrike-slackbot <docker_hub>/<docker_repo>/crowdstrike-slackbot:[tag]
```
- Push docker image to docker hub
```
docker push <docker_hub>/<docker_repo>/crowdstrike-slackbot:[tag]
```

### Cloud Foundry
- Authenticate to Cloud Foundry and choose your environment
```
cf login -a <cloud_foundry_site> -u <NTID>
```
:warning: **If you are deploying the app for the first time, you need to create route and service**
- Deploy app to Cloud Foundry
```
cd crowdstrike-slackbot
CF_DOCKER_PASSWORD=[redacted] cf push --no-start
```

### Vault
- Authenticate to vault (I am using OIDC example, but you can also use GitHub or AD)
```
export VAULT_ADDR=<vault_addr>
vault login -method=oidc role=<oidc_role>
```
- Export Vault token
```
export VAULT_TOKEN=<temp_vault_token>
```
- Pass secrets to Cloud Foundry
```
export CF_APP=crowdstrike-slackbot-prod
python3 vault/cs_get_secrets.py
```

### Start App
- Start app in Cloud Foundry
```
cf start crowdstrike-slackbot-prod
```

### Slack
- Update Slack events API under `Event Subscriptions`
```
Enable 'Enable Events'
Add <cloud_foundry_route>/crowdstrikeslack/events
Save changes
```
