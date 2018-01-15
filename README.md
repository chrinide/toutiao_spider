# toutiao_spider

今日头条异步爬虫代码

> run
```shell
pip install -r requirements.txt
```
> requirements.txt

```txt

aiohttp==2.3.7
async-timeout==2.0.0
beautifulsoup4==4.6.0
chardet==3.0.4
idna==2.6
motor==1.2.0
multidict==4.0.0
pymongo==3.6.0
selenium==3.8.1
yarl==0.18.0
```

> Selenium Chrome Driver 

- Chrome =  63.0
- Chromedriver =  2.35

> toutiao_urls

```python
toutiao_urls = [
    'https://www.toutiao.com/',
    'https://www.toutiao.com/ch/news_hot/',
    'https://www.toutiao.com/ch/news_tech/',
    'https://www.toutiao.com/ch/news_entertainment/',
    'https://www.toutiao.com/ch/news_game/',
]
```
