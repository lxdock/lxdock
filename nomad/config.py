import yaml

class Config(dict):
    def __init__(self, path):
        self.homedir = path.resolve().parent
        with path.open('rb') as fp:
            d = yaml.load(fp)
        self.update(d)
