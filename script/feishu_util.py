# headers中添加上content-type这个参数，指定为json格式
import requests
import json
import log_util


headers = {'Content-Type': 'application/json'}
web_hook = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"


def send_message(message_title, message_list):
    """
    发送列表消息
    :param message_title: 消息标题
    :param message_list: 消息列表
    :return:
    """
    if len(message_list) == 0:
        return
    data = {"email": "he.wenyao@qq.com",
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": message_title,
                        "content": message_list
                    }
                }
            }}
    res = requests.post(url=web_hook, headers=headers, data=json.dumps(data))
    log_util.logger.info(f"res{res.json()}")


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
    log_util.logger.info(f"res{res.json()}")


if __name__ == '__main__':
    pass
