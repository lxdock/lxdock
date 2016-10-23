import yaml

class Config(dict):
    def __init__(self, path):
        with path.open('rb') as fp:
            d = yaml.load(fp)
        self.update(d)
