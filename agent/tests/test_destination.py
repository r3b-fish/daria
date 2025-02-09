import pytest

from agent import cli
from agent import destination


@pytest.fixture(autouse=True)
def host_id(monkeypatch):
    def constant_host_id(length=10):
        return 'ABCDEF'
    monkeypatch.setattr(destination.HttpDestination, 'generate_host_id', constant_host_id)


def test_destination(cli_runner):
    result = cli_runner.invoke(cli.destination, args=['--url=http://wrong-url'], catch_exceptions=False,
                               input='y\nhttp://squid:3128\n\n\n\nhttp://dummy_destination\ncorrect_token\ncorrect_key\n')
    assert result.exit_code == 0
    assert destination.repository.exists()


def test_edit_destination(cli_runner):
    prev_dest_host_id = destination.repository.get().host_id
    result = cli_runner.invoke(cli.destination, catch_exceptions=False,
                               input='y\nhttp://squid:3128\n\n\n\n\ncorrect_token\n')
    print(result.output)
    curr_dest = destination.repository.get()
    assert result.exit_code == 0
    assert curr_dest.host_id == prev_dest_host_id


def test_update(cli_runner):
    result = cli_runner.invoke(cli.pipeline.update, catch_exceptions=False)
    assert result.exit_code == 0
