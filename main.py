# -*- coding: utf-8 -*-
# Author: viotbery
# Time: 2022-08-03
from requests_html import HTMLSession
from urllib.request import urlretrieve
import os
# 已支持网站
# MOA:　中国农业农村部（http://www.moa.gov.cn/）


MOABASEURL = 'http://www.moa.gov.cn/govsearch/gov_list_ad_media_new.jsp?'
# 网站url
# 参数类型：
# Title：标题
# page：页码
# SearchClassInfoId2： 搜索类别（默认为71，政策法规类）
# SType：未知
# 返回请求链接
def MOAURL(Title, page, SearchClassInfoId2 = '71', SType = '3'):
    return MOABASEURL + 'Title=' + Title + '&page=' + page + '&SearchClassInfoId2=' + SearchClassInfoId2 + '&SType=' + SType

# 构造sessoin
def MOASession(title, page):
    try: 
        r = HTMLSession().get(MOAURL(title, page))
        # 自适应解码
        r.html.encoding = r.apparent_encoding
        result =  r.html.links
    except Exception as e:
        result = None
        print(e)
    return result

def htmlParsing(url):
    result = {}
    try:
        r = HTMLSession().get(url)
        # 自适应解码
        # r.html.encoding = r.apparent_encoding
        r.html.encoding = 'utf-8'
        
        # 获取标题
        if r.html.find('h2', first=True):
            result['title'] =  r.html.find('h2', first=True).text
        elif r.html.find('h1', first=True):
            result['title'] =  r.html.find('h1', first=True).text
        else:
            raise Exception('title not found')

        # 获取内容
        if r.html.find('.Custom_UnionStyle p', first=True):
            result['content'] = ''
            for p in r.html.find('.Custom_UnionStyle p'):
                result['content'] += p.text + '\n'
        elif r.html.find('.gsj_htmlcon_bot', first=True): 
            result['content'] = r.html.find('.gsj_htmlcon_bot', first=True).text
        else :
            raise Exception('content not found')
            
        # 若存在非文本型附件，将内容下载附件
        if r.html.find('.xiangqing_fujian a', first=True):
            result['attach'] = '/'.join(url.split('/')[2:-1]) + '/' + r.html.find('.xiangqing_fujian a', first=True).attrs['href'].split('/')[-1]
        elif r.html.find('.nyb_fj a', first=True):
            result['attach'] = '/'.join(url.split('/')[2:-1]) + '/' + r.html.find('.nyb_fj a', first=True).attrs['href'].split('/')[-1]
        else:
            result['attach'] = None
    except Exception as e:
        print(e)
        result = None
    return result

if __name__ == '__main__':
    links = []
    for page in range(1, 30):
        linksPart = MOASession('秸秆', str(page))
        if linksPart is not None:
            links.extend(list(linksPart))
        else:
            break
    docs = []
    for link in links:
        docRes = htmlParsing(link)
        if docRes is not None:
            docs.append(docRes)
        with open('moaUrl.txt', 'a') as f:
            f.write(link + '\n')
    # 判断目录是否存在
    if not os.path.exists('docs\\'):
        os.makedirs('docs\\')
    for doc in docs:
        if doc['attach'] is not None:
            if not os.path.exists('docs\\' + doc['title'] + '\\'):
                os.makedirs('docs\\' + doc['title'])
            urlretrieve('http://' + doc['attach'], 'docs\\' + doc['title'] + '\\附件.ceb')
            with open('docs\\' + doc['title'] + '\\' + doc['title'] + '.txt', 'a', encoding="utf-8") as fb:
                fb.write(doc['content'])
        else:
            with open('docs\\' + doc['title'] + '.txt', 'a', encoding="utf-8") as fb:
                fb.write(doc['content'])