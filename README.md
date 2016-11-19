**INSTALLATION**

Make sure TOR is accessible. For example, you can run it locally using a Docker container: 

`docker run -d -p 9050:9050 --name tor osminogin/tor-simple`

Pull and run the Stronghold Paste scraper Docker image:

`docker run -d --network host --name scraper shemsu/strongscrape`

By default the Stronghold Paste application expects TOR to run on localhost and be available on port 9050. The hostname can be changed by using the `--tor-host` option like below:

`docker run -d --network host --name scraper shemsu/strongscrape --tor-host 10.0.0.5`
