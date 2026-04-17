
class GenerationPipeline:

    def __init__(self):
        pass

    def __init__(self, config: GenerationConfig, reporter):
        self.config = config
        self.reporter = reporter
        self.classifier = ClassificationEngine(context)
        self.extractor = self._create_extractor()  # Based on config.extraction_type
        self.formatter = self._create_formatter()  # Based on config.output_format
        self.writer = LabelWriter(config)

    def execute(self, visible_objects, camera, depsgraph, render_settings) -> LabelData:
        # Classify
        classifications = self.classifier.classify(visible_objects)

        label_data = self.extractor.extract(
            visible_objects=visible_objects,
            classifications=classifications,
            camera=camera,
            depsgraph=depsgraph,
            render_settings=render_settings
        )
        files = self.formatter.format(label_data)

        self.writer.write(files)
        return label_data