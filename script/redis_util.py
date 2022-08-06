import redis
import feishu_util
import log_util

try:
    pool = redis.ConnectionPool(
        host='127.0.0.1', port=6379, decode_responses=True)
    redisDB = redis.Redis(connection_pool=pool)
    # 在创建连接后执行一个查询操作，查看连接否好用
    redisDB.client_list()
except Exception as e:
    log_util.logger.info("Redis 连接异常 ", str(e))
    feishu_util.send_warning_message("紧急预警 - Redis 连接异常", str(e))
    exit()


def setKey(title, value, expire=60 * 60 * 24):
    return redisDB.setex(title, expire, value)


def getKey(title):
    return redisDB.get(title)