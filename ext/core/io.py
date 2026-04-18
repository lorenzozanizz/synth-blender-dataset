from .configurations import WritingConfig

from typing import Union, Literal
from pathlib import Path
from os.path import join, dirname, isdir, isfile
from os import makedirs, listdir
from enum import Enum

import re


class FolderStructure(Enum):
    """

    """
    YOLO = "yolo"
    YOLO_SPLIT = "yolo_split"       # images/train, labels/train, etc.
    COCO_FLAT = "coco_flat"         # single dir with annotations.json
    KITTI_3D = "kitti_3d"           # image_2/, label_2/, calib/


class LabelWriter:

    def __init__(self, write_config: WritingConfig):
        self.config = write_config

        self.shot_idx: int = 0

    def get_write_path(self, filename: str) -> str:

        """Map filename to actual path based on folder structure"""
        subdir = ""
        fs = self.config.folder_struct
        # Note: if folder structure is YOLO, subdir remains "
        if fs == FolderStructure.YOLO_SPLIT:
            if filename.endswith('.txt'):
                subdir = f"labels/{self.config.split}"
            else:
                subdir = f"images/{self.config.split}"
        elif fs == FolderStructure.COCO_FLAT:
            subdir = ""
        elif fs == FolderStructure.KITTI_3D:
            if "calib" in filename:
                subdir = "calib"
            elif "label" in filename:
                subdir = "label_2"
            else:
                subdir = "image_2"

        return join(self.config.save_path, subdir, filename)

    def get_image_folder(self) -> str:

        """Map filename to actual path based on folder structure"""
        subdir = ""
        fs = self.config.folder_struct
        if fs == FolderStructure.YOLO_SPLIT:
                subdir = f"images/{self.config.split}"
        elif fs == FolderStructure.COCO_FLAT:
            subdir = ""
        elif fs == FolderStructure.KITTI_3D:
                subdir = "image_2"
        return join(self.config.save_path, subdir)


    def set_shot_index(self, shot_idx):
        self.shot_idx = shot_idx

    def write_label(self, files):

        for filename, content in files.items():
            # Determine output path based on folder structure
            path = self.get_write_path(filename)
            makedirs(dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)

    def get_image_path(self) -> Union[str, Path]:
        return self.get_write_path(f"{self.config.prefix}_{self.shot_idx}{self.config.extension}")

    def compute_starting_index(self):
        prefix = self.config.prefix
        if self.config.from_last:
            # We have to inspect the data folder, if there are already fils with the same root and
            # some indexes are already present, start counting from the last
            return self._analyze_folder_last_index(self.get_image_folder(), prefix)
        return 0

    @staticmethod
    def _analyze_folder_last_index(path_root: Union[str, Path], prefix) -> int:

        files = [f for f in listdir(path_root) if isfile(join(path_root, f))]

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
