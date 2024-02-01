# washerbot

For quite a while I've been using one of the Etekcity smart plugs with my ghcr.io/jcostom/plugmon container to monitor our washer. For whatever reason, it's become impossibly hard to come by any of those plugs, apart from the outdoor ones.

So, I'm flipping to a Kasa plug that's got energy monitoring. In my case I've got one of their KP115 models, but with the Kasa API, pretty much any plug with energy monitoring should be able to get the job done.

Check out the accompanying example docker-compose file for the variables you need defined. At a minimum, you need the IP of the plug, and your Telegram bot info.

As a bonus compared vs plugmon, this doesn't need Internet access, as the python-kasa module does all local communication with the plug.

As of v1.0 of the container, multiple notification types are supported. Yes, you can do multiple notification types simultaneously too!

## Setting up Pushover

1. Sign up for an account at the [Pushover](https://pushover.net/) website and install the app on your device(s). Make note of your User Key in the app. It's easy to find it in the settings.

2. Follow their [API Docs](https://pushover.net/api) to create yourself an app you intend to use.

3. Pass the variables USE_PUSHOVER (set this to 1!), PUSHOVER_APP_TOKEN, and PUSHOVER_USER_KEY into the container and magic will happen.

## Setting up Pushbullet

1. Sign up for an account at the Pushbullet website.

2. In the Settings > Account page, setup an API key.

3. Pass the variables USE_PUSHBULLET and PUSHBULLET_APIKEY to the container and wait for magic.

## Setting up Alexa Notifications

1. Add the "Notify Me" skill to your Alexa account

2. Note the accessCode value from the email you got from the skill.

3. Pass the variables USE_ALEXA and ALEXA_ACCESSCODE to the container, and wait for the glowing ring on your Echo!
