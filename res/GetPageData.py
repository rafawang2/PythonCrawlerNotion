import requests
from lxml import etree
import pandas as pd
import re
from res import GetBookData as GBD
from res.LoadingBar import waiting_loading_bar, getData_loading_bar, ANSI_string

def generate_author_url(keyword):   #輸入作者後產生作者頁面之連結
    link = "https://search.books.com.tw/search/query/key/"+keyword+"/adv_author/1/"
    print(link)
    return link

def generate_book_url(bookID): #利用書本ID產生該書連結
    return "https://www.books.com.tw/products/" + bookID + "?sloc=main"

def get_bookID(book_links): #取得書本ID，為產生書本連結用
    book_ids = []
    for link in book_links:
        book_id_match = re.search(r'/item/([^/]+?)/', link)
        if book_id_match:
            book_id = book_id_match.group(1)
            book_ids.append(book_id)
        else:
            print(f"No book ID found in link: {link}")
    return book_ids

headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
               "AppleWebKit/537.36 (KHTML, like Gecko)"
               "Chrome/63.0.3239.132 Safari/537.36"}

def page_crawel(page_url):
    res = requests.get(page_url,headers=headers)
    if(res.status_code==requests.codes.ok):
        print("連接成功!")
        print("抓取資料...")
        
        content = res.content.decode()  #解碼網頁
        html = etree.HTML(content)
        
        book_link = html.xpath('/html/body/div/div/div/div/div/div/div/div/h4/a/@href') #將此頁面所有書籍連結都放進book_link[]
        bookIDs = get_bookID(book_link) #把ID從連結擷取出來
        
        #產生書籍連結陣列，可以遍歷這個陣列來達成此頁面所有書籍的訪問
        booklinks = []
        for id in bookIDs:
            booklinks.append(generate_book_url(id))
        
        print(f"抓取到{len(bookIDs)}筆書本連結資料")
        
        titles                  = []    #書名陣列 
        ISBNs                   = []    #ISBN
        authors                 = []    #作者
        publishs                = []    #出版社
        dates                   = []    #出版日期
        bookImglinks            = []    #書本封面圖片連結
        Successful_books_links  = []    #成功抓到的書籍連結    
        Failed_books_links      = []    #存取被拒的書籍連結
        
        cnt = 0 #計數器，可以知道抓到的資料數
        for link in booklinks:  #開始第一次訪問所有書籍連結
            getData_loading_bar(2,cnt+1)     #間隔兩秒請求一次以免因為過量請求而被伺服器拒絕
            BookData = GBD.get_book_data(link)  #利用自訂函式求得此單本書籍的基本資料
            
            if(BookData!='fail'):   #書本連結存取正常
                if BookData[0] == '未找到資料':     #網路異常導致抓取錯誤，放進失敗陣列，之後反覆檢查
                    print(ANSI_string('資料未正確抓取',color='red'))
                    Failed_books_links.append(link)
                else:
                    print(ANSI_string('成功抓取資料',color='green') + ANSI_string(f'　{BookData}',bold=True))
                    titles.append(BookData[0])
                    ISBNs.append(BookData[1])
                    authors.append(BookData[2])
                    publishs.append(BookData[3])
                    dates.append(BookData[4])
                    bookImglinks.append(BookData[5])
                    Successful_books_links.append(link)
                    BookData = []
            else:   #書籍連結存取被拒，放進失敗陣列等待重複檢查跟請求
                print(ANSI_string(f'{BookData}',color='red'))
                Failed_books_links.append(link)
            cnt=cnt+1
        df = pd.DataFrame({'書名': titles, '書本封面':bookImglinks, 'ISBN': ISBNs, '作者':authors, '出版社':publishs,'出版日期':dates, '書本連結': Successful_books_links})
        
        if(Failed_books_links!=[]):
            print('抓取失敗的資料連結如下')
            df_failed = pd.DataFrame({'連結':Failed_books_links})
            print(df_failed,end="\n<====================================================>\n")
        
        fail_cnt = 1
        while Failed_books_links:   #走訪失敗陣列，成功抓取目前索引的資料則將此索引之書籍連結移出失敗陣列，直到失敗陣列裡的連結都被成功抓取
            fail_book_cnt = 1
            print('重新抓取失敗之資料，請等待5秒:')
            waiting_loading_bar(5)
            print(f'第{fail_cnt}次重新嘗試抓取失敗連結，還剩{len(Failed_books_links)}筆失敗資料，請等待')
            for link in Failed_books_links[:]:  # 使用切片[:]以便在迴圈中修改原始串列
                getData_loading_bar(2,fail_book_cnt)
                fail_book_cnt = fail_book_cnt + 1
                BookData = GBD.get_book_data(link)
                if BookData != 'fail':
                    if BookData[0] == '未找到資料':
                        print(ANSI_string('資料未正確抓取',color='red'))
                    else:
                        print(ANSI_string('成功抓取資料',color='green') + ANSI_string(f'　{BookData}',bold=True))
                        titles.append(BookData[0])
                        ISBNs.append(BookData[1])
                        authors.append(BookData[2])
                        publishs.append(BookData[3])
                        dates.append(BookData[4])
                        bookImglinks.append(BookData[5])
                        Successful_books_links.append(link)
                        Failed_books_links.remove(link)  # 從失敗連結串列中移除成功處理的連結
                else:
                    print(ANSI_string(f'連結失敗：{link}',color='red'))
            fail_cnt = fail_cnt+1
            print("<====================================================>")
        print("此頁資料全部抓取完畢!")
        
        df = pd.DataFrame({'書名': titles, '書本封面':bookImglinks, 'ISBN': ISBNs, '作者':authors, '出版社':publishs,'出版日期':dates, '書本連結': Successful_books_links})
        return df
    else:
        print(ANSI_string("連接失敗",color='red'))
        
        
