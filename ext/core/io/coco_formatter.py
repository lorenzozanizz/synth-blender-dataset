from datetime import datetime
from collections.abc import Collection

from ...labeling.generator.data_structure import *
from ..configurations import WritingConfig, RenderConfig
from .formatter import SerializationStrategy


class CocoFormatter(SerializationStrategy):

    def __init__(self, write_config: WritingConfig):
        super().__init__(write_config)
        self.json_intermediate = {}

    def mark_beginning(self) -> None:
        """ Initializes the coco structure, maintaining a local json which will be
        serialized at the end of the labeling session. """

        # Note: the licences section is not written. It is up to the user to
        # change it.
        self._fill_out_info()
        self._initialize_entries()

    def mark_end(self) -> None:
        pass

    def format(self, label_data: LabelData, render_config: RenderConfig) -> Collection[tuple[str, str]]:
        pass

    def get_subdir(self, ext: str) -> str:
        """

        :param ext:
        :return:
        """
        if 'json' in ext:
            return 'annotations'
        elif 'image' in ext:
            return 'images'
        return ""

    def _initialize_entries(self) -> None:
        """ Initialize the basic structure of a COCO file without storing it yet,
        keeping it in memory in an intermediate json dictionary before finally
        serializing it.
        """
        # Image files are stores into a separate section with id, name width and height
        self.json_intermediate['images'] = []
        # The same goes for annotations
        self.json_intermediate['annotations'] = []
        # The classes are instead filled out inside declare_classes()

    def _fill_out_info(self) -> None:
        """

        :return:
        """
        # Explicitly write out the information section for the coco file.
        self.json_intermediate['info'] = {
            "year": datetime.now().year,
            "version": "1.0",
            "date_created": datetime.now().isoformat(),
            # Maybe add the contributor?
        }
