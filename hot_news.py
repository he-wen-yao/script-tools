"""
爬取微博平台热榜
"""

import requests
import json
import time
import io
import sys
from bs4 import BeautifulSoup

# 改变标准输出的默认编码
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

def send_message(message_title, message_list):
    web_hook = "https://open.feishu.cn/open-apis/bot/xxxxxxxxxxxxxxxxxxx"
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
    # headers中添加上content-type这个参数，指定为json格式
    headers = {'Content-Type': 'application/json'}
    res = requests.post(url=web_hook, headers=headers, data=json.dumps(data))


def weibo_hot_brand():
  # 微博热榜接口
    weibo_hot_brand_url = "https://weibo.com/ajax/statuses/hot_band"
    res = requests.get(weibo_hot_brand_url)
    res = res.json()

    # 爬取成功
    if res['http_code'] == 200:
        data = res['data']
        message_list = data['band_list']
        message_list = [[{
            "tag": "a",
            "text": f"【{item.get('category', '无分类')}】{item['word']}",
            "href": f"https://s.weibo.com/weibo?q=%23{ item['word'] }%23"
        }] for item in message_list]
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    send_message(f"{now} - 微博热搜", message_list)


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
        return  [{
            "tag": "a",
            "text": f"【百度热搜】{text}",
            "href": herf
        }]

    hot_list = [deal(item) for item in hot_list]
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    send_message(f"{now} - 百度热搜", hot_list)


if __name__ == "__main__":
    weibo_hot_brand()
    baidu_hot_brand()
