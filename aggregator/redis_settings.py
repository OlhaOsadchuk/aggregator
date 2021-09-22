import redis
from autopodbor.settings import CONSTANCE_REDIS_CONNECTION

REDIS = redis.StrictRedis(CONSTANCE_REDIS_CONNECTION['host'],
                          CONSTANCE_REDIS_CONNECTION['port'],
                          CONSTANCE_REDIS_CONNECTION['db'])
