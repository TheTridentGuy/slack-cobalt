# cobalt-slack

## Slack bot that responds to media links with the raw media. Uses a [cobalt API](https://github.com/imputnet/cobalt) instance fetch raw media.

## Running it for yourself:

* First set up a [cobalt API](https://github.com/imputnet/cobalt) instance.
* Then set up a Slack bot on [api.slack.com/apps](https://api.slack.com/apps). You can select "create from a manifest",
  and paste in the contents of `manifest.json`.
* Set up your `.env` file from this template:

```dotenv
COBALT_API_INSTANCE=https://api.your.cobalt.instance/
COBALT_API_KEY=your-api-key-omit-for-no-auth
SLACK_BOT_TOKEN=xoxb-bot-token
SLACK_APP_TOKEN=xapp-token
```

### Run from prebuilt docker images (linux/arm64, linux/amd64):

* Run the prebuilt images with: `docker run --name cobalt-slack thetridentguy/slack-media-bot:latest --env-file .env`

### Build your own images:

* Clone the repo: `git clone https://github.com/TheTridentGuy/cobalt-slack`
* Enter the cloned repo: `cd cobalt-slack`
* Build the image: `docker build .`
* Run the built image: `docker run --name cobalt-slack <built_image_hash> --env-file .env`

The bot will automatically upload media from supported services in channels that it's added to.
