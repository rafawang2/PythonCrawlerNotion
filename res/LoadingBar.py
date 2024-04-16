import time
import sys

def ANSI_string(s, color=None, background=None, bold=False):
    colors = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m'
    }
    
    background_colors = {
        'black': '\033[40m',
        'red': '\033[41m',
        'green': '\033[42m',
        'yellow': '\033[43m',
        'blue': '\033[44m',
        'magenta': '\033[45m',
        'cyan': '\033[46m',
        'white': '\033[47m',
        'reset': '\033[0m'
    }
    
    styles = {
        'bold': '\033[1m',
        'reset': '\033[0m'
    }
    color_code = colors[color] if color in colors else ''
    background_code = background_colors[background] if background in colors else ''
    bold_code = styles['bold'] if bold else ''

    return f"{color_code}{background_code}{bold_code}{s}{styles['reset']}"

def getData_loading_bar(duration, k):
    total_ticks = 20
    for i in range(total_ticks + 1):
        if i == total_ticks:
            progress = ANSI_string('[',bold=True) + ANSI_string('=',color='cyan') * total_ticks + ANSI_string('=',color='cyan') + ANSI_string(']',bold=True)
        else:
            progress = ANSI_string('[',bold=True) + ANSI_string('=',color='blue') * i + ANSI_string('>',color='blue') + ' ' * (total_ticks - i) + ANSI_string(']',bold=True)
        sys.stdout.write('\r' + progress + f' 抓取第{k}筆資料中，請等待' + '.' * (i % 4) + ' ' * (4 - i % 4))
        sys.stdout.flush()
        time.sleep(duration / total_ticks)
    sys.stdout.write('\n')

def waiting_loading_bar(duration):
    total_ticks = duration
    for i in range(total_ticks + 1):
        if(i==total_ticks):
            sys.stdout.write('\r' + ANSI_string(f'等待完畢，開始執行下一步',bold=True))
            sys.stdout.flush()
        else:    
            sys.stdout.write('\r' + ANSI_string(f'請等待{duration-i}秒',bold=True) + '.' * (i % 4) + ' ' * (4 - i % 4))
            sys.stdout.flush()
            time.sleep((duration / total_ticks))
    sys.stdout.write('\n')


# import time   #覆蓋上一行

# # 打印第一行
# print('hi')

# # 将光标移动到上一行的开头
# print('\033[F', end='', flush=True)

# # 打印覆盖内容
# print('hi_cover', end='', flush=True)

# # 模拟一些操作
# time.sleep(2)

import sys
import time

def dynamic_loading_bar(data_list):
    total_items = len(data_list)
    while data_list:
        completed_items = total_items - len(data_list) +1
        progress_percentage = int((completed_items / total_items) * 100)
        progress = '[' + '=' * (progress_percentage // 5) + ' ' * (20 - progress_percentage // 5) + ']'
        sys.stdout.write('\r' + progress)
        sys.stdout.flush()
        
        # 模擬處理每個元素的時間
        time.sleep(0.5)
        
        # 處理完畢後移除第一個元素
        data_list.pop(0)
    
    sys.stdout.write('\n')

# 假設你有一個列表需要處理
# my_list = list(range(30)) 
# dynamic_loading_bar(my_list)
