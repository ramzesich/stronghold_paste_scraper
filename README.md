**GENERAL INFO**

The following possible dependencies were omitted due to the "no external dependency" requirement:
* supervisord (for runtime management)
* sqlalchemy (or other, simpler, ORM)
* scrapy (for crawler implementation)

The "line too long" warning from Flake8 is ignored, since it is 2016 now and our widescreen monitors are somewhat wider than 80 chars.
See PEP 8: "A Foolish Consistency is the Hobgoblin of Little Minds".

The base image for the Stronghold Paste image is `ubuntu:latest` with Python 3.5 installed.
It is a huge image and probably not the best choice, but it was used for its simplicity to speed up the implementation process.

**INSTALLATION**

Make sure TOR is accessible. For example, you can run it locally using a Docker container: 

`docker run -d -p 9050:9050 --name tor osminogin/tor-simple`

Pull and run the Stronghold Paste scraper Docker image:

`docker run -d --network host --name scraper shemsu/strongscrape`

By default the Stronghold Paste application expects TOR to run on localhost and be available on port 9050. The hostname can be changed by using the `--tor-host` option like below:

`docker run -d --network host --name scraper shemsu/strongscrape --tor-host 10.0.0.5`
