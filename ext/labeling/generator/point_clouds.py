from typing import Iterable, Any

from ext.labeling import Extractor, LabelData


class PointCloudExtractor(Extractor):

    def extract(self, visible_objects, classifier, entity_data, camera, estimate_visibility: bool = True,
                **kwargs) -> LabelData:
        pass

    def get_estimated_visibility(self) -> dict[str | Any, float]:
        pass

    def get_visible_entities(self) -> Iterable[Any]:
        pass
