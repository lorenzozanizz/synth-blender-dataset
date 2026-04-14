from typing import Dict, SupportsIndex, Union
from time import time


class TimingContext:

    def __init__(self, res_dict: Union[Dict, SupportsIndex], key: str):
        """ Create a timing context object with a given target dictionary and a key

        :param res_dict: a target indexable
        :param key: the key to which the value is to be written
        """
        self.ref_dict = res_dict
        self.key = key
        self.start = None

    def __enter__(self):
        """ Capture the initial time """
        self.start = time()

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Update the reference dictionary with the given key """
        end_time = time()
        self.ref_dict[self.key] = end_time - self.start