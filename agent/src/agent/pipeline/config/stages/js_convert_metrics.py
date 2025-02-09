from .base import JSProcessor
from typing import Optional


class JSConvertMetrics(JSProcessor):
    def get_js_vars(self):
        return f"""
state['TIMESTAMP_COLUMN'] = '{self.pipeline.timestamp_path}';
state['DIMENSIONS'] = {self.pipeline.dimension_paths};
state['DIMENSIONS_NAMES'] = {self.pipeline.dimension_names};
state['VALUES_COLUMNS'] = {self.pipeline.value_paths};
state['DYNAMIC_TAGS'] = {self._get_tags_config()};
// it's used in kafka js metric 2.0
state['MEASUREMENT_NAMES'] = {self.pipeline.measurement_names_paths};
state['TARGET_TYPES'] = {self.pipeline.target_types_paths};
state['COUNT_RECORDS'] = {int(self.pipeline.count_records)};
state['COUNT_RECORDS_MEASUREMENT_NAME'] = '{self.pipeline.count_records_measurement_name}';
state['STATIC_WHAT'] = {int(self.pipeline.static_what)};
state['VALUES_ARRAY_PATH'] = '{self.pipeline.values_array_path}';
state['VALUES_ARRAY_FILTER'] = {self.pipeline.values_array_filter_metrics};
state['metrics'] = {{}}
    """

    def get_config(self) -> dict:
        return {
            'initScript': self.get_js_vars(),
            'stageRequiredFields': self._required_fields(),
        }

    def _required_fields(self) -> list:
        return [f'/{f}' for f in [*self.pipeline.required_dimension_paths]]

    def _get_tags_config(self) -> dict:
        return {name: value['value_path'] for name, value in self.pipeline.tag_configurations.items()}


class JSConvertMetrics30(JSConvertMetrics):
    JS_SCRIPT_NAME = 'protocol_3.js'

    def get_js_vars(self):
        return f"""
state['TIMESTAMP_COLUMN'] = '{self.pipeline.timestamp_path}';
state['DIMENSIONS'] = {self.pipeline.dimension_paths_with_names};
state['MEASUREMENTS'] = {self.pipeline.value_paths_with_names};
state['COUNT_RECORDS'] = {int(self.pipeline.count_records)};
state['COUNT_RECORDS_MEASUREMENT_NAME'] = '{self.pipeline.count_records_measurement_name}';
state['INTERVAL'] = {self._get_interval()};
state['HEADER_ATTRIBUTES'] = {self.pipeline.header_attributes};
state['SEND_WATERMARK_IF_NO_DATA'] = '{str(bool(self.pipeline.dvp_config))}';
state['DYNAMIC_TAGS'] = {self._get_tags_config()};
        """

    def get_config(self) -> dict:
        return {
            'initScript': self.get_js_vars(),
            'script': self._get_script(),
            'stageRequiredFields': self._required_fields()
        }

    def _get_interval(self) -> Optional[int]:
        return self.pipeline.interval if self.pipeline.interval is not None else 'null'


class SageJSConvertMetrics30(JSConvertMetrics30):
    def _get_interval(self) -> Optional[int]:
        # This workaround is needed because 'interval' value in Sage's pipeline configuration set in minutes
        return self.pipeline.interval * 60 if self.pipeline.interval is not None else 'null'
