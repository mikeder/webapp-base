from lib.Logger import Logger as LOGGER
from lib.Shared.Config import Config
from lib.Stats import Stats

SUCCESS = 2000
SUCCESS_OTP_REQUIRED = 2001
SUCCESS_LEGAL_DOC_REQUIRED = 2002
SUCCESS_OUTSIDE_GRACE_PERIOD = 2003

MAINTENANCE = 3000
SERVICE_DISABLED = 4000

# Data Exceptions (5000 - 5999)
MISSING_MAND_PARAM = 5000
INVALID_PARAM_VAL = 5001
INVALID_PATH = 5002
INVALID_UUID = 5003
INVALID_INPUT = 5004
INVALID_XML = 5005
INVALID_JSON = 5006
DATA_NOT_FOUND = 5007
INVALID_TOKEN = 5008
DATA_LIMIT_REACHED = 5009

# Upload Data exceptions
UPLOAD_INITIATED_ALREADY = 5051
UPLOAD_NO_SUCH_UPLOAD = 5052
UPLOAD_COMPLETED_ALREADY = 5053
UPLOAD_PART_MISMATCH = 5054
UPLOAD_CHECKSUM_MISMATCH = 5055
UPLOAD_PART_MISSING = 5056
UPLOAD_CHECKSUM_MISSING = 5057
UPLOAD_ONLY_ACTIVE = 5058

# HTTP Exceptions (6000 - 6999)
INVALID_URL = 6000
INVALID_REQUEST = 6001
LOBBY_ROUTER_TIMEOUT = 6002
HTTP_SERVER_ERROR = 6003
MAX_POPULATION_REACHED = 6004
MAX_POPULATION_DATA_STALE = 6005
SERVICE_RATE_EXCEEDED = 6006
USER_RATE_EXCEEDED = 6007
BLOCKED_CLIENT_IP = 6008
BLOCKED_CLIENT_AGENT = 6009
REALM_DOWN = 6010
REALM_LOCKED = 6011
BLOCKED_CLIENT_FINGERPRINT = 6012
NETWORK_CONNECT_TIMEOUT_ERROR = 6013

# DB Exceptions (7000 - 7999)
DB_CONN_ERROR = 7000
DB_OPERATIONAL_ERROR = 7001
DB_ERROR = 7002
DB_LOCK_WAIT_TIMEOUT_ERROR = 7003

# Server Exceptions (9000 - 9999)
SERVER_ERROR = 9000

# Memcache Exceptions (10000 - 10499)
MEMCACHED_INIT_ERROR = 10000
MEMCACHED_SET_ERROR = 10001
MEMCACHED_GET_ERROR = 10002

# Redis Exceptions (10500 - 10999)
REDIS_CONNECTION_ERROR = 10500
REDIS_INTERNAL_ERROR = 10501

# Google Captcha Exception
CAPTCHA_INVALID = 11000


class BaseException(Exception):
    Config.ioloop_initialize()

    def __init__(self, status_code, platform_code, error_string, response=None):
        self.status_code = status_code
        self.platform_code = platform_code
        self.message = error_string
        self.response = response
        self.status_reason = ''

        a_stats_name = "{0}.{1}.{2}".format(self.__class__.__name__, platform_code, status_code)
        Stats.collect_host_stat_total(a_stats_name)
        Stats.collect_stat_total(a_stats_name)


class DataException(BaseException):
    def __init__(self, status_code, platform_code, error_string):
        super(DataException, self).__init__(status_code, platform_code, error_string)


class HTTPException(BaseException):
    def __init__(self, status_code, platform_code, error_string):
        super(HTTPException, self).__init__(status_code, platform_code, error_string)


class UnknownHttpException(BaseException):
    def __init__(self, status_code, platform_code, error_string):
        super(UnknownHttpException, self).__init__(status_code, platform_code, error_string)


class DBException(BaseException):
    def __init__(self, status_code, platform_code, error_string, critical=False):
        super(DBException, self).__init__(status_code, platform_code, error_string)
        if critical:
            LOGGER.outage("DB", error_string)


class MemcachedException(BaseException):
    def __init__(self, status_code, platform_code, error_string, critical=False):
        super(MemcachedException, self).__init__(status_code, platform_code, error_string)
        if critical:
            LOGGER.outage("Memcached", error_string)


class RedisException(BaseException):
    def __init__(self, status_code, platform_code, error_string, critical=False):
        super(RedisException, self).__init__(status_code, platform_code, error_string)
        if critical:
            LOGGER.outage("Redis", error_string)