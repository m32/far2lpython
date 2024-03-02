#!/usr/bin/env vpython3
import os
import configparser
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        #logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

class Config:
    def __init__(self, home):
        self.inipath = os.path.join(home, 'adb.ini')
        self.config = configparser.ConfigParser()
        self.config['adb'] = {
            'box': 'default',
            'execute': 'False',
        }

    def load(self):
        try:
            self._load()
        except:
            log.exception('load config')

    def _load(self):
        if os.path.isfile(self.inipath):
            with open(self.inipath, "rt") as fp:
                self.config.read_file(fp)

    def save(self):
        try:
            self._save()
        except:
            log.exception('save config')

    def _save(self):
        with open(self.inipath, "wt") as fp:
            self.config.write(fp)

    @property
    def box(self):
        return self.config.get('adb', 'box')

    @box.setter
    def box(self, value):
        self.config.set('adb', 'box', value)

    @property
    def execute(self):
        return self.config.getboolean('adb', 'execute')

    @execute.setter
    def execute(self, value):
        self.config.set('adb', 'execute', str(value))


USERHOME = os.path.expanduser('~/.config/far2l/plugins/python')
cfg = Config(USERHOME)
cfg.load()
print('box=', cfg.box)
print('exec=', cfg.execute)
cfg.save()
