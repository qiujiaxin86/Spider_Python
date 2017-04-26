#encoding=utf-8

#导入模块
import urllib2,re,urllib
from bs4 import BeautifulSoup
import json,time
import requests
import csv
import random
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

#定义抓取类
class JD:

    #记录抓取产品个数
    prodNum = 1
    #初始化参数
    def __init__(self,baseurl,page):
        self.baseurl = baseurl
        self.page = page
        #拼装成url
        self.url = self.baseurl+'&'+'page='+str(self.page)

    #获取html源代码
    def getHtml2(self,url):
        session = requests.Session()
        req = session.get(url, headers=headers)
        return req.text
        '''
        #请求抓取对象
        request = urllib2.Request(url)
        #响应对象
        reponse = urllib2.urlopen(request)
        #读取源代码
        html = reponse.read()
        #返回源代码
        return html
        '''

    def getHtml(self, url):
        req = urllib2.Request(url)
        req.add_header('User-Agent',
                       'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36')
        response = urllib2.urlopen(req)
        html = response.read()
        return html

    def getHtml3(self, url):
        # 能测试目前ip的网址
        iplist = ['175.155.25.62:808', '113.69.253.21:808', '36.249.28.178:808', '175.155.24.23:808']
        proxy_support = urllib2.ProxyHandler({'http': random.choice(iplist)})
        opener = urllib2.build_opener(proxy_support)
        # 定制、创建一个opener
        opener.addheaders = [('User-Agent',
                              'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36')]

        urllib2.install_opener(opener)
        # 安装opener
        req = urllib2.Request(url)
        print req
        response = urllib2.urlopen(req)
        print response
        html = response.read().decode('utf-8')
        print html
        return html

    #获取总页数
    def getNum(self,html):
        #封装成BeautifulSoup对象
        soup = BeautifulSoup(html,"html.parser")
        #定位到总页数节点
        items = soup.find_all('span',class_='p-skip')
        #获取总页数
        for item in items:
            pagenum = item.find('em').find('b').string
        return pagenum

    #获取所有产品id列表
    def getIds(self,html):
        #生成匹配规则
        pattern =  re.compile('<a target="_blank" href="//item.jd.com/(.*?).html".*?>')
        #查询匹配对象
        items = re.findall(pattern,html)
        return items

    def getIds_ziying(self, html):
        # 生成匹配规则
        pattern = re.compile('<a target="_blank" href="//item.jd.com/(.*?).html".*?>')
        # 查询匹配对象
        items = re.findall(pattern, html)
        new_items= []
        i = 0
        for item in items:
            time.sleep(3)
            i = i + 1
            if i<61:
                print item, i
                urlprod = basePd + str(item) + '.html'
                htmlprod = self.getHtml(urlprod)
                soup = BeautifulSoup(htmlprod, "html.parser")
                str1 = soup.find('div', {"class":"J-hove-wrap EDropdown fr"})
                if str1 is None:
                    continue
                else:
                    strs = str1.div.div.em
                    #print strs
                    if strs is None:
                        continue
                    else:
                        str1 = strs.contents[2][0:2]
                        print str1
                    if str1.encode('utf8') == "自营":
                        new_items.append(item)
                    #print "是否自营: "+soup.find('em', {"class":"u-jd"}).string
            else:
                break
        return new_items


    #获取产品价格
    def getPrice(self,id):
        url = 'http://p.3.cn/prices/mgets?skuIds=J_'+str(id)
        jsonString = self.getHtml(url)
        jsonObject = json.loads(jsonString.decode())
        price_jd = jsonObject[0]['p']
        price_mk = jsonObject[0]['m']
        print '京东价格：',str(price_jd)
        print '市场价格：',str(price_mk)

    def getPrice_jd(self, id):
        url = 'http://p.3.cn/prices/mgets?skuIds=J_' + str(id)
        jsonString = self.getHtml(url)
        jsonObject = json.loads(jsonString.decode())
        price_jd = jsonObject[0]['p']
        return price_jd


    #获取目录
    def getCategory(self,html,subid):
        soup = BeautifulSoup(html,"html.parser")
        l = []
        crumb_fl_clearfix = soup.find('div', {"class":"crumb fl clearfix"})
        items = crumb_fl_clearfix.findAll('div', {"class":"item"})
        for item in items:
            if item.a is not None:
                l.append(item.a.string)
        item_ellipsis = crumb_fl_clearfix.find('div', {"class":"item ellipsis"})
        l.append(item_ellipsis['title'])
        #加入商品名称
        sku_name = soup.find('div',{"class":"sku-name"}).stripped_strings
        for str1 in sku_name:
            l.append(u"商品名称: " + str(str1))
        #加入产品编码
        l.append(u"商品编号: "+str(subid))
        #加入京东价格
        l.append(u"价格:")
        price_jd = self.getPrice_jd(subid)
        l.append(price_jd)
        #res_date = json.dumps(l,ensure_ascii=False,encoding="gb2312")
        #print res_date
        return l

    #获取内容
    def getContent(self,html,subid):
        soup = BeautifulSoup(html,"html.parser")
        title = soup.find('div',class_='sku-name')
        print '\n-----------------第'+ str(JD.prodNum) +'个产品--------------------\n'
        for t in title:
            print '名称: ',t.string
        time.sleep(1)
        #价格
        self.getPrice(subid)
        #编码
        print '产品编码：%s' % (str(subid))
        items1 = soup.find_all('ul',class_='parameter1 p-parameter-list')
        #商品基本信息
        for item in items1:
            p = item.findAll('p')
            for i in p:
                print i.string
        # 商品基本信息
        items2 = soup.find_all('ul', class_='parameter2 p-parameter-list')
        for item in items2:
            p = item.findAll('li')
            for i in p:
                print i.string
        #规格与包装
        items3 = soup.find_all('div',class_='Ptable-item')
        for item in items3:
            contents1 = item.findAll('dt')
            contents2 = item.findAll('dd')
            for i in range(len(contents1)):
                print contents1[i].string,contents2[i].string
        JD.prodNum += 1

    #启动抓取程序
    def start(self):
        html = self.getHtml(self.url)
        pageNum = self.getNum(html)
        print '正在抓取网页请稍后............'
        time.sleep(3)
        print '抓取完毕，本次共抓取',pageNum,'页。'
        time.sleep(1)
        print '正在解析内容.........'
        #循环1--页数
        writer = csv.writer(csvFile)
        for page in range(1,int(pageNum)+1):
            abc = ["第 ", page, "页"]
            writer.writerow(abc)
            print "第 "+ str(page) + " 页"
            url = self.baseurl+'&'+'page='+str(page)
            url_list= [url]
            writer.writerow(url_list)
            html = self.getHtml(url)
            #ids = self.getIds(html)
            ids = self.getIds_ziying(html)
            #将筛选完的id输出到文件中
            #writer.writerow(ids)
            #循环2--产品列表
            for id in ids:
                urlprod = basePd+str(id)+'.html'
                htmlprod = self.getHtml(urlprod)
                id_category = self.getCategory(htmlprod, id)
                if float(id_category[-1]) <= 300.00:
                    writer.writerow(id_category)
                    res_date = json.dumps(id_category, ensure_ascii=False, encoding="gb2312")
                    print res_date
                else:
                    continue
                '''
                subids = self.getIdByItems(id)
                #循环3--产品组列表
                for subid in subids:
                    urlsubprod = basePd+str(subid)+'.html'
                    subhtml = self.getHtml(urlsubprod)
                    time.sleep(1)
                    self.getContent(subhtml,subid)
                '''
        csvFile.close()


headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Accept-Encoding": "gzip,deflate,sdch","Accept":"*/*","Accept-Language":"zh-CN,zh;q=0.8"}

#产品列表base页
basePd  = 'http://item.jd.com/'

'''
抓取入口URL
手机
baseURL = 'http://list.jd.com/list.html?cat=9987,653,655'

剃须刀
baseURL = 'https://list.jd.com/list.html?cat=737,1276,739'

牙刷
baseURL = 'https://list.jd.com/list.html?cat=1316,1384,1406'

牙膏
baseURL = 'https://list.jd.com/list.html?cat=1316,1384,1405'

茶具_茶杯
baseURL = 'https://list.jd.com/list.html?cat=6196,11143,11149'

茶壶
baseURL = 'https://list.jd.com/list.html?cat=6196,11143,11150'

整套茶具
baseURL = 'https://list.jd.com/list.html?cat=6196,11143,11148'

文具
baseURL = 'https://list.jd.com/list.html?cat=670,729,1449'

四件套
baseURL = 'https://list.jd.com/list.html?cat=1620,1621,1626'

被子
baseURL = 'https://list.jd.com/list.html?cat=1620,1621,1627'

枕头
baseURL = 'https://list.jd.com/list.html?cat=1620,1621,1628'

#炒锅
baseURL = 'https://list.jd.com/list.html?cat=6196,6197,6199'

#煎锅
baseURL = 'https://list.jd.com/list.html?cat=6196,6197,6200'

#压力锅
baseURL = 'https://list.jd.com/list.html?cat=6196,6197,6201'

#蒸锅
baseURL = 'https://list.jd.com/list.html?cat=6196,6197,6202'

#汤锅
baseURL = 'https://list.jd.com/list.html?cat=6196,6197,6203'
#火锅
baseURL = 'https://list.jd.com/list.html?cat=6196,6197,11976'

#储物置物架
baseURL = 'https://list.jd.com/list.html?cat=6196,6214,11977'

#保鲜盒
baseURL = 'https://list.jd.com/list.html?cat=6196,6214,6215'

#厨房小工具：
baseURL = 'https://list.jd.com/list.html?cat=6196,6214,11978'

#雨伞
baseURL = 'https://list.jd.com/list.html?cat=1620,1624,1656'

#保温杯
baseURL = 'https://list.jd.com/list.html?cat=6196,6219,6223'

#茶壶
baseURL = 'https://list.jd.com/list.html?cat=6196,11143,11150'

#遥控电动
baseURL = 'https://list.jd.com/list.html?cat=6233,6235'
'''

#户外健身 户外游乐设备
baseURL = 'https://list.jd.com/list.html?cat=6233,6260,6268'

#生成爬虫抓取对象
spider = JD(baseURL,1)

csvFile = open("/Users/qiujiaxin/Desktop/jdspider/wanju_huwaiyouleshebei.csv",'ab+')

#开始抓取
spider.start()