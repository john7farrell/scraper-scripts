# coding: utf-8
'''
Author: Johnfarrell
Usage:
  pip install -r requirements.txt
  #modify `code` variable in the script  
  python yahoo-finance-scraper.py
  
requirements:
  requests==2.18.4
  lxml==4.2.1
  numpy==1.14.3
  pandas==0.23.0
  beautifulsoup4==4.6.0
'''

import re
import time
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

def make_query(stock_code, start_date, end_date=None, time_mode='day'):
    """
    Example: 
    stock_code(int): 6758 
    start_date(str): '2018, 06, 13' or '20180613' or '2018-06-13'
    end_date(str): None -> same as start_date
    time_mode(str): 'day'(Default), 'week', 'month', 'd', 'w', 'm'
    Return:
    query(dict)
    """
    mode_map = {'day': 'd', 'd': 'd',
                'week': 'w', 'w': 'w',
                'month': 'm', 'm': 'm'}
    assert time_mode.lower() in mode_map.keys()
    query = {}
    query['code'] = '{}.T'.format(stock_code)
    start_date = pd.to_datetime(start_date)
    if end_date is not None:
        end_date = pd.to_datetime(end_date)
    else:
        end_date = start_date
    query['sy'] = start_date.year
    query['sm'] = start_date.month
    query['sd'] = start_date.day
    query['ey'] = end_date.year
    query['em'] = end_date.month
    query['ed'] = end_date.day
    query['tm'] = mode_map[time_mode.lower()]
    return query

def parse_page_info(page_info):
    page_numbers = re.findall(r"[0-9]+", page_info)
    if len(page_numbers)<3:
        total_pages = 1
    elif len(page_numbers)==3:
        page_numbers = list(map(int, page_numbers))
        current_page_start, current_page_end, total_page_end = page_numbers
        if current_page_end==total_page_end:
            total_pages = 1
        else:
            intervals = 1+current_page_end-current_page_start
            total_pages = total_page_end//intervals
            if total_page_end%intervals!=0:
                total_pages = total_pages+1
    else:
        print('Parsing pages failed?', page_numbers)
        return None
    return total_pages

def parse_stock_table(stocktable):
    symbol = stocktable.findAll('th')
    columns = [s.text for s in symbol]
    symbol = stocktable.findAll('td')
    entries = [s.text.replace(',', '') for s in symbol]
    entry_arr = np.array(entries).reshape(-1, len(columns))
    def str_to_number(x):
        try:
            res = float(x)
            return res
        except ValueError:
            print('Not a valid number:', x)
            return np.nan
    entry_df = pd.DataFrame(entry_arr, columns=columns)
    entry_df = entry_df.set_index(columns[0])
    for c in entry_df.columns:
        entry_df[c] = entry_df[c].apply(str_to_number)
    return entry_df

def get_stock_data(query, 
                   random_sleep=True,
                   base_url="https://info.finance.yahoo.co.jp/history/"):
    ret = requests.get(base_url, params=query)
    soup = BeautifulSoup(ret.content, "lxml")
    nomatch = soup.find('div', {'class':'stocksHistoryCode nomatch'})
    if nomatch is not None:
        print('No Match!', nomatch.text)
        return None
    page_info = soup.find('span', {'class': 'stocksHistoryPageing yjS'})
    page_info = page_info.text
    print('[Page Info]', page_info)
    total_pages = parse_page_info(page_info)
    data_all = []
    for idx in range(total_pages):
        print('[Page {}/{}]'.format(idx+1, total_pages))
        if idx>0:
            if random_sleep:
                to_sleep = float(np.random.rand())/2
                time.sleep(to_sleep)
                print('...\n\t[Slept', to_sleep, 'seconds]\n...')
            query.update({'p': idx+1})
            ret = requests.get(base_url, params=query)
            soup = BeautifulSoup(ret.content, "lxml")
        stocktable =  soup.find('table', {'class':'boardFin yjSt marB6'})
        if stocktable is None:
            print('Unexpeted Error! Empty stock table!')
            return None
        print('[Get stock table] succeeded!')
        df = parse_stock_table(stocktable)
        data_all.append(df)
    print('\nAll Finished!')
    return pd.concat(data_all, axis=0).reset_index()

if __name__ == "__main__":
	code = 6758 #SONY
	start_date = '2017-12-01'
	end_date = pd.datetime.now().strftime('%Y-%m-%d')
	#end_date = '2018-04-01'
	time_mode = 'day' #d, w, m
	
	data = get_stock_data(make_query(code, start_date, end_date, time_mode))
	
	save_name = '{}_{}_{}_{}.csv'.format(code, start_date, end_date, time_mode)
	data.to_csv(save_name, index=False, encoding='utf-8')
	print('Data saved at', save_name)

