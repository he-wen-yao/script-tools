import redis
import feishu_util
import log_util

try:
    pool = redis.ConnectionPool(
        host='xxxxxxxxxxxxxxx', port=6379, decode_responses=True)
    redisDB = redis.Redis(connection_pool=pool)
    # 在创建连接后执行一个查询操作，查看连接否好用
    redisDB.client_list()
except Exception as e:
    log_util.logger.info("Redis 连接异常 ", str(e))
    feishu_util.send_warning_message("紧急预警 - Redis 连接异常", str(e))
    exit()


def setKeyExpire(key, value, expire=60 * 5):
    """
    向 redis 里存放值为 value 的 key ，以及设置 key 的过期时间
    :param key: key 的名称
    :param value: key 值
    :param expire: key 的过期时间，默认为 5 分钟
    :return:
    """
    return redisDB.setex(key, expire, value)


def getKey(key):
    return redisDB.get(key)
