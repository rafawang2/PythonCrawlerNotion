import os
import requests
from lxml import etree
import pandas as pd
import re
from res.GetPageData import page_crawel
from res import NotionAPI
from res.LoadingBar import ANSI_string
from res.NotionAPI import set_working_directory
import json

NO_secret_json = False  #預設有SECRET.json檔案

def generate_author_url(keyword):   #輸入作者後產生作者頁面之連結
    link = "https://search.books.com.tw/search/query/cat/1/v/1/adv_author/1/key/" + keyword
    print(link)
    return link

def generate_page_link(keyword,page):
    link = "https://search.books.com.tw/search/query/cat/all/sort/1/v/1/adv_author/1/spell/3/ms2/ms2_1/page/" + str(page) + "/key/" + keyword
    return link

def generate_book_url(bookID): #利用書本ID產生該書連結
    return "https://www.books.com.tw/products/" + bookID + "?sloc=main"


if __name__ == "__main__":
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                "AppleWebKit/537.36 (KHTML, like Gecko)"
                "Chrome/63.0.3239.132 Safari/537.36"}

    keyword=str(input("請輸入作者:"))
    print("建立連結中...")
    res = requests.get(generate_author_url(keyword),headers=headers)
    if(res.status_code == requests.codes.ok):
        content = res.content.decode()  #解碼網頁
        html = etree.HTML(content)
        pages_cnt_list = html.xpath('/html/body/div/div/div/div/div/ul/li/select/option/text()')
        if(pages_cnt_list!=[]):
            pages_cnt = re.search(r'\d+', pages_cnt_list[0])
            pages_cnt = int(pages_cnt.group())
        else:
            pages_cnt = 1
        print(f'共{pages_cnt}頁')
        df = pd.DataFrame({'書名': [], '書本封面':[], 'ISBN': [], '作者':[], '出版社':[],'出版日期':[], '書本連結': []})
        for i in range(1,pages_cnt+1):
            page_link = generate_page_link(keyword,i)
            print(ANSI_string(f'抓取第{i}頁資料中',bold=True))
            df = pd.concat([df, page_crawel(page_link)], ignore_index=True, axis=0)
        
        print('所有書籍抓取完畢!')
        print(df)
        
        set_working_directory()
        current_directory = os.getcwd()
        csv_directory = os.path.join(current_directory, "作者csv")
        if not os.path.exists(csv_directory):
            os.makedirs(csv_directory)
        file_path = os.path.join(csv_directory, keyword + ".csv")
        df.to_csv(file_path,index=False,encoding='utf-8')   #寫出成csv
        
        
        set_working_directory()
        # 檢查是否存在 SECRET.json 檔案
        secret_json_path = os.path.join(os.getcwd(), 'SECRET.json')
        if os.path.exists(secret_json_path):
            # 讀取 JSON 檔案
            with open(secret_json_path) as file:
                data = json.load(file)
            # 取得 integration 和 Database 資訊
            NOTION_TOKEN = data.get('notion_id')
            PAGE_ID = data.get('page_id')
            file.close()
        else:
            NO_secret_json = True
        
        if(NOTION_TOKEN != "" or PAGE_ID != ""):
            upload = input('是否要將資料匯入Notion(y/n)\n')
            if(upload=='y'):
                NotionAPI.EstablishFullDatabase(keyword=keyword,df=df,page_id=PAGE_ID)
            else:
                print('未啟用自動上傳，可以使用Notion的匯入csv功能建立database')
        elif(NO_secret_json):
            print(ANSI_string(s='SECRET.json不存在，請確保有使用SetUp.exe輸入您的整合密碼及Page連結',color='red'))
        elif(NOTION_TOKEN == ""):
            print(ANSI_string(s='無效的整合密碼，請確認頁面是否成功連結到您的integration，或是再次檢查整合密碼是否有誤',color='red'))
        elif(PAGE_ID == ""):
            print(ANSI_string(s='無效的Page ID，請再次確認連結無誤',color='red'))
    else:
        print('存取被拒')