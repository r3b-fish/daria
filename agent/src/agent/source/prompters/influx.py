import click
from datetime import datetime
from urllib.parse import urlparse


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError as e:
        return False


class PromptInflux:

    def prompt(self, default_config, advanced=False):
        config = dict()
        config['host'] = click.prompt('InfluxDB API url', type=click.STRING, default=default_config.get('host'))
        if not is_url(config['host']):
            raise click.UsageError(f"{config['host']} is not and url")

        config['username'] = click.prompt('Username', type=click.STRING, default=default_config.get('username', ''))
        config['password'] = click.prompt('Password', type=click.STRING, default=default_config.get('password', ''))
        config['db'] = click.prompt('Database', type=click.STRING, default=default_config.get('db'))

        config['offset'] = click.prompt(
            'Initial offset (amount of days ago or specific date in format "dd/MM/yyyy HH:mm")',
            type=click.STRING,
            default=default_config.get('offset', '')).strip()
        if config['offset']:
            if config['offset'].isdigit():
                try:
                    int(config['offset'])
                except ValueError:
                    raise click.UsageError(config['offset'] + ' is not a valid integer')
            else:
                try:
                    datetime.strptime(config['offset'], '%d/%m/%Y %H:%M').timestamp()
                except ValueError as e:
                    raise click.UsageError(str(e))

        return config
