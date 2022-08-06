# -*- coding: utf-8 -*-
# Author: viotbery
# Time: 2022-08-03
from ast import keyword
from itertools import count
from time import sleep
from turtle import title
from unittest import result
from requests_html import HTMLSession
from urllib.request import urlretrieve
import os
import random
import time
# 已支持网站
# MOA:　中国农业农村部（http://www.moa.gov.cn/）
# ANNYNC: 农业农村部（http://www.nync.gov.cn/）

MOABASEURL = 'http://www.moa.gov.cn/govsearch/gov_list_ad_media_new.jsp?'
# 网站url
# 参数类型：
# Title：标题
# page：页码
# SearchClassInfoId2： 搜索类别（默认为71，政策法规类）
# SType：未知

ANNYNC_BASE_URL = 'http://nync.ah.gov.cn/site/search/6796471?'

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

def MOAdownLoad():
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

def ANNYNCUrl(keywords, pageIndex, beginDate, endDate):
    isAllSite	=	'false'
    platformCode	=	'anhui_szbm_4'
    siteId	=	'6796471'
    ssqdZoneCode	=	'340000000000'
    ssqdDeptCode	=	'34000011010000000000'
    fromCode	=	'title'
    orderType	=	'0'
    pageSize	=	'20'
    fuzzySearch	=	'false'
    sort	=	'desc'
    flag	=	'true'
    return ANNYNC_BASE_URL + 'isAllSite=' + isAllSite + '&platformCode=' + platformCode + '&siteId=' + siteId + '&ssqdZoneCode=' + ssqdZoneCode + '&ssqdDeptCode=' + ssqdDeptCode + '&beginDate=' + beginDate + '&endDate=' + endDate + '&fromCode=' + fromCode + '&orderType=' + orderType + '&pageSize=' + pageSize + '&fuzzySearch=' + fuzzySearch + '&keywords=' + keywords + '&sort=' + sort + '&flag=' + flag + '&pageIndex=' + pageIndex

def ANNYNCSeesion(keywords, pageIndex, beginDate, endDate):
    try: 
        r = HTMLSession().get(ANNYNCUrl(keywords, pageIndex, beginDate, endDate))
        # 自适应解码
        r.html.encoding = r.apparent_encoding
        result = []
        lists = r.html.find('.search-list')
        if lists:
            for list in lists:
                doc = {
                    'title': list.find('.search-title a', first=True).attrs['title'],
                   'link': list.find('.search-title a', first=True).attrs['href'],
                   'date': list.find('.search-resources .date', first=True).text
                }
                result.append(doc)
        else :
            result = None
    except Exception as e:
        result = None
        print(e)
    return result

def ANNYNCHtmlParsing(url):
    content = ''
    try:
        r = HTMLSession().get(url)
        # 自适应解码
        r.html.encoding = r.apparent_encoding
        doc = r.html.find('.j-fontContent.newscontnet', first=True)
        if doc:
            for p in doc.find('p'):
                if p.text != '':
                    content += p.text + '\n' + '\n'
        else:
            raise Exception('content not found')
    except Exception as e:
        print('errrrrooooo:', e)
        content = None
    if content == '':
        content = '未发现文本内容，可能是纯图片或视频'
    return content


if __name__ == '__main__':
    keyWords = '秸秆'
    beginDate = '2013-01-01'
    endDate = '2022-08-06'
    result = []
    for page in range(1, 30):
        res = ANNYNCSeesion(keyWords, str(page), beginDate, endDate)
        if res:
            result.extend(res)
            # 随机休眠一定时间
            time.sleep(random.random() * 2)
            print('正在爬取第' + str(page) + '页')
        else:
            break
    print('网页链接爬取完毕，本次共采集了' + str(len(result)) + '条数据')
    if not os.path.exists('docs-AHNCNY\\'):
        os.makedirs('docs-AHNCNY\\')
    count = 0
    for doc in result:
        content = None
        content = ANNYNCHtmlParsing(doc['link'])
        time.sleep(random.random() * 2)
        if content:
            with open('docs-AHNCNY\\' + doc['date'] + ' ' + doc['title'] + '.txt', 'a', encoding="utf-8") as fb:
                fb.write(content)
                count += 1
                print('正在记录第' + str(count) + '条数据,进度：[ ' + str(count / len(result) * 100) + '% ]')
        with open('安徽农业农村厅文章对应链接.txt', 'a') as f:
            f.write('文章标题： ' + doc['title'] + '\n')
            f.write('发布时间： ' + doc['date'] + '\n')
            f.write('原链接： ' + doc['link'] + '\n\n')



