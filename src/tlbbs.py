import os
import requests
import re
from datetime import datetime
import logging

# 设置日志级别和输出格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# 将内容写入文件
def append_to_file(filename, content):
    with open(filename, 'a') as file:
        file.write(content)


# 搜索文件中是否存在搜索文本
def search_multiline_text(filename, search_text):
    # 文件不存在则先创建文件
    if not os.path.isfile(filename):
        with open(filename, 'w') as file:
            file.write('')
        print(f'创建文件 {filename}')

    with open(filename, 'r') as file:
        lines = file.readlines()

    search_lines = search_text.splitlines()
    num_lines = len(search_lines)
    num_file_lines = len(lines)

    for i in range(num_file_lines - num_lines + 1):
        if all(lines[i + j].strip() == search_lines[j].strip() for j in range(num_lines)):
            return True

    return False


# 写出日志文件
filename = 'log.txt'
# 机器人的 token
TOKEN = '2122878220:AAHVc1j3r3bfIPfb9Hmqtw3OZNFVUcbTMaw'
# TOKEN = '1773760234:AAHGJG-6v9LOd1ah_O5ou7_lHmK5SWvBlhw'
# 聊天的 ID
CHAT_ID = '991050819'

# 发送请求等url
url = 'http://bbs.tl.changyou.com/forum.php?mod=forumdisplay&fid=504'
# 添加协议头，否则网站请求403
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
}

# 发送get请求
response = requests.get(url, headers=headers)
# 正则匹配
# pattern = re.compile(r'>预览</a>.*?<a href=".*?tid=(.*?)&amp;extra=page%3D1".*?onclick=.*?class="s xst">(.*?)</a>.*?<em><span.*?>(.*?)</span></em>',re.DOTALL)

pattern = re.compile(
    r'>预览[\s\S]*?<a href=".*?tid=(.*?)&amp;extra=page%3D1".*?onclick=.*?class="s xst">(.*?)</a>.*?<em><span[\s\S]*?>(.*?)</span></em>',
    re.DOTALL)

# 返回匹配结果
matches = pattern.findall(response.text)

# 遍历匹配结果数组
# 定义更新标识符flag
flag = 0
for match in matches:
    # print(match)
    # match数组共3个值，第一个是tid，第二个是标题，第三个是时间
    # 解析时间字符串，转换为datetime对象
    time_obj = datetime.strptime(match[2], '%Y-%m-%d %H:%M')
    # 获取当前时间，提取年月日
    now = datetime.now()
    now_year, now_month, now_day = now.year, now.month, now.day
    # 首先对内测区关键字进行判断
    if match[1].find('龙腾天下') != -1 or match[1].find('内测') != -1 or match[1].find('龙门') != -1:
        # 比较时间判断是否今天更新的公告
        # print(match)
        if time_obj.year == now_year and time_obj.month == now_month and time_obj.day == now_day:
            # 指定时间进行测试
            # if time_obj.year == 2023 and time_obj.month == 5 and time_obj.day == 22:
            # 根据tid组合新的url，match[0]即为tid
            url = 'http://bbs.tl.changyou.com/forum.php?mod=viewthread&tid={}&extra=page%3D1'.format(match[0])
            response = requests.get(url, headers=headers)
            # print(response.text)

            # 首次匹配出更新内容
            text_pattern = re.compile(
                r'<span class="atips_close" onclick="this.parentNode.style.display=\'none\'">x</span>(.*?)</td></tr></table>',
                re.DOTALL)
            result = text_pattern.findall(response.text)
            # print(response.text)
            # print(result)

            # 将html源码只保留字符串，数字，下划线等基本字符。
            new_pattern = re.compile(r'[0-9\u4e00-\u9fa5\s—\-：:.《》!，。,、]+')
            # 将result数组连接成字符串：''.join(result)
            new_result = new_pattern.findall(''.join(result))
            # new_result = list(filter(lambda x: x != ' ', new_result))
            # 组合成字符串
            new_result = ''.join(new_result)
            print(match[1] + '\r\n' + new_result)
            # 更新标识符赋值
            flag = 1

            # TG消息内容
            MESSAGE = match[1] + new_result + '------------------------------------------' + '\n'

            # 搜索多行文本
            search_text = MESSAGE
            result = search_multiline_text(filename, search_text)
            if result:
                print('该公告已推送通知')
                logging.info('该公告已推送通知')
            else:

                # 设置TG代理
                # proxies = {"http": "http://127.0.0.1:6152", "https": "http://127.0.0.1:6152", }
                # 发送5次
                for i in range(5):
                    # 推送TG消息
                    r = requests.post(f'https://api.telegram.org/bot{TOKEN}/sendMessage',
                                      json={"chat_id": CHAT_ID, "text": MESSAGE}, proxies=proxies)

                    if r.status_code == 200:
                        print("消息发送成功！")
                        logging.info("消息发送成功！")

                        # 将公告内容写入文件
                        append_to_file(filename, MESSAGE)
                        break

                    else:
                        print(f"消息发送失败，状态码：{r.status_code}")
                        logging.warning(f"消息发送失败，状态码：{r.status_code}")

if flag == 0:
    print("今天没有更新！")
    logging.info('今天没有更新公告...')
