import asyncio
import multiprocessing
import time
import re
import html

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import aiohttp
import motor.motor_asyncio
from bs4 import BeautifulSoup

# 头条的URLs
toutiao_urls = [
    'https://www.toutiao.com/',
    'https://www.toutiao.com/ch/news_hot/',
    'https://www.toutiao.com/ch/news_tech/',
    'https://www.toutiao.com/ch/news_entertainment/',
    'https://www.toutiao.com/ch/news_game/',
]
# motor_asyncio_mogodb
client = motor.motor_asyncio.AsyncIOMotorClient('localhost',27017)
db = client['toutiao']
collection = db['toutiao_spider']

def config_driver():
    '''
    配置你的浏览器
    :param ok_headless:
    :return:
    '''
    opts = Options()
    # 设置不加载图片
    prefs = {"profile.managed_default_content_settings.images": 2}
    opts.add_experimental_option("prefs", prefs)
    # 添加headless 模式
    opts.add_argument('--headless')
    driver = webdriver.Chrome(chrome_options=opts)
    return driver

async def get_page_souse(url):
    '''
    :param pull_down_num: 下拉次数
    :param pixel: 每次下拉像素
    :return:
    '''

    pull_down_num = 300
    pixel = 2000
    driver = config_driver()
    driver.get(url)
    time.sleep(.5)
    entry = await get_info(0, driver.page_source)
    for i in range(pull_down_num):
        driver.execute_script('window.scrollTo(0,%s);' % pixel)
        pixel += 200
        entry = await get_info(entry, driver.page_source)
        time.sleep(.3)

async def get_info(entry, response):
    '''
    :param entry: 跳过的条目
    :param response: 网页源码
    :return:  这次条条目数量
    '''
    all_info = BeautifulSoup(response, 'lxml').find(
        'div', {'class': 'wcommonFeed'}).find_all('li', {'class': 'item'})
    for li in all_info[entry:]:
        try:
            is_article = li.find('a', {'class': 'link'}).parent.attrs[
                'ga_event']
            if is_article != 'article_title_click':
                continue
            title = li.find('a', {'class': 'link'}).text.replace(" ", '')
            url = 'https://toutiao.com' + \
                  li.find('a', {'class': 'link'})['href']
            source = li.find(
                'a', class_='source').get_text().replace('\xa0', '')
            crawl_time = time.strftime(
                '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
            if '/api/pc/subject/' in url:
                continue
            result = re.findall("content: '([ \\']*.*)", await get_detail(url))[0]
            soup = BeautifulSoup(html.unescape(result[:-2]), 'lxml')
            content = soup.get_text()
            result = re.findall("time: '([ \\']*.*)", await get_detail(url))[0]
            soup = BeautifulSoup(html.unescape(result[:-2]), 'lxml')
            publish_time = soup.get_text()
        except AttributeError:
            continue
        except IndexError:
            pass
        else:
            document = {
                'title': title,
                'url': url,
                'source': source,
                'crawl_time': crawl_time,
                'content': content,
                'publish_time': publish_time
            }
            # insert to mongodb
            await do_insert(document)
    return len(all_info)

async def get_detail(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as res:
            return await res.text()

async def do_insert(docuemnt):
    try:
        result = await collection.insert_one(docuemnt)
    except BaseException as e:
        print('error :%s'%e)
    else:
        print('result %s' % repr(result.inserted_id))

def run(url):
    loop = asyncio.get_event_loop()
    tasks = [get_page_souse(url), ]
    loop.run_until_complete(asyncio.wait(tasks))
    loop.close()


if __name__ == '__main__':
    # Pool
    p = multiprocessing.Pool()
    for url in toutiao_urls:
        p.apply_async(run,args=(url,))

    p.close()
    p.join()
