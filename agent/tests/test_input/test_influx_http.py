import os

from ..fixtures import cli_runner
from agent import cli
from agent.streamsets_api_client import api_client
from agent import source
from ..test_pipelines.test_zpipeline_base import pytest_generate_tests


class TestInflux:

    params = {
        'test_source_create': [{'name': 'test_influx', 'offset': '10/03/2019 12:53'},
                               {'name': 'test_influx_offset', 'offset': '19/03/2019 12:53'}],
        'test_create': [{'name': 'test_basic', 'source_': 'test_influx'},
                        {'name': 'test_basic_offset', 'source_': 'test_influx_offset'}],
    }

    def test_source_create(self, cli_runner, name, offset):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input=f"influx\n{name}\nhttp://influx:8086\nadmin\nadmin\ntest\n{offset}\n\n")
        assert result.exit_code == 0
        assert os.path.isfile(os.path.join(source.repository.SOURCE_DIRECTORY, f'{name}.json'))

    def test_create(self, cli_runner, name, source_):
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False,
                                   input=f'{source_}\n{name}\ncpu_test\n\nusage_active usage_idle\n\ncp<u zone host\n\n7000000\n\n\n')
        assert result.exit_code == 0
        assert api_client.get_pipeline(name)

    def test_create_adv(self, cli_runner):
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False,
                                   input="test_influx\ntest_influx_adv\ncpu_test\n\nusage_active usage_idle\n\ncp<u zone host\n \nkey:val key1:val1\nkey:val key1:val1\n\n7000000\nzone = 'GEO'\n\n\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline('test_influx_adv')
