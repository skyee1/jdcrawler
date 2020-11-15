import json
import pandas
import requests
from lxml import etree
from selenium import webdriver
import time

from selenium.common.exceptions import NoSuchElementException

DRIVER_PATH = r'C:\Users\Lenovo-yi\AppData\Local\Google\Chrome\Application\chromedriver.exe'

FIRST_PATH = r'https://search.jd.com/Search?keyword=%E5%8F%A3%E7%BA%A2&enc=utf-8&wq=%E5%8F%A3%E7%BA%A2&pvid=6be9016dfc5540edbef74a51f2c2a273'

COMMENTS_PATH = r'https://club.jd.com/comment/productCommentSummaries.action?referenceIds={}'

HEADERS = {
    'user-agen': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
    'cookie': 'unpl=V2_ZzNtbUMCER18XEcGKBhUDWIDRw5KVUdCcF8WBHMQWgViAxZdclRCFnQURlRnGFoUZwUZXkpcQhJFCEdkexhdBGYCEFpBU3NMJVZGV3lFFzVXABJtQlZzFXIJQ1J%2bGV4AYwQVX0JVQBN9CkZTeylsAlczIlxyVnMURUMoVTYZWwRiBRddQFJHEnIKRlZ4H1QHZwQSbUNnQA%3d%3d; __jdu=1604741345663132793161; areaId=18; ipLoc-djd=18-1482-48936-0; shshshfpa=fcb5b36d-db9c-931b-edea-ecb21a944a6d-1604741349; mt_xid=V2_52007VwMVU1heV1odTB1bAmUDEFFbUFBaGEkpWwRkCxIHCl1OChdMSkAAZAdATg4IVlgDTEpVUGQGE1UNCldfL0oYXwR7AxJOXF5DWhlCGlQOZwMiUm1YYlkXSB1fDGMHFVptWlZbHQ%3D%3D; shshshfpb=kd%202RH1aDS4sOP5TOE%2FGrKw%3D%3D; rkv=1.0; __jdv=76161171|www.hao123.com|t_1000003625_hao123mz|tuiguang|0dc98e0cb09941db935f4faa98714151|1604741751487; PCSYCityID=CN_430000_430100_430104; __jdc=122270672; shshshfp=b13d7102f6b201c2954488f6c94d4a5b; 3AB9D23F7A4B3C9B=IFH5A4XVR2VS3SRDML5Q5XXT5K4DGIHLTMNY2RIK6TQ4B3GKX7NHUIPWQLLMHDYTXVF7S2OP52P5GW53AJMMLMVGKA; shshshsID=9da14bcc40776a1a916853ef905c2c69_1_1605431336461; __jda=122270672.1604741345663132793161.1604741345.1605428659.1605431337.3; __jdb=122270672.1.1604741345663132793161|3.1605431337; qrsc=3'
}

driver = webdriver.Chrome(executable_path=DRIVER_PATH)


# 根据url处理列表页信息
def parse_list_page(url):
    driver.get(url)

    # 向下滑动 加载完全页面
    for i in range(2):
        driver.execute_script('document.documentElement.scrollTop=6000')
        time.sleep(3)  # 3秒再滑

    # 拿到网页完整源代码
    resp = driver.page_source
    html = etree.HTML(resp)

    goods_ids = html.xpath('.//ul[@class="gl-warp clearfix"]/li[@class="gl-item"]/@data-sku')
    goods_names_tag = html.xpath('.//div[@class="p-name p-name-type-2"]/a/em')
    goods_stores_tag = html.xpath('.//div[@class="p-shop"]')
    print(goods_ids)
    print(goods_names_tag)
    print(goods_stores_tag)

    goods_names = []
    for goods_name in goods_names_tag:
        goods_names.append(goods_name.xpath('string(.)').strip())

    goods_stores = []
    for goods_store in goods_stores_tag:
        goods_stores.append(goods_store.xpath('string(.)').strip())

    goods_infos = list()
    for i in range(0, len(goods_ids)):
        goods_info = dict()
        goods_info['goods_id'] = goods_ids[i]
        goods_info['goods_name'] = goods_names[i]
        goods_info['goods_store'] = goods_stores[i]

        goods_infos.append(goods_info)

    return goods_infos


# 根据商品id获取商品的评论数量统计信息
def get_goods_comment(goods_id):
    url = COMMENTS_PATH.format(goods_id)
    resp_text = requests.get(url=url, headers=HEADERS).text
    comment_json = json.loads(resp_text)
    # print(comment_json)
    comments_count = comment_json['CommentsCount'][0]
    # 评论总数
    comment_count = comments_count['CommentCount']
    # 默认好评数
    default_good_count = comments_count['DefaultGoodCount']
    # 好评数
    good_count = comments_count['GoodCount']
    # 普通评价数
    general_count = comments_count['GeneralCount']
    # 差评数
    poor_count = comments_count['PoorCount']
    # 追评数
    after_count = comments_count['AfterCount']
    # 好评率
    good_rate = comments_count['GoodRate']

    comment_info = dict()
    comment_info['comment_count'] = comment_count
    comment_info['default_good_count'] = default_good_count
    comment_info['good_count'] = good_count
    comment_info['general_count'] = general_count
    comment_info['poor_count'] = poor_count
    comment_info['after_count'] = after_count
    comment_info['good_rate'] = good_rate

    return comment_info


def get_next_page_url():
    try:
        next_btn = driver.find_element_by_xpath('.//a[@class="pn-next"]')
        next_btn.click()
        cur_url = driver.current_url
        return cur_url
    except NoSuchElementException as e:
        return ""


i = 1

info_list = list()


def spider_run(url):
    goods_infos = parse_list_page(url)

    for goods_info in goods_infos:
        comment_info = get_goods_comment(goods_info['goods_id'])

        # 将信息合并成一个商品的完整信息
        info = dict(goods_info, **comment_info)

        print(info)
        info_list.append(info)
        print(len(info_list))

    global i
    pandas.DataFrame(info_list).to_csv('jd_kh_{}.csv'.format(i))
    i += 1
    info_list.clear()

    next_page_url = get_next_page_url()
    if next_page_url != "":
        spider_run(next_page_url)


if __name__ == '__main__':
    spider_run(FIRST_PATH)
