import logging
from Stac import STAC


logging.basicConfig(level=logging.INFO)
url = "https://api.eneslab.pilot.eosc-beyond.eu/"
client = STAC(url)

collections = client.getcollections()

print (collections)
