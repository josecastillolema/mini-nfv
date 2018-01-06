#!/usr/bin/python

# Author: Jose Castillo Lema <josecastillolema@gmail.com>
# Author: Alberico Castro <>

import requests
import json
import re
import logging

site = 'https://api2.milvus.com.br/'

def updateStatusOnline ():
  r.text_parsed = json.loads(r.text)
  logging.debug(json.dumps(r.text_parsed, indent=4, sort_keys=True))

if __name__ == '__main__':
    print 'main'
