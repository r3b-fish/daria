import urllib.parse

from agent.modules import proxy
from .base import Stage, JythonProcessor


class Destination(Stage):
    def get_config(self) -> dict:
        return {
            'conf.agentOffsetUrl': urllib.parse.urljoin(
                self.pipeline.streamsets.agent_external_url, f'/pipeline-offset/{self.pipeline.name}'
            ),
            self.pipeline.destination.CONFIG_ENABLE_REQUEST_LOGGING: self.pipeline.destination.if_logs_enabled,
            **self.pipeline.destination.config,
        }


class WatermarkDestination(Stage):
    def get_config(self) -> dict:
        return {
            'conf.agentWatermarkUrl': urllib.parse.urljoin(
                self.pipeline.streamsets.agent_external_url, f'/pipelines/{self.pipeline.name}/watermark'
            ),
            **self.pipeline.destination.config,
        }


class WatermarkWithMetricsDestination(JythonProcessor):
    JYTHON_SCRIPT = 'send_watermark_and_monitoring_metrics.py'

    def _get_script_params(self) -> list[dict]:
        return [
            {
                'key': 'PROXIES',
                'value': proxy.get_config(self.pipeline.destination.proxy)
            },
            {
                'key': 'WATERMARK_URL',
                'value': urllib.parse.urljoin(
                    self.pipeline.destination.url,
                    f'/api/v1/metrics/watermark'
                    f'?token={self.pipeline.destination.token}&protocol={self.pipeline.destination.PROTOCOL_30}',
                    )
            },
            {
                'key': 'WATERMARK_DELTA_MONITORING_ENDPOINT',
                'value': urllib.parse.urljoin(
                    self.pipeline.streamsets.agent_external_url, f'/monitoring/watermark_delta/{self.pipeline.name}')
            },
            {
                'key': 'WATERMARK_SENT_MONITORING_ENDPOINT',
                'value': urllib.parse.urljoin(
                    self.pipeline.streamsets.agent_external_url, f'/monitoring/watermark_sent/{self.pipeline.name}')
            },
            {
                'key': 'WATERMARK_IN_LOCAL_TIMEZONE',
                'value': str(self.pipeline.watermark_in_local_timezone),
            },
            {
                'key': 'TIMEZONE',
                'value': str(self.pipeline.timezone),
            },
            {
                'key': 'WATERMARK_LOGS',
                'value': str(self.pipeline.watermark_logs_enabled)
            },
            {
                'key': 'VERIFY_SSL',
                'value': str(not self.pipeline.destination.use_jks_truststore)
            }
        ]


class EventsDestination(Stage):
    def get_config(self) -> dict:
        return self.pipeline.destination.config


class AnodotEventsDestination(JythonProcessor):
    JYTHON_SCRIPT = 'events_destination.py'

    def _get_script_params(self) -> list[dict]:
        return [{
            'key': 'ANODOT_URL',
            'value': self.pipeline.destination.url
        }, {
            'key': 'ACCESS_TOKEN',
            'value': self.pipeline.destination.access_key
        }, {
            'key': 'PROXIES',
            'value': proxy.get_config(self.pipeline.destination.proxy)
        }]


class HttpDestination(Stage):
    def get_config(self) -> dict:
        send_data_format = self.pipeline.config.get('send_data_format', 'DELIMITED')
        config = {
            'conf.dataFormat': send_data_format,
        }
        if send_data_format == 'DELIMITED':
            config['conf.dataGeneratorFormatConfig.csvHeader'] = 'WITH_HEADER'
        return config
