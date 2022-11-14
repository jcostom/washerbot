# washerbot

For quite a while I've been using one of the Etekcity smart plugs with my ghcr.io/jcostom/plugmon container to monitor our washer. For whatever reason, it's become impossibly hard to come by any of those plugs, apart from the outdoor ones.

So, I'm flipping to a Kasa plug that's got energy monitoring. In my case I've got one of their KP115 models, but with the Kasa API, pretty much any plug with energy monitoring should be able to get the job done.

Check out the accompanying example docker-compose file for the variables you need defined. At a minimum, you need the IP of the plug, and your Telegram bot info.

As a bonus compared vs plugmon, this doesn't need Internet access, as the python-kasa module does all local communication with the plug.
