from datetime import datetime
from agent import source, cli
from ..test_zpipeline_base import TestInputBase


class TestPostgreSQL(TestInputBase):
    __test__ = True
    params = {
        'test_source_create': [{'name': 'test_jdbc_postgres', 'type': 'postgres', 'conn': 'postgresql://postgres:5432/test'}],
        'test_create': [
            {'name': 'test_postgres', 'source': 'test_jdbc_postgres', 'timestamp_type': '', 'timestamp_name': 'timestamp_unix'},
            {'name': 'test_postgres_timestamp_ms', 'source': 'test_jdbc_postgres', 'timestamp_type': 'unix_ms',
             'timestamp_name': 'timestamp_unix_ms'},
            {'name': 'test_postgres_timestamp_datetime', 'source': 'test_jdbc_postgres', 'timestamp_type': 'datetime',
             'timestamp_name': 'timestamp_datetime'}],
        'test_create_advanced': [{'name': 'test_postgres_advanced', 'source': 'test_jdbc_postgres'}],
        'test_create_with_file': [{'file_name': 'jdbc/postgres_pipelines'}],
        'test_create_source_with_file': [{'file_name': 'jdbc/postgres_sources'}],
    }

    def test_source_create(self, cli_runner, name, type, conn):
        result = cli_runner.invoke(cli.source.create, catch_exceptions=False,
                                   input=f"{type}\n{name}\n{conn}\npostgres\npassword\n\n")
        assert result.exit_code == 0
        assert source.repository.exists(name)

    def test_create(self, cli_runner, name, source, timestamp_type, timestamp_name):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        result = cli_runner.invoke(cli.pipeline.create, catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}}\n\n86400\n{days_to_backfill}\n1\n{timestamp_name}\n{timestamp_type}\n\nclicks:gauge impressions:gauge\nadsize country\n\n\n\n')
        assert result.exit_code == 0

    def test_create_advanced(self, cli_runner, name, source):
        days_to_backfill = (datetime.now() - datetime(year=2017, month=12, day=10)).days + 1
        result = cli_runner.invoke(cli.pipeline.create, ['-a'], catch_exceptions=False,
                                   input=f'{source}\n{name}\nSELECT * FROM test WHERE {{TIMESTAMP_CONDITION}} AND not country is NULL\n\n86400\n{days_to_backfill}\n1\ntimestamp_unix\nunix\ny\ntest\nclicks:gauge impressions:gauge\nadsize country\nkey1:val1 key2:val2\n\n\n\n')
        assert result.exit_code == 0
