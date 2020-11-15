import requests
from bs4 import BeautifulSoup
# import codecs
import csv
import re

def getHTML(url):
    r = requests.get(url)
    return r.content

def parseHTML(url):
    html = getHTML(url)
    soup = BeautifulSoup(html, 'html.parser')  # html.parser是解析器
    div_people_list = soup.find('table', attrs={'align': 'left'})  # 定位到要爬取的第一行
    # print(div_people_list)
    # ul_people_list = div_people_list.find('ul', attrs={'class': 'ul-imgtxtq2'})
    a_s = div_people_list.find_all('a', attrs={'target': '_blank'})
    temp_list = []  # 创建空列表
    for a in a_s:
        url = a['href']
        name = a.get_text()
        print(name, url)
        temp_list.append([name,url])  # 注意转码问题
    return temp_list

# 将列表转成csv
def writeCSV(file_name,data_list):
    with open(file_name,'w',newline='') as f:
        writer = csv.writer(f)
        for data in data_list:
            writer.writerow(data)

# 获取页面
def get_page(url,page_num):
    pageList =[]
    for i in range(1,page_num +1):
        formdata ={'type':'index' ,
                   'paged': i}
        try:
            r = requests.post(url,data =formdata)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            print('链接成功')
            p = re.compile(r'href="(http://www.jdlingyu.net/\d{5}/)"')
            tempList = re.findall(p,r.text)
            for each in tempList:
                pageList.append(each)
                print('保存页面成功')
            tempList = []
        except:
            print('链接失败')
    print(pageList)
    return pageList

if __name__=="__main__":
    url = 'https://search.jd.com/Search?keyword=%E7%94%B5%E8%84%91&page=1'    #基础url
    print(getHTML(url))
    # for i in range(1,4,2):
    #     url_page = url.format(str(i))
    #     print(getHTML(url_page))
    # data_list = parseHTML(url)
    # writeCSV('data.csv',data_list)
