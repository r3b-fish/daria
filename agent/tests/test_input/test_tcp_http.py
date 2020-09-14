import traceback

from ..conftest import get_input_file_path
from agent.cli import source as source_cli, pipeline as pipeline_cli
from agent.modules.streamsets_api_client import api_client
from agent import source


class TestTCPServer:

    params = {}

    def test_source_create(self, cli_runner):
        grok_file_path = get_input_file_path('grok_patterns.txt')
        result = cli_runner.invoke(source_cli.create, catch_exceptions=False,
                                   input="splunk\ntest_tcp_log\n9999\nLOG\n" + grok_file_path + "\n%{NONNEGINT:timestamp_unix_ms} %{TIMESTAMP:timestamp_string} %{NONNEGINT:ver} %{WORD} %{WORD:Country} %{WORD:AdType} %{WORD:Exchange} %{NUMBER:Clicks}\n")
        traceback.print_exception(*result.exc_info)
        assert result.exit_code == 0
        assert source.repository.exists('test_tcp_log')

    def test_create(self, cli_runner):
        result = cli_runner.invoke(pipeline_cli.create, catch_exceptions=False,
                                   input=f"test_tcp_log\ntest_tcp_log\n\nn\nClicks:gauge\nClicks:clicks\ntimestamp_unix_ms\nunix_ms\nver Country\nExchange optional_dim\n\n")
        assert result.exit_code == 0
        assert api_client.get_pipeline('test_tcp_log')
