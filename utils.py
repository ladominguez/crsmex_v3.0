import os
import json

def load_configuration():
    root_crsmex = os.environ["ROOT_CRSMEX_V3"]
    config_file = open(os.path.join(root_crsmex, 'config.json'))
    return json.load(config_file)