import requests
from lxml import etree
import re
import html
import json
from selenium import webdriver
import time
import os

def url():
    url = 'https://edu.tipdm.org/classroom/311/courses'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.89 Safari/537.36'}
    res = requests.get(url,headers=headers)
    selectors = etree.HTML(res.text)
    for selector in selectors:
        href_list = selector.xpath('//*/div[@class="media"]/a/@href')                    # 获取目标js链接所需的字符串
        hrefs = [i for i in href_list]                                                   # 放入列表中方便操作

    # print(hrefs)
    lists = []

    for href in hrefs:
        href = 'https://edu.tipdm.org' + href + '/task/list/render/default'              # 拼接目标
        lists.append(href)

    info = []

    for list in lists[0:-3]:
        res_href = requests.get(list, headers=headers)
        htmls = re.findall('<div class="hidden js-hidden-cached-data">[\s]+(.*?)[\s]+</div>', res_href.text)[0]  # 翻找数据存储网址并使用正则解析
        result = html.unescape(htmls.encode('utf-8').decode('unicode-escape'))                                   # 整理转义字符并将unicode编码转为utf-8
        json_text = json.loads(result)                                                                           # json解析
        if list.split('/')[-5]=='2885':
            href_id = [i['taskId'] for i in json_text if i['taskId'].startswith('7')]                            # 提取json字符串中的目标id并筛选
        else:
            href_id = [i['taskId'] for i in json_text if i['taskId'].startswith('6')]
        info.append(href_id[0:-1])
    print(info[0])
    x = 0

    try:
        while True:
            for i in info[x]:                                                                                    # 此处将一维列表与二维列表嵌套循环并拼接为视频所在地址
                driver = webdriver.Chrome()
                driver.get('https://edu.tipdm.org' + hrefs[x] + '/task/' + i +'/show')                           # 进入目标视频播放地址

                driver.find_element_by_name("_username").send_keys("账号")                                # 输入账号
                time.sleep(2)
                driver.find_element_by_id("login_password").send_keys("密码")                                # 输入密码
                time.sleep(1)
                driver.find_element_by_xpath("//*[@id='login-form']/div[4]/button").click()                      # 点击登录
                HTML = etree.HTML(driver.page_source)
                time.sleep(1.5)
                title = HTML.xpath("//*[@id='dashboard-content']/div[1]/text()")                                 # 获取视频标题
                if title[1].strip().split("：")[1] =='进入实训平台':
                    pass
                else:
                    driver.get('https://edu.tipdm.org' + hrefs[x] + '/task/' + i +'/activity_show')
                    innerHTML = driver.execute_script("return document.body.innerHTML")                          # 获取网页js内容
                    res = re.findall("(https:.*?.m3u8)", innerHTML)[0]                                           # 获取m3u8文件地址
                    with open('数据.txt', 'a') as f:
                        f.write(title[1].strip().split("：")[1] + ':' + res + '\n')                              # 保存为文本(此处已经获取所有链接，但由于其需要苹果浏览器请求头伪装下载，直接调用ffmpeg不生效)
                time.sleep(20)
                driver.close()
            x += 1
            if x >13:
                break
    except IndexError:
        pass


if __name__ == '__main__':
    url()
