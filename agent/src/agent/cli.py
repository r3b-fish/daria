import click

# for using arrows in cli
# import readline

from . import pipeline, source
from .pipeline.cli import pipeline_group
from .source.cli import source_group
from .destination.cli import destination
from agent.version import __version__, __build_time__, __git_sha1__


class DefaultHelp(click.Group):
    def __init__(self, *args, **kwargs):
        context_settings = kwargs.setdefault('context_settings', {})
        if 'help_option_names' not in context_settings:
            context_settings['help_option_names'] = ['-h', '--help']
        self.help_flag = context_settings['help_option_names'][0]
        super(DefaultHelp, self).__init__(*args, **kwargs)

    def parse_args(self, ctx, args):
        if not args:
            args = [self.help_flag]
        return super(DefaultHelp, self).parse_args(ctx, args)


@click.group(cls=DefaultHelp, invoke_without_command=True)
@click.option('-v', '--version', is_flag=True, default=False)
def agent(version):
    if version:
        click.echo('Daria Agent version: ' + __version__)
        click.echo('Build Time (UTC): ' + __build_time__)
        click.echo('Git commit: ' + __git_sha1__)


@click.command()
def update():
    """
    Update all pipelines configuration, recreate and restart them
    """

    for p in pipeline.get_pipelines():
        pipeline_manager = pipeline.PipelineManager(p)
        pipeline_manager.update()

        click.secho(f'Pipeline {p.id} updated', fg='green')


agent.add_command(source_group)
agent.add_command(pipeline_group)
agent.add_command(destination)
agent.add_command(update)

if __name__ == '__main__':
    agent()
