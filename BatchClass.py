import json
import os
from Config import *
import re
import subprocess

class Batch:
    all_batches = []
    def __init__(self, path, sudo=''):
        self.sudo = sudo
        self.directory = Path(path)
        self.init_path = self.directory / 'init.txt'
        self.read_path = self.directory / 'readme.txt'
        self.run_path = self.directory / 'run.bat'

    @staticmethod
    def instantiate_saved_batches():
        saved_dict = json.load(open(json_save_path, 'r'))
        try:
            for k, v in saved_dict['batch_saves'].items():
                instance = Batch(path=v, sudo=k)
                Batch.all_batches.append(instance)
        except KeyError:
            saved_dict['batch_saves'] = {}
            json.dump(saved_dict, open(json_save_path, 'w'))

    def write_init(self, settings:dict):
        if not os.path.exists(self.init_path):
            return
        if settings != {}:
            txt = ''
            with open(self.init_path, 'r') as r:
                txt = r.read()
            for k, v in settings.items():
                match = re.match(fr'{k}::\w+', txt)
                txt.replace(match.group(0), f'{k}::{v}')

    def run_batch(self):
        subprocess.run([self.run_path], cwd=self.directory)

    def save_path(self):
        sudo = self.sudo
        if not self.sudo:
            raise ValueError('Saved Sudonym Cannot be Nothing')
        save_dict = json.load(open(json_save_path, 'r'))
        save_dict['batch_saves'].update({sudo: str(self.directory)})
        json.dump(save_dict, open(json_save_path, 'w'), indent='\t')
        Batch.all_batches.append(self)