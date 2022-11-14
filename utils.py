import os
import json

def load_configuration():
    config_file = open('./config.json')
    return json.load(config_file)
