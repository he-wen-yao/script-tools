"""
爬取微博平台热榜
"""
import requests
import json
import time
import io
import sys
import redis
from bs4 import BeautifulSoup

# headers中添加上content-type这个参数，指定为json格式
headers = {'Content-Type': 'application/json'}
web_hook = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxxxxxxxxxxxx"


def send_message(message_title, message_list):
    if len(message_list) == 0:
        return
    data = {
        "email": "he.wenyao@qq.com",
        "msg_type": "post",
        "content": {
            "post": {
                "zh_cn": {
                    "title": message_title,
                    "content": message_list
                }
            }
        }
    }
    res = requests.post(url=web_hook, headers=headers, data=json.dumps(data))


def send_warning_message(title, warning_message):
    """
    发送报警消息
    title : 警告标题
    """
    data = {
        "msg_type": "interactive",
        "card": {
            "config": {
                "wide_screen_mode": True,
                "enable_forward": True
            },
            "header": {
                "template": "red",
                "title": {"content": title, "tag": "plain_text"}
            },
            "i18n_elements": {
                "zh_cn": [{
                    "tag": "div",
                    "text": {"content": warning_message, "tag": "lark_md"}
                }]
            }
        }
    }
    res = requests.post(url=web_hook, headers=headers, data=json.dumps(data))


try:
    pool = redis.ConnectionPool(
        host='xxxxxxxxxxxxxxxxx', port=6379, decode_responses=True)
    redisDB = redis.Redis(connection_pool=pool)
    # 在创建连接后执行一个查询操作
    redisDB.client_list()
except Exception as e:
    send_warning_message("紧急预警 - Redis 连接异常", str(e))
    exit()


def setKey(title, value, expire=60 * 60 * 24):
    return redisDB.setex(title, expire, value)


def getKey(title):
    return redisDB.get(title)


# 改变标准输出的默认编码
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


def weibo_hot_brand():
  # 微博热榜接口
    weibo_hot_brand_url = "https://weibo.com/ajax/statuses/hot_band"
    res = requests.get(weibo_hot_brand_url)
    res = res.json()

    # 爬取成功
    if res['http_code'] == 200:
        data = res['data']
        message_list = data['band_list']
        temp_list = []
        for item in message_list:
            key = f"weibo_{item['word']}"
            if not getKey(key):
                setKey(key, 1)
                temp_list.append([{
                    "tag": "a",
                    "text": f"【{item.get('category', '无分类')}】{item['word']}",
                    "href": f"https://s.weibo.com/weibo?q=%23{ item['word'] }%23"
                }])
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    send_message(f"{now} - 微博热搜", temp_list)


def baidu_hot_brand():
    head = {
        "User-Agent": '''Mozilla/5.0 (Windows NT 10.0; Win64; x64)
         AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.55'''
    }
    # 用户代理 告诉服务器我只是一个普普通通的浏览器
    requset = requests.get(
        "https://top.baidu.com/board?tab=realtime")
    # 将返回的文本转为 BeautifulSoup
    soup = BeautifulSoup(requset.text, "html.parser")
    hot_list = soup.select('div[class^="category-wrap"]')

    def deal(item):
        a = item.find("a")
        herf = a.get("href")
        div = item.select(".c-single-text-ellipsis")[0]
        text = div.text
        key = f"baidu_{text}"
        if not getKey(key):
            setKey(key, 1)
            return [{
                "tag": "a",
                "text": f"【百度热搜】{text}",
                "href": herf
            }]
        return None
    temp_list = []
    for item in hot_list:
        temp_item = deal(item)
        if temp_item:
            temp_list.append(temp_item)
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    send_message(f"{now} - 百度热搜", temp_list)


def zhihu_brand():
    request_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    zhihu_brand_url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true&reverse_order=0"
    res = requests.get(url=zhihu_brand_url,
                       headers=request_headers, verify=False)
    res = res.json()
    hot_brand_list = res['data']
    push_message_list = []
    for item in hot_brand_list:
        temp_item = item['target']
        title = temp_item['title']
        curr_value = temp_item['answer_count'] + temp_item['follower_count']
        key = f"zhihu_{title}"
        value = getKey(key)
        old_value = 0 if not value else int(value)
        if not old_value or curr_value > old_value:
            setKey(key, curr_value)
            push_message_list.append([{
                "tag": "a",
                "text": f"【知乎热搜】{title}",
                "href": temp_item['url']
            }])
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    send_message(f"{now} - 知乎热搜", push_message_list)


if __name__ == "__main__":
    weibo_hot_brand()
    baidu_hot_brand()
    zhihu_brand()
