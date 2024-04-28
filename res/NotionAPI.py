import requests
import json
import pandas as pd
import res.LoadingBar as loadingbar
from res.LoadingBar import ANSI_string
import sys
import os

def set_working_directory():
    # 獲取執行檔案的路徑
    exe_path = sys.argv[0]
    # 轉換為絕對路徑
    exe_dir = os.path.abspath(os.path.dirname(exe_path))
    # 設置工作目錄
    os.chdir(exe_dir)
set_working_directory()
secret_json_path = os.getcwd() + '\\SECRET.json'
file = open(secret_json_path)
data = json.load(file)

#integration
NOTION_TOKEN = data['notion_id']

#Database
PAGE_ID = data['page_id']

file.close()

class NotionClient():
    def __init__(self):
        self.notion_key = "secret_7nnWrn1Gwij3unEuz8XboKqDxC2wxJKJPdf215dNCuM"
        self.default_headers = {'Authorization': f"Bearer {self.notion_key}",
                                'Content-Type': 'application/json', 'Notion-Version': '2022-06-28'}
        self.session = requests.Session()
        self.session.headers.update(self.default_headers)    

    def create_database(self, data):
        url = "https://api.notion.com/v1/databases"
        response = self.session.post(url, json=data)
        return response.json()

    def create_page(self, data, databaseID):
        url = "https://api.notion.com/v1/pages"
        payload = {"parent": {"database_id": databaseID}, "properties": data}
        response = requests.post(url, headers=self.default_headers, json=payload)
        return response.json(),response.status_code

def CreateDatabase(page_id,author):
    notion_client = NotionClient()
    print("建立database中，請等待")
    loadingbar.waiting_loading_bar(1)
    # Create a database with some properties
    data = {
        "parent": {
            "type": "page_id",
            "page_id": page_id
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": f"{author}",
                    "link": None
                }
            }
        ],
        "properties": {
            "書名": {
                "title": {}
            },
            "書本封面": {
                 "files": {}
            },
            "書本連結": {
                 "url": {}
            },
            "ISBN": {
                "rich_text": {}
            },
            "作者": {
                "rich_text": {}
            },   
            "出版社": {
                "rich_text": {}
            },
            "出版日期": {
                "date": {}
            }    
        }
    }
    catches_create_response = notion_client.create_database(data)
    json_str = json.dumps(catches_create_response, indent=2)
    # # 寫入到文件
    # with open('catches_database.json', 'w', encoding='utf-8') as f:
    #     f.write(json_str)
    # f.close()
    #print(json_str)
    catches_dict = json.loads(json_str)
    # 從字典中取得 "id" 的值
    database_ID = catches_dict["id"]
    return database_ID

def NormalizeDate(date):
    if(not ('/' in date)):
        date = '1000/1/1'  
    date_split = date.split('/')
    year = date_split[0]
    mon =  date_split[1]
    day =  date_split[2]
    if(len(mon)==1):
        mon = '0' + mon
    if(len(day)==1):
        day = '0' + day
    return f'{year}-{mon}-{day}'

def CreatePage(databaseID,title=None,book_img=None,ISBN=None,author=None,publish=None,published_date=None,book_link=None):
    notion_client = NotionClient()
    published_date = NormalizeDate(published_date)
    data = {
        "書名": {"title": [{"text": {"content": title}}]},
        "書本封面": {
                    "id": "V%5E%5Be",
                    "type": "files",
                    "files": [
                        {
                            "name": book_img,
                            "type": "external",
                            "external": {
                                "url": book_img
                            }
                        }
                    ]
                },
        "ISBN": {
                    "rich_text": [
                        {
                            "text": {
                                "content": ISBN,
                            },
                        }
                    ]
                },
        "作者": {
                    "rich_text": [
                        {
                            "text": {
                                "content": author,
                            },
                        }
                    ]
                },
        "出版社": {
                    "rich_text": [
                        {
                            "text": {
                                "content": publish,
                            },
                        }
                    ]
                },
        "出版日期": {"date": {"start": published_date, "end": None}},
        "書本連結": {"url":book_link}
    }
    status_code = notion_client.create_page(data,databaseID)[1]
    if(status_code==200):
        print(ANSI_string(ANSI_string(f'{title}',bold=True)+'上傳至Notion成功',color='green'))
    else:
        print(ANSI_string(ANSI_string(f'{title}',bold=True)+'上傳至Notion失敗',color='red'))

def EstablishFullDatabase(keyword,df = pd.DataFrame({'書名': [], '書本封面':[], 'ISBN': [], '作者':[], '出版社':[],'出版日期':[], '書本連結': []})):
    databaseID = CreateDatabase(author=keyword,page_id=PAGE_ID)
    for i in range(len(df['書名'])):
        CreatePage(databaseID,title=df['書名'][i],book_img=df['書本封面'][i],ISBN=df['ISBN'][i],author=df['作者'][i],publish=df['出版社'][i],published_date=df['出版日期'][i],book_link=df['書本連結'][i])