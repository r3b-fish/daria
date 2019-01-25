import click
import json
import os
import re

from .logger import get_logger
from .streamsets_api_client import api_client

logger = get_logger(__name__)

# https://json-schema.org/latest/json-schema-validation.html#rfc.section.6.5.3
# https://docs.oracle.com/javase/8/docs/api/java/text/SimpleDateFormat.html
config_schema = {
    'type': 'array',
    'items': {
        'type': 'object',
        'properties': {
            'pipeline_id': {'type': 'string'},  # name of the pipeline
            'source': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'enum': ['mongo']},
                    'config': {'type': 'object', 'properties': {
                        'configBean.mongoConfig.connectionString': {'type': 'string'},
                        'configBean.mongoConfig.username': {'type': 'string'},
                        'configBean.mongoConfig.password': {'type': 'string'},
                        'configBean.mongoConfig.database': {'type': 'string'},
                        'configBean.mongoConfig.collection': {'type': 'string'},
                        'configBean.isCapped': {'type': 'boolean'},
                        'configBean.initialOffset': {'type': 'string'},  # date
                    }},
                },
                'required': ['name', 'config']
            },
            'measurement_name': {'type': 'string'},
            'value': {
                'type': 'object',
                'properties': {
                    'type': {'type': 'string', 'enum': ['column', 'constant']},
                    'value': {'type': 'string'}
                },
                'required': ['type', 'value']
            },
            'target_type': {'type': 'string', 'enum': ['counter', 'gauge']},  # default gauge
            'timestamp': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'type': {'type': 'string', 'enum': ['string', 'datetime', 'unix', 'unix_ms']},
                    'format': {'type': 'string'}  # if string specify date format
                },
                'required': ['name', 'type'],
            },
            'dimensions': {
                'type': 'object',
                'properties': {
                    'required': {'type': 'array', 'items': {'type': 'string'}},
                    'optional': {'type': 'array', 'items': {'type': 'string'}}
                },
                'required': ['required']},
            'destination': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string', 'enum': ['http']},
                    'config': {'type': 'object', 'properties': {
                        'conf.resourceUrl': {'type': 'string'},  # anodot metric api url with token and protocol params
                    }},
                },
                'required': ['name', 'config']
            },
        },
        'required': ['pipeline_id', 'source', 'measurement_name', 'value',
                     'dimensions', 'timestamp', 'destination']},
}


def get_previous_pipeline_config(label, stage=0):
    recent_pipeline_config = {}
    pipelines_with_source = api_client.get_pipelines(order_by='CREATED', order='DESC',
                                                     label=label)
    if len(pipelines_with_source) > 0:
        recent_pipeline = api_client.get_pipeline(pipelines_with_source[0]['pipelineId'])
        for conf in recent_pipeline['stages'][stage]['configuration']:
            recent_pipeline_config[conf['name']] = conf['value']
    return recent_pipeline_config


class PipelineConfigHandler:
    """
    Overrides base config file
    """
    PIPELINES_BASE_CONFIGS_PATH = 'pipelines/{source_name}_{destination_name}.json'

    def __init__(self, client_config):
        self.client_config = client_config

        base_path = self.PIPELINES_BASE_CONFIGS_PATH.format(**{
            'source_name': client_config['source']['name'],
            'destination_name': client_config['destination']['name']
        })
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), base_path), 'r') as f:
            data = json.load(f)
            self.config = data['pipelineConfig']
            self.rules = data['pipelineRules']

    def update_source_configs(self):
        for conf in self.config['stages'][0]['configuration']:
            if conf['name'] in self.client_config['source']['config']:
                conf['value'] = self.client_config['source']['config'][conf['name']]

    def update_properties(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue

            conf['value'][1]['expression'] = self.client_config['measurement_name']

            if 'target_type' in self.client_config:
                conf['value'][2]['expression'] = self.client_config['target_type']

            if self.client_config['value']['type'] == 'column':
                expression = f"record:value('/{self.client_config['value']['value']}')"
                conf['value'][3]['expression'] = '${' + expression + '}'
            else:
                conf['value'][3]['expression'] = self.client_config['value']['value']

            return

    def get_rename_mapping(self):
        rename_mapping = []

        if self.client_config['timestamp']['name'] != 'timestamp':
            rename_mapping.append({'fromFieldExpression': '/' + self.client_config['timestamp']['name'],
                                   'toFieldExpression': '/timestamp'})

        dimensions = self.client_config['dimensions']['required']
        if 'optional' in self.client_config['dimensions']:
            dimensions = self.client_config['dimensions']['required'] + self.client_config['dimensions']['optional']
        for dim in dimensions:
            rename_mapping.append({'fromFieldExpression': '/' + dim, 'toFieldExpression': '/properties/' + dim})
        return rename_mapping

    def rename_fields_for_anodot_protocol(self, stage):
        for conf in stage['configuration']:
            if conf['name'] == 'renameMapping':
                conf['value'] = self.get_rename_mapping()

            if conf['name'] == 'stageRequiredFields':
                conf['value'] = ['/' + d for d in self.client_config['dimensions']['required']]

    def update_destination_config(self):
        for conf in self.config['stages'][-1]['configuration']:
            if conf['name'] in self.client_config['destination']['config']:
                conf['value'] = self.client_config['destination']['config'][conf['name']]

    def convert_timestamp_to_unix(self, stage):
        for conf in stage['configuration']:
            if conf['name'] != 'expressionProcessorConfigs':
                continue

            if self.client_config['timestamp']['type'] == 'string':
                dt_format = self.client_config['timestamp']['format']
                get_timestamp_exp = f"time:extractDateFromString(record:value('/timestamp'), '{dt_format}')"
                expression = f"time:dateTimeToMilliseconds({get_timestamp_exp})/1000"
            elif self.client_config['timestamp']['type'] == 'datetime':
                expression = "time:dateTimeToMilliseconds(record:value('/timestamp'))/1000"
            elif self.client_config['timestamp']['type'] == 'unix_ms':
                expression = "record:value('/timestamp')/1000"
            else:
                expression = "record:value('/timestamp')"

            conf['value'][0]['expression'] = '${' + expression + '}'
            return

    def override_base_config(self, new_uuid, new_pipeline_title):
        self.config['uuid'] = new_uuid
        self.config['title'] = new_pipeline_title

        self.update_source_configs()

        for stage in self.config['stages']:
            if stage['instanceName'] == 'ExpressionEvaluator_01':
                self.update_properties(stage)

            if stage['instanceName'] == 'FieldRenamer_01':
                self.rename_fields_for_anodot_protocol(stage)

            if stage['instanceName'] == 'ExpressionEvaluator_02':
                self.convert_timestamp_to_unix(stage)

        self.update_destination_config()
        self.config['metadata']['labels'] = [self.client_config['source']['name'],
                                             self.client_config['destination']['name']]

        return self.config

    def override_base_rules(self, new_uuid):
        self.rules['uuid'] = new_uuid
        return self.rules
