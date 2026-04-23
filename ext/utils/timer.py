""" A small module containing an auxiliary timing module used throughout the code
to monitor the rendering, labeling time in the preview and possibly in other places.

Classes:
    TimingContext: The main timing object, which allows to time the time it takes
    to complete a python context and save the time under a label in a given dictionary.

Example:

    >>> from ext.utils.timer import TimingContext
    >>> timings = {}
    >>> with TimingContext(timings, 'timer_name'):
    >>>     ex = None
    >>> print("Time is", timings['timer_name'])
"""

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
