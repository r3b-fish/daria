from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy import Column, Integer, String, JSON, func
from agent import source
from agent.modules.db import Entity


class Source(Entity):
    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    config = Column(MutableDict.as_mutable(JSON))
    created_at = Column(TIMESTAMP(timezone=True), default=func.now())
    last_edited = Column(TIMESTAMP(timezone=True), default=func.now(), onupdate=func.now())

    pipelines = relationship('Pipeline', back_populates='source_')

    def __init__(self, name: str, source_type: str, config: dict):
        self._previous_config = {}
        self.config = config
        self.type = source_type
        self.name = name
        self.sample_data = None

    def config_changed(self) -> bool:
        return self.config != self._previous_config

    # todo refactor
    def __getattr__(self, attr):
        if attr == 'sample_data':
            return []
        raise AttributeError(f'type object {type(self)} has no attribute {attr}')

    def to_dict(self) -> dict:
        return {'name': self.name, 'type': self.type, 'config': self.config}

    # todo refactor children
    def set_config(self, config):
        self.config = config

    @property
    def query_timeout(self) -> int:
        return int(self.config.get('query_timeout', 300))


class ElasticSource(Source):
    CONFIG_INDEX = 'conf.index'
    CONFIG_MAPPING = 'conf.mapping'
    CONFIG_IS_INCREMENTAL = 'conf.isIncrementalMode'
    CONFIG_QUERY_INTERVAL = 'conf.queryInterval'
    CONFIG_OFFSET_FIELD = 'conf.offsetField'
    CONFIG_INITIAL_OFFSET = 'conf.initialOffset'
    CONFIG_QUERY = 'conf.query'
    CONFIG_CURSOR_TIMEOUT = 'conf.cursorTimeout'
    CONFIG_BATCH_SIZE = 'conf.maxBatchSize'
    CONFIG_HTTP_URIS = 'conf.httpUris'

    def set_config(self, config):
        super().set_config(config)
        if 'query_interval_sec' in self.config:
            self.config[ElasticSource.CONFIG_QUERY_INTERVAL] = \
                '${' + str(self.config['query_interval_sec']) + ' * SECONDS}'
        self.config[ElasticSource.CONFIG_IS_INCREMENTAL] = True


class JDBCSource(Source):
    CONFIG_CONNECTION_STRING = 'connection_string'
    CONFIG_USE_CREDENTIALS = 'hikariConfigBean.useCredentials'
    CONFIG_USERNAME = 'hikariConfigBean.username'
    CONFIG_PASSWORD = 'hikariConfigBean.password'


class MongoSource(Source):
    CONFIG_CONNECTION_STRING = 'configBean.mongoConfig.connectionString'
    CONFIG_USERNAME = 'configBean.mongoConfig.username'
    CONFIG_PASSWORD = 'configBean.mongoConfig.password'
    CONFIG_AUTH_SOURCE = 'configBean.mongoConfig.authSource'
    CONFIG_AUTH_TYPE = 'configBean.mongoConfig.authenticationType'
    CONFIG_DATABASE = 'configBean.mongoConfig.database'
    CONFIG_COLLECTION = 'configBean.mongoConfig.collection'
    CONFIG_IS_CAPPED = 'configBean.isCapped'
    CONFIG_OFFSET_TYPE = 'configBean.offsetType'
    CONFIG_INITIAL_OFFSET = 'configBean.initialOffset'
    CONFIG_OFFSET_FIELD = 'configBean.offsetField'
    CONFIG_BATCH_SIZE = 'configBean.batchSize'
    CONFIG_MAX_BATCH_WAIT_TIME = 'configBean.maxBatchWaitTime'

    OFFSET_TYPE_OBJECT_ID = 'OBJECTID'
    OFFSET_TYPE_STRING = 'STRING'
    OFFSET_TYPE_DATE = 'DATE'

    AUTH_TYPE_NONE = 'NONE'
    AUTH_TYPE_USER_PASS = 'USER_PASS'

    offset_types = [OFFSET_TYPE_OBJECT_ID, OFFSET_TYPE_STRING, OFFSET_TYPE_DATE]

    def set_config(self, config):
        super().set_config(config)
        if self.config[MongoSource.CONFIG_USERNAME] != '':
            self.config[MongoSource.CONFIG_AUTH_TYPE] = self.AUTH_TYPE_USER_PASS
        else:
            self.config[MongoSource.CONFIG_AUTH_TYPE] = self.AUTH_TYPE_NONE
            del self.config[MongoSource.CONFIG_USERNAME]


