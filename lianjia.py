# -* coding: utf-8 *-

import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import time



class LianjiaSpider(object):

    def __init__(self):
        self.headers = {"User-Agent": UserAgent().random}
        self.datas = list()

    def getTotalPage(self, url):
        #request 请求目标网页
        response = requests.get(url, headers = self.headers)
        if response.status_code == 200:
            source = response.text
            #使用BeautifulSoup解析网页
            soup = BeautifulSoup(source, "html.parser")
            #解析到总页数字段
            pageData = soup.find("div", class_ = "page-box house-lst-page-box")["page-data"]
            totalPage = eval(pageData)["totalPage"] # eval()把字符串转换为字典
            return  totalPage
        else:
            print("请求失败")
            return None


    def getContent(self, url):
        totalPage = self.getTotalPage(url)
        totalPage = 2 #为了方便调试，我这里把总页数写死了
        # 循环处理每个目标页面
        for pageNum in range(1, totalPage+1 ):
            url = "https://bj.lianjia.com/ershoufang/pg{}/".format(pageNum)
            print("正在获取第{}页数据: {}".format(pageNum,url))
            response = requests.get(url, headers = self.headers)
            soup = BeautifulSoup(response.text, "html.parser")
            links = soup.find_all("div", class_ = "info clear")
            for i in links:
                link = i.find("a")["href"]
                detail = self.parseDetail(link)
                self.datas.append(detail)
                #为了防止反爬限制休眠1s
                time.sleep(1)

        # 数据存储到csv文件中
        data = pd.DataFrame(self.datas)
        # 自定义字段
        columns = ["小区", "户型", "面积", "价格", "单价", "朝向", "电梯", "位置", "地铁"]
        data.to_csv("./lianjiaData.csv", encoding='utf_8_sig', index=False, columns=columns)


    def parseDetail(self, url):
        # request 请求详情页
        response = requests.get(url, headers = self.headers)
        detail = {}
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            detail["价格"] = soup.find("span", class_ = "total").text
            detail["单价"] = soup.find("span", class_ = "unitPriceValue").text
            detail["小区"] = soup.find("div", class_ = "communityName").find("a", class_ = "info").text
            detail["位置"] = soup.find("div", class_="areaName").find("span", class_="info").text
            detail["地铁"] = soup.find("div", class_="areaName").find("a", class_="supplement").text
            base = soup.find("div", class_ = "base").find_all("li") # 基本信息
            detail["户型"] = base[0].text[4:]
            detail["面积"] = base[2].text[4:]
            detail["朝向"] = base[6].text[4:]
            detail["电梯"] = base[10].text[4:]
            return detail
        else:
            return None

if __name__ == "__main__":
    Lianjia = LianjiaSpider()
    Lianjia.getContent("https://bj.lianjia.com/ershoufang/")
