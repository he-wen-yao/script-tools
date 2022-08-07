"""
爬取微博平台热榜
"""
import requests
import time
import redis_util
import feishu_util
from urllib import parse
from bs4 import BeautifulSoup


# 改变标准输出的默认编码
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


def article_list_by_uid(uid, page):
    """
    获取指定微博用户的文章
    uid : 用户ID
    page: 第几页文章
    feature: 10 代表获取文章
    """
    user_article_url = f"https://weibo.com/ajax/statuses/mymblog"
    headers = {
        "cookie": "SINAGLOBAL=7184263238970.686.1644755393941; UOR=,,link.zhihu.com; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWPqpBgMBpcyyhnCb9vcCeB5JpX5KMhUgL.FoqXS0-cSKzNSoM2dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMcShMfSo-ES0qN; ULV=1659712250649:32:5:6:1861997161683.917.1659712250477:1659617022959; PC_TOKEN=d194dd7b4e; ALF=1691298818; SSOLoginState=1659762818; SCF=AgX31d3T5E9dQTjT9p2ak3DpeEcJT3EUfzMOL0ZwSmcHFzDqOLcuoTpv-UdSevY__qMUSM7joapSHyRV3mL9G1s.; SUB=_2A25P6YjSDeRhGeBK7FcX9SzLzTuIHXVsnv0arDV8PUNbmtAKLWjTkW9NR5gbmQtZNKNx5kZrxBd7wazTinHFMtAV; XSRF-TOKEN=hKXBYdf63pvlBmvXdsSO1yJO; WBPSESS=KoUoLReqegcHLJn5iYh1z31dAXII0F6--r4GjD3XEesldpZ3ilZcI4ECQIRcM5UzGRCZ3d6nbmDSZbKB97f3o_2HZQQIhWtqV-NT5qLvHqwGaTs7BeBfLnl7CeURmDfW7Rjg5algSTaF6_FQ0LptGQ==",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
    }
    params = {"uid": uid, "page": page, "feature": 10}
    res = requests.get(url=user_article_url, headers=headers, params=params)
    res = res.json()
    data = res['data']['list']
    push_message_list = []
    for item in data:
        for item_ in item['url_struct']:
            key = f"baidu_article_{item_['url_title']}"
            if not redis_util.getKey(key):
                redis_util.setKeyExpire(key, 1)
                push_message_list.append([{
                    "tag": "a",
                    "text": f"【文章】{item_['url_title']}",
                    "href": f"{item_['short_url']}"
                }])
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    feishu_util.send_message(f"{now} - 人民日报", push_message_list)


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
            break
            key = f"weibo_{item['word']}"
            if not redis_util.getKey(key):
                redis_util.setKeyExpire(key, 1)
                # 将话题进行编码，在飞书手机端为编码不能访问
                keyword = parse.quote(f"#{item['word']}#")
                temp_list.append([{
                    "tag": "a",
                    "text": f"【{item.get('category', '无分类')}】{item['word']}",
                    "href": f"https://s.weibo.com/weibo?q={keyword}"
                }])
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    feishu_util.send_message(f"{now} - 微博热搜", temp_list)


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
        href = a.get("href")
        div = item.select(".c-single-text-ellipsis")[0]
        text = div.text
        key = f"baidu_{text}"
        if not redis_util.getKey(key):
            redis_util.setKeyExpire(key, 1)
            return [{
                "tag": "a",
                "text": f"【百度热搜】{text}",
                "href": href
            }]
        return None
    temp_list = []
    for item in hot_list:
        temp_item = deal(item)
        if temp_item:
            temp_list.append(temp_item)
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    feishu_util.send_message(f"{now} - 百度热搜", temp_list)


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
        # 当前热点的回答数量
        answer_count = temp_item['answer_count']
        key = f"zhihu_{title}"
        # 取出上一次该热点的回答数
        value = redis_util.getKey(key)
        old_answer_count = 0 if not value else int(value)
        # 如果当前热点没有存过 redis 或者 回答数量比上次多 50 个，则就更新回答数以及推送热点
        if not old_answer_count or (answer_count - old_answer_count) >= 50:
            # 设置新的过期时间
            redis_util.setKeyExpire(key, answer_count)
            # 放进推送列表
            push_message_list.append([{
                "tag": "a",
                "text": f"【知乎热搜】{title}",
                "href": f"https://www.zhihu.com/question/{temp_item['id']}"
            }])
    now = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime())
    feishu_util.send_message(f"{now} - 知乎热搜", push_message_list)


if __name__ == "__main__":
    weibo_hot_brand()
    baidu_hot_brand()
    zhihu_brand()
    article_list_by_uid(2803301701, 1)
