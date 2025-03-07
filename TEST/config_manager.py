import json

class ConfigManager:
    def __init__(self, config_path=None):
        self.channels = {}
        self.graphs = {}
        if config_path:
            self.load_config(config_path)

    def load_config(self, path):
        with open(path, 'r') as f:
            config = json.load(f)
            self.channels = config.get('channels', {})
            self.graphs = config.get('graphs', {})