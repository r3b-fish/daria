import pytest

from ..test_zpipeline_base import TestPipelineBase, get_schema_id, get_expected_output
from ...conftest import get_output


class TestInflux(TestPipelineBase):
    __test__ = True

    params = {
        'test_start': [
            {'name': 'test_basic'},
            {'name': 'test_basic_offset'},
            {'name': 'test_influx_file_short'},
            {'name': 'test_influx_file_full'},
            {'name': 'test_influx_file_transform'},
            {'name': 'test_influx_schema_query'},
            {'name': 'test_influx2'},
            {'name': 'test_influx2_file_full'},
            {'name': 'test_influx2_query'},
            {'name': 'influx2_influxql_pipeline'},
            {'name': 'test_influx_adv'},
            {'name': 'test_influx_schema_tag'},
            {'name': 'test_influx_tag'},
            {'name': 'test_influx2_tag'},
            {'name': 'test_influx2_query_join'},
        ],
        'test_force_stop': [
            {'name': 'test_basic'},
            {'name': 'test_basic_offset'},
            {'name': 'test_influx_file_short'},
            {'name': 'test_influx_file_full'},
            {'name': 'test_influx_file_transform'},
            {'name': 'test_influx_schema_query'},
            {'name': 'test_influx2', 'check_output_file_name': 'test_influx2_influx2.json'},
            {'name': 'test_influx2_file_full'},
            {'name': 'test_influx2_query'},
            {'name': 'influx2_influxql_pipeline'},
            {'name': 'test_influx_adv'},
            {'name': 'test_influx_schema_tag'},
            {'name': 'test_influx_tag'},
            {'name': 'test_influx2_tag'},
            {'name': 'test_influx2_query_join'},
        ],
        'test_reset': [{'name': 'test_basic'}],
        'test_output': [
            {'name': 'test_influx_file_short', 'output': 'influx.json', 'pipeline_type': 'influx'},
            {'name': 'test_influx_file_full', 'output': 'influx_file_full.json', 'pipeline_type': 'influx'},
            {'name': 'test_influx_adv', 'output': 'influx_adv.json', 'pipeline_type': 'influx'},
            {'name': 'test_influx_file_transform', 'output': 'influx_file_transform.json', 'pipeline_type': 'influx'},
            {'name': 'test_influx_tag', 'output': 'influx_tag.json', 'pipeline_type': 'influx'},
        ],
        'test_output_schema': [
            {'name': 'test_basic', 'output': 'influx_schema.json', 'pipeline_type': 'influx'},
            {'name': 'test_influx_schema_query', 'output': 'influx_schema_query.json', 'pipeline_type': 'influx'},
            {'name': 'influx2_influxql_pipeline', 'output': 'influx2_influxql_schema.json', 'pipeline_type': 'influx'},
            {'name': 'test_basic_offset', 'output': 'influx_offset_schema.json', 'pipeline_type': 'influx'},
            {'name': 'test_influx2', 'output': 'influx2_schema.json', 'pipeline_type': 'influx2'},
            {'name': 'test_influx2_file_full', 'output': 'influx2_file_schema.json', 'pipeline_type': 'influx2'},
            {'name': 'test_influx2_query', 'output': 'influx2_query.json', 'pipeline_type': 'influx2'},
            {'name': 'test_influx_schema_tag', 'output': 'influx_schema_tag.json', 'pipeline_type': 'influx'},
            {'name': 'test_influx2_tag', 'output': 'influx2_tag.json', 'pipeline_type': 'influx2'},
            {'name': 'test_influx2_query_join', 'output': 'influx2_query_join.json', 'pipeline_type': 'influx2'},
        ],
        'test_delete_pipeline': [
            {'name': 'test_basic'},
            {'name': 'test_basic_offset'},
            {'name': 'test_influx_file_short'},
            {'name': 'test_influx_file_full'},
            {'name': 'test_influx_file_transform'},
            {'name': 'test_influx_schema_query'},
            {'name': 'test_influx2'},
            {'name': 'test_influx2_file_full'},
            {'name': 'test_influx2_query'},
            {'name': 'influx2_influxql_pipeline'},
            {'name': 'test_influx_adv'},
            {'name': 'test_influx_schema_tag'},
            {'name': 'test_influx_tag'},
            {'name': 'test_influx2_tag'},
            {'name': 'test_influx2_query_join'},
        ],
        'test_source_delete': [
            {'name': 'test_influx'},
            {'name': 'test_influx_offset'},
            {'name': 'test_influx_1'},
            {'name': 'test_influx2'},
            {'name': 'test_influx2_file'},
            {'name': 'influx2_influxql_source'},
        ],
    }

    def test_info(self, cli_runner, name=None):
        pytest.skip()

    def test_stop(self, cli_runner, name=None, check_output_file_name=None):
        pytest.skip()

    def test_start(self, cli_runner, name, sleep):
        super().test_start(cli_runner, name, sleep)

    def test_output(self, name, pipeline_type, output):
        def compare_output():
            expected_output = get_expected_output(name, output, pipeline_type)
            actual_output = get_output(f'{name}_{pipeline_type}.json')
            return actual_output == expected_output
        self._wait(compare_output)
        assert compare_output()

    def test_output_schema(self, name, pipeline_type, output):
        super().test_output_schema(name, pipeline_type, output)

    def test_force_stop(self, cli_runner, name, check_output_file_name):
        super().test_force_stop(cli_runner, name, check_output_file_name)

    def test_watermark(self):
        initial_offset = 1552222380
        interval = 1200000
        schema_id = get_schema_id('test_basic')
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': initial_offset + interval, 'schemaId': schema_id}
        initial_offset = 1552999980
        schema_id = get_schema_id('test_basic_offset')
        assert get_output(f'{schema_id}_watermark.json') == {'watermark': initial_offset + interval, 'schemaId': schema_id}