class SchemalessSource(Source):
    CONFIG_DATA_FORMAT = 'conf.dataFormat'
    CONFIG_CSV_MAPPING = 'csv_mapping'

    DATA_FORMAT_JSON = 'JSON'
    DATA_FORMAT_CSV = 'DELIMITED'
    DATA_FORMAT_AVRO = 'AVRO'
    DATA_FORMAT_LOG = 'LOG'

    CONFIG_CSV_TYPE = 'conf.dataFormatConfig.csvFileFormat'
    CONFIG_CSV_TYPE_DEFAULT = 'CSV'
    CONFIG_CSV_TYPE_CUSTOM = 'CUSTOM'
    csv_types = [CONFIG_CSV_TYPE_DEFAULT, CONFIG_CSV_TYPE_CUSTOM]

    CONFIG_CSV_HEADER_LINE = 'conf.dataFormatConfig.csvHeader'
    CONFIG_CSV_HEADER_LINE_NO_HEADER = 'NO_HEADER'
    CONFIG_CSV_HEADER_LINE_WITH_HEADER = 'WITH_HEADER'

    CONFIG_CSV_CUSTOM_DELIMITER = 'conf.dataFormatConfig.csvCustomDelimiter'

    CONFIG_AVRO_SCHEMA_SOURCE = 'conf.dataFormatConfig.avroSchemaSource'
    CONFIG_AVRO_SCHEMA = 'conf.dataFormatConfig.avroSchema'
    CONFIG_AVRO_SCHEMA_FILE = 'schema_file'
    CONFIG_AVRO_SCHEMA_REGISTRY_URLS = 'conf.dataFormatConfig.schemaRegistryUrls'
    CONFIG_AVRO_SCHEMA_LOOKUP_MODE = 'conf.dataFormatConfig.schemaLookupMode'

    CONFIG_KEY_DESERIALIZER = 'conf.keyDeserializer'
    CONFIG_VALUE_DESERIALIZER = 'conf.keyDeserializer'

    AVRO_SCHEMA_SOURCE_SOURCE = 'SOURCE'
    AVRO_SCHEMA_SOURCE_INLINE = 'INLINE'
    AVRO_SCHEMA_SOURCE_REGISTRY = 'REGISTRY'
    avro_sources = [AVRO_SCHEMA_SOURCE_SOURCE, AVRO_SCHEMA_SOURCE_INLINE, AVRO_SCHEMA_SOURCE_REGISTRY]

    AVRO_LOOKUP_SUBJECT = 'SUBJECT'
    AVRO_LOOKUP_ID = 'ID'
    AVRO_LOOKUP_AUTO = 'AUTO'
    avro_lookup_modes = [AVRO_LOOKUP_SUBJECT, AVRO_LOOKUP_ID, AVRO_LOOKUP_AUTO]

    CONFIG_AVRO_LOOKUP_ID = 'conf.dataFormatConfig.schemaId'
    CONFIG_AVRO_LOOKUP_SUBJECT = 'conf.dataFormatConfig.subject'

    CONFIG_BATCH_SIZE = 'conf.maxBatchSize'
    CONFIG_BATCH_WAIT_TIME = 'conf.batchWaitTime'

    CONFIG_GROK_PATTERN_DEFINITION = 'conf.dataFormatConfig.grokPatternDefinition'
    CONFIG_GROK_PATTERN = 'conf.dataFormatConfig.grokPattern'
    CONFIG_GROK_PATTERN_FILE = 'grok_definition_file'

    data_formats = [DATA_FORMAT_JSON, DATA_FORMAT_CSV, DATA_FORMAT_AVRO, DATA_FORMAT_LOG]

    def set_config(self, config):
        super().set_config(config)
        if self.config.get(self.CONFIG_GROK_PATTERN_FILE):
            with open(self.config[self.CONFIG_GROK_PATTERN_FILE]) as f:
                self.config[self.CONFIG_GROK_PATTERN_DEFINITION] = f.read()


