**GENERAL INFO**

The following possible dependencies were omitted due to the "no external dependency" requirement:
* supervisord (for runtime management)
* sqlalchemy (or other, simpler, ORM)
* scrapy (for crawler implementation)

The base image for the Stronghold Paste image is `ubuntu:latest` with Python 3.5 installed.
It is a huge image and probably not the best choice, but it was used for its simplicity to speed up the implementation process.

**INSTALLATION**

Make sure TOR is installed and running. It should listen on port 9050.
You may use a TOR Docker image for that purpose. For example:
`docker run -p 9050:9050 --name tor osminogin/tor-simple`

Pull and run the Stronghold Paste scraper Docker image:
`docker run shemsu/strongscrape`

