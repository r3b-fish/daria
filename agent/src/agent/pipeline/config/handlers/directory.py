from agent.pipeline.config import stages
from agent.pipeline.config.handlers.base import SchemaConfigHandler, TestConfigHandler, ConfigHandler


class DirectoryConfigHandler(SchemaConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
        'JythonEvaluator_01': stages.jython.ConvertToMetrics30,
        'ExpressionEvaluator_02': stages.expression_evaluator.AddProperties30,
        'ExpressionEvaluator_03': stages.expression_evaluator.Filtering,
        'FieldTypeConverter_01': stages.field_type_converter.FieldTypeConverter,
        'destination': stages.destination.Destination,
        'JythonEvaluator_02': stages.jython.CreateWatermark,
        'destination_watermark': stages.destination.WatermarkDestination,
        'destination_watermark_with_metrics': stages.destination.WatermarkWithMetricsDestination,
    }


class TestDirectoryConfigHandler(TestConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
    }


class DirectoryEventsConfigHandler(ConfigHandler):
    stages_to_override = {
        'source': stages.source.Source,
        'JythonEvaluator_01': stages.jython.CreateEvents,
        'destination': stages.destination.AnodotEventsDestination,
    }

    def _check_pipeline(self):
        pass
