#!/usr/bin/python

# Author: Jose Castillo Lema <josecastillolema@gmail.com>
# Author: Alberico Castro <>

"""Main module of the mini-nfv framework"""

#import json
#import logging
#import re
import yaml

SITE = 'https://api2.milvus.com.br/'

def parse_file(path):
    """Parses the yaml file"""
    yaml_file = open(path, 'r')
    content = yaml_file.read()
    parsed_file = yaml.load(content)
    print parsed_file
    print yaml.dump(parsed_file)
    print parsed_file['description']
    print parsed_file['topology_template']['node_templates']['VDU1']
    #r.text_parsed = json.loads(r.text)
    #logging.debug(json.dumps(r.text_parsed, indent=4, sort_keys=True))

if __name__ == '__main__':
    print 'main'
    parse_file('samples/tosca-vnfd-hello-world.yaml')