class KafkaSource(SchemalessSource):
    CONFIG_BROKER_LIST = 'conf.brokerURI'
    CONFIG_CONSUMER_GROUP = 'conf.consumerGroup'
    CONFIG_TOPIC_LIST = 'conf.topicList'
    CONFIG_OFFSET_TYPE = 'conf.kafkaAutoOffsetReset'
    CONFIG_OFFSET_TIMESTAMP = 'conf.timestampToSearchOffsets'

    CONFIG_CONSUMER_PARAMS = 'conf.kafkaOptions'
    CONFIG_N_THREADS = 'conf.numberOfThreads'
    CONFIG_LIBRARY = 'library'
    CONFIG_VERSION = 'version'

    OFFSET_EARLIEST = 'EARLIEST'
    OFFSET_LATEST = 'LATEST'
    OFFSET_TIMESTAMP = 'TIMESTAMP'


class SageSource(Source):
    URL = 'url'
    TOKEN = 'token'
    SAGE_SOURCE_HEADER = 'source_header'


class APISource(Source):
    URL = 'url'
    HOSTS = 'hosts'
    AUTHENTICATION = 'authentication'
    USERNAME = 'username'
    PASSWORD = 'password'
    VERIFY_SSL = 'verify_ssl'

    @property
    def url(self) -> str:
        return self.config.get(self.URL)

    @property
    def hosts(self) -> str:
        return self.config.get(self.HOSTS)

    @property
    def verify_ssl(self) -> bool:
        return self.config.get('verify_ssl', True)

    @property
    def authentication(self) -> dict:
        return self.config.get(self.AUTHENTICATION, {})


class SNMPSource(APISource):
    READ_COMMUNITY = 'read_community'
    VERSION = 'version'

    @property
    def read_community(self) -> str:
        return self.config[self.READ_COMMUNITY]

    @property
    def version(self) -> str:
        return self.config.get(self.VERSION, 'v2c')


class ObserviumSource(Source):
    HOST = 'host'
    PORT = 'port'
    USERNAME = 'username'
    PASSWORD = 'password'
    DATABASE = 'database'

    PORTS = 'ports'
    MEMPOOLS = 'mempools'
    PROCESSORS = 'processors'
    STORAGE = 'storage'


class PromQLSource(APISource):
    pass


class PRTGSource(APISource):
    pass


class RRDSource(Source):
    RRD_DIR_PATH = 'rrd_dir_path'
    RRD_ARCHIVE_PATH = 'rrd_archive_path'
    ARCHIVE_COMPRESSION_TYPE = 'archive_compression'


class SolarWindsSource(APISource):
    pass


class ZabbixSource(APISource):
    USER = 'user'


class CactiSource(RRDSource):
    MYSQL_CONNECTION_STRING = 'mysql_connection_string'


class DirectorySource(SchemalessSource):
    pass


class TCPSource(SchemalessSource):
    pass


class TopologySource(APISource):
    pass


class InfluxSource(Source):
    pass


class Influx2Source(InfluxSource):
    pass


class SourceException(Exception):
    pass


class SourceNotExists(SourceException):
    pass


def make_typed(source_: Source) -> Source:
    source_.__class__ = source.types[source_.type]
    return source_
