from .configurations import WritingConfig

from ..labeling.generator import LabelData

from typing import Union, Collection, Tuple
from pathlib import Path
from os.path import join, dirname, isdir, isfile
from os import makedirs, listdir
from enum import Enum
from abc import ABCMeta, abstractmethod


import re

class FolderStructure(Enum):
    """

    """
    YOLO = "yolo"
    YOLO_SPLIT = "yolo_split"       # images/train, labels/train, etc.
    COCO_FLAT = "coco_flat"         # single dir with annotations.json
    KITTI_3D = "kitti_3d"           # image_2/, label_2/, calib/


class SerializationStrategy(metaclass=ABCMeta):
    """ Abstract base for output formats """

    def __init__(self, write_config: WritingConfig):
        self.config = write_config

    @abstractmethod
    def format(self, label_data: LabelData) -> Collection[Tuple[str, str]]:
        """

        :param label_data:
        :return:
        """
        pass

    @abstractmethod
    def get_subdir(self, ext: str) -> str:
        """

        :param ext:
        :return:
        """
        pass

    @abstractmethod
    def mark_beginning(self) -> None:
        """

        :return:
        """
        pass

    @abstractmethod
    def mark_end(self) -> None:
        """

        :return:
        """
        pass


class YoloFormatter(SerializationStrategy):

    def mark_beginning(self) -> None:
        return

    def mark_end(self) -> None:
        return

    def __init__(self, write_config: WritingConfig):
        super().__init__(write_config)

    def format(self, label_data: LabelData) -> Collection[Tuple[str, str]]:
        return ('.txt', "Jewish boy!"),

    def get_subdir(self, ext: str) -> str:
        if 'txt' in ext:
            return 'labels'
        elif 'image' in ext:
            return 'images'
        return ""

class YoloSplitFormatter(SerializationStrategy):

    def __init__(self, write_config: WritingConfig):
        super().__init__(write_config)

    def format(self, label_data: LabelData) -> Collection[Tuple[str, str]]:
        pass

    def get_subdir(self, ext: str) -> str:
        if 'image' in ext:
            pass
        else:
            subdir = f"images/{self.config.split}"


class CocoFormatter(SerializationStrategy):

    def mark_beginning(self) -> None:
        pass

    def mark_end(self) -> None:
        pass

    def __init__(self, write_config: WritingConfig):
        super().__init__(write_config)

    def format(self, label_data: LabelData) -> Collection[Tuple[str, str]]:
        pass

    def get_subdir(self, ext: str) -> str:
        pass


class OutputWriter:

    def __init__(self, config: WritingConfig, strategy: SerializationStrategy = None):
        self.config = config
        self.strategy: SerializationStrategy = strategy
        self.shot_idx = 0

    def get_config(self) -> WritingConfig:
        return self.config

    def set_strategy(self, strategy: SerializationStrategy):
        self.strategy = strategy

    def set_shot_index(self, idx: int) -> None:
        self.shot_idx = idx

    def get_image_write_path(self) -> str:
        """Get full path where image will be saved"""
        filename = self._get_base_filename()
        subdir = self.strategy.get_subdir("image")
        return join(self.config.save_path, subdir, filename)

    def get_image_folder(self) -> str:
        """Get folder where images are stored"""
        subdir = self.strategy.get_subdir("image")
        return join(self.config.save_path, subdir)

    def write_label(self, files: Collection[Tuple[str, str]]) -> None:
        """Format and write all label files for current shot"""
        if not self.strategy:
            return

        base_filename = self._get_base_filename()

        for (extension, content) in files:
            filename = f"{base_filename}{extension}"
            subdir = self.strategy.get_subdir(extension)
            path = join(self.config.save_path, subdir, filename)

            makedirs(dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)

    def _get_base_filename(self) -> str:
        """Build base filename from prefix and shot index"""
        return f"{self.config.prefix}_{self.shot_idx}"


    def compute_starting_index(self):
        prefix = self.config.prefix
        if self.config.from_last:
            # We have to inspect the data folder, if there are already fils with the same root and
            # some indexes are already present, start counting from the last
            return self._analyze_folder_last_index(self.get_image_folder(), prefix)
        return 0

    @staticmethod
    def _analyze_folder_last_index(path_root: Union[str, Path], prefix) -> int:
        # If the path does not exist yet, the index is simply 0.
        try:
            entries = listdir(path_root)
        except FileNotFoundError:
            return 0
        files = [f for f in entries if isfile(join(path_root, f))]

        # Find all files matching "prefix_index" pattern
        pattern = re.compile(rf"{re.escape(prefix)}_(\d+)")
        indices = []

        for file in files:
            match = pattern.match(file)
            if match:
                indices.append(int(match.group(1)))

        # Get the last index, or -1 (which becomes 0 when i add +1) if no matches
        last_index = max(indices) if indices else -1
        next_index = last_index + 1
        return next_index

