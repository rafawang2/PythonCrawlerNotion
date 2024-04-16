import requests
from lxml import etree
import re

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               "AppleWebKit/537.36 (KHTML, like Gecko)"
               "Chrome/63.0.3239.132 Safari/537.36"}

def extract_book_id(url):
    # 使用正則表達式從URL中提取數字部分
    match = re.search(r'/products/(\d+)', url)
    if match:
        return match.group(1)
    else:
        return None

def get_BookTitle(html):
    title_x = html.xpath('/html/body/div[4]/div/div[1]/div/div/div/div[1]/h1/text()')
    #title_x = html.xpath('/html/body/div/div/div/div/div/div/div/h1/text()')
    if(title_x != []):
        title = title_x[-1]
        return title
    else:
        title_x = html.xpath('/html/body/div[4]/div/div[1]/div[2]/div[1]/h1/text()')
        if(title_x != []):
            title = title_x[-1]
            return title
        else:
            return '未找到資料'

def get_ISBN(html):
    ISBN_x = html.xpath('/html/body/div[4]/div/div/div[1]/div/div/ul[1]/li[1]/text()')
    #ISBN_x = html.xpath('/html/body/div/div/div/div/div/div/ul/li[1]/text()')
    if(ISBN_x != []):
        has_isbn = any(item.startswith('ISBN') or item.startswith('條碼') for item in ISBN_x)
        has_Eisbn = any(item.startswith('EISBN') for item in ISBN_x)
        if(has_isbn or has_Eisbn):
            ISBN = ISBN_x[-1].split("：")[1]
            return ISBN
        else:
            return '未找到ISBN'
    else:
        ISBN_x = html.xpath('/html/body/div[4]/div[3]/div[1]/section[5]/div/ul[1]/li[1]/text()')
        if(ISBN_x != []):
            ISBN = ISBN_x[-1].split("：")[1]
            return ISBN
        else:
            return '未找到資料'

def get_Author(html):
    author_x = html.xpath("/html/body/div/div/div/div/div/ul/li[contains(., '作者')]/a/text()")
    if(author_x == []):
        author_x = html.xpath("/html/body/div/div/div/div/div/ul/li[contains(., '編者')]/a/text()")
    if(author_x!=[]):
        if(' ' in author_x[0]):
            author = re.sub(r'\s+', '，', author_x[0])
            return author
        return author_x[0]
    else:
        author_x = html.xpath("/html/body/div/div/div/div/div/div/div/div/ul/li[contains(., '作者')]/a/text()")
        if(author_x == []):
            author_x = html.xpath("/html/body/div/div/div/div/div/div/div/div/ul/li[contains(., '編者')]/a/text()")
        if(author_x!=[]):
            if(' ' in author_x[0]):
                author = re.sub(r'\s+', '，', author_x[0])
                return author
            return author_x[0]
        else:
            return '未找到資料'
        
def get_Publishing(html):
    publish_x = html.xpath('/html/body/div/div/div/div/div/ul/li[contains(., "出版社")]/a/span/text()')
    if(publish_x != []):
        publish = publish_x[-1]
        return publish
    else:
        publish_x = html.xpath('/html/body/div/div/div/div/div/ul/li[contains(., "出版社")]/a/text()')
        if(publish_x != []):
            publish = publish_x[-1]
            return publish
        else:
            return '未找到資料'
        
def get_PublishDate(html):
    date_x = html.xpath('/html/body/div/div/div/div/div/ul/li[contains(., "出版日期")]/text()')
    if(date_x!=[]):
        return date_x[0].split("：")[1]
    else:
        date_x = html.xpath("/html/body/div/div/div/div/div/div/div/div/ul/li[contains(., '出版日期')]/text()")
        if(date_x!=[]):
            return date_x[0].split("：")[1]
        else:
            return '未找到資料'

def get_bookImg(html):
    img_x = html.xpath('/html/body/div[4]/div/div[1]/div[1]/div/div/img/@src')
    if(img_x != []):
        img_link = img_x[0].split('&')[0]
        img_link = img_link.split('?i=')[-1]
        return img_link
    else:
        img_x = html.xpath('/html/body/div[4]/div[1]/div[1]/div/div/div[1]/div[1]/div/img/@src')
        if(img_x != []):
            img_link = img_x[0].split('&')[0]
            img_link = img_link.split('?i=')[-1]
            return img_link
        else:
            return '未找到資料'
    
def get_book_data(url):
    res = requests.get(url,headers=headers, timeout=10)
    bookID = extract_book_id(url)
    if(res.status_code==requests.codes.ok):
        content = res.content.decode()
        html = etree.HTML(content)    
        title = get_BookTitle(html)
        ISBN = get_ISBN(html)
        author = get_Author(html)
        publish = get_Publishing(html)
        date = get_PublishDate(html)
        bookImglink = get_bookImg(html)
        book_data = [title, ISBN, author, publish, date, bookImglink]
        return book_data
    else:
        return 'fail'