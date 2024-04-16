import requests
import json
import pandas as pd
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
NOTION_TOKEN = data['id']

#Database
DATABASE_ID = data['database']

file.close()


headers = {
    "Authorization": "Bearer " + NOTION_TOKEN,
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def get_pages(num_pages=None):
    """
    If num_pages is None, get all pages, otherwise just the defined number.
    """
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"

    get_all = num_pages is None
    page_size = 1000 if get_all else num_pages

    payload = {"page_size": page_size}
    response = requests.post(url, json=payload, headers=headers)

    data = response.json()

    # Comment this out to dump all data to a file
    import json
    with open('db.json', 'w', encoding='utf8') as f:
       json.dump(data, f, ensure_ascii=False, indent=4)

    results = data["results"]
    while data["has_more"] and get_all:
        payload = {"page_size": page_size, "start_cursor": data["next_cursor"]}
        url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        results.extend(data["results"])
    return results,data


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
    

def create_page(title,book_img,ISBN,author,publish,published_date,book_link): #寫出新的
    get_pages()
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
    create_url = "https://api.notion.com/v1/pages"

    payload = {"parent": {"database_id": DATABASE_ID}, "properties": data}
    res = requests.post(create_url, headers=headers, json=payload)  #帶著資料前往API，API會將資料(data)丟進Notion
    if(res.status_code==200):
        print(ANSI_string(ANSI_string(f'{title}',bold=True)+'上傳至Notion成功',color='green'))
    else:
        print(ANSI_string(ANSI_string(f'{title}',bold=True)+'上傳至Notion失敗',color='red'))
    return res

def delete_page(page_id: str):
    url = f"https://api.notion.com/v1/pages/{page_id}"

    payload = {"archived": True}

    res = requests.patch(url, json=payload, headers=headers)
    return res

def delete_All_page():
    data = get_pages(100)[1]
    page_cnt = 0
    while(data['results']!=[]):
        page_cnt = page_cnt+1 
        data = get_pages()[1]
        ids = [result['id'] for result in data['results']]
        ids_copy = ids.copy()
        total_items = len(ids)
        for id in ids_copy:
            completed_items = total_items - len(ids) +1
            progress_percentage = int((completed_items / total_items) * 100)
            progress = '[' + ANSI_string('=',color='cyan') * (progress_percentage // 5) + ANSI_string('=',color='yellow') * (20 - progress_percentage // 5) + ']'
            sys.stdout.write('\r' + progress + f' 刪除舊資料第{page_cnt}頁，請等待...' + f'({completed_items}/{total_items} , {int((completed_items/total_items)*100)}%)')
            sys.stdout.flush()
            delete_page(id)
            ids.remove(id)
        sys.stdout.write('\n')
        ids.clear()

def EstablishFullDatabase(df = pd.DataFrame({'書名': [], '書本封面':[], 'ISBN': [], '作者':[], '出版社':[],'出版日期':[], '書本連結': []})):
    delete_All_page()
    for i in range(len(df['書名'])):
        create_page(title=df['書名'][i],book_img=df['書本封面'][i],ISBN=df['ISBN'][i],author=df['作者'][i],publish=df['出版社'][i],published_date=df['出版日期'][i],book_link=df['書本連結'][i])

get_pages()