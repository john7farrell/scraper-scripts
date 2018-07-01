# coding: utf-8
import os
import re
import sys
import time
import json
import requests
import urllib
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

def nest_print(dict_item, inline=True, indent=True):
        s = []
        s_ind = '\t' if indent else ''
        for k, v in dict_item.items():
            s += [': '.join([k, str(v)])]
        if inline:
            print(s_ind+' '.join(s))
        else:
            print(s_ind+'\n'.join(s))
            
def print_info(gallery):
    keys = [
        'id', 'media_id', 'title', 
        'tags', 
        'num_pages', 'num_favorites', 
        'upload_date', 'scanlator'
    ]
    for k in keys:
        if isinstance(gallery[k], dict):
            print(k)
            nest_print(gallery[k])
        elif isinstance(gallery[k], list):
            print(k, 'items:\n')
            for ck in gallery[k]:
                if isinstance(ck, dict):
                    nest_print(ck)
                else:
                    print(ck)
        else:
            print(k, gallery[k])

def get_data(src):
    return urllib.request.urlopen(src)

def get_save_img(img_url, path):
    if not os.path.isdir(path):
        os.makedirs((path))
        print("Directory %s was created." %path)
    data = get_data(img_url).read()
    fname = img_url.split('/')[-1]
    with open(path+fname, 'wb') as to_write:
        to_write.write(data)

def scrape_once(code, parent_dir, random_sleep):

    #code = 214001
    #parent_dir = 'D:\\DL\\'
    #random_sleep = True
    base_url='https://nhentai.net/g/{}/'
    ret = requests.get(base_url.format(code))
    soup = BeautifulSoup(ret.content, "lxml")
    gallery = eval(soup.text.split('var gallery = new N.gallery(')[-1].split(');')[0])
    gallery['upload_date'] = pd.to_datetime('1970-01-01')+pd.Timedelta(gallery['upload_date'], 's')
    gallery['upload_date'] = str(gallery['upload_date'])
    print('\nInfo\n')
    print_info(gallery)
    path = os.path.join(parent_dir, '{}\\'.format(gallery['title']['japanese']))
    assert not os.path.isdir(path), 'Save dir existed!'
    os.makedirs(path)
    with open(path+'gallery.json', 'w') as outfile:
        json.dump(gallery, outfile)
    print(f'Gallery json saved at {path}gallery.json !')
    num_pages = gallery['num_pages']
    media_id = gallery['media_id']
    ext_li = ['jpg', 'png', 'jpeg', 'bmp', 'JPG', 'JPEG', 'PNG', 'BMP']
    ext = None
    for pi in range(num_pages):
        img_id = pi+1
        if ext is None:
            for ext in ext_li:
                try:
                    img_url = f'https://i.nhentai.net/galleries/{media_id}/{img_id}.{ext}'
                    get_save_img(img_url, path)
                    break
                except urllib.error.HTTPError:
                    continue
        else:
            img_url = f'https://i.nhentai.net/galleries/{media_id}/{img_id}.{ext}'
            get_save_img(img_url, path)
        print(f'{img_id} out of {num_pages} pages saved!')
        if random_sleep:
            to_sleep = float(np.random.rand())/5
            time.sleep(to_sleep)
            #print('...\n\t[Slept', to_sleep, 'seconds]\n...')
    print(f'\n\tCode {code} Completed!\n')

if __name__ == "__main__":
    
    print(sys.argv)
    
    if len(sys.argv)==1 or not os.path.isdir(sys.argv[1]):
        sys.argv = [sys.argv[0]] + ['.'] + sys.argv[1:]
    
    if len(sys.argv)==2:
        sys.argv.append('214001')

    #parent_dir = 'D:\\DL\\'
    parent_dir = sys.argv[1]
    code_list = sys.argv[2:] 

    print(f'code_list: {code_list}')
    print(f'parent_dir: {parent_dir}')
    print('\nStart!\n')
    
    random_sleep = True

    for code in code_list:
        scrape_once(code, parent_dir, random_sleep)
        #print(code)
