'''
Author: 
	Unknown. From: https://pastebin.com/QhdEAHK4
Arranged(->Python 3 availability) by 
	Johnfarrell
	
Scrapes a gallery from E-Hentai when provided with the URL of the gallery.
Execute with a command like the following at a command prompt:

python ehscrape.py -i http://g.e-hentai.org/g/gallery/url/ like:
	> python ehscrape.py -i https://e-hentai.org/g/1101107/cac7c8c713/ 

For more information:

python ehscrape.py -h

Requires you to have BeautifulSoup installed. Google it.
'''

from bs4 import BeautifulSoup
import time
import urllib
import os
import os.path
import re
import argparse
import sys

# python ehscrape.py -i https://e-hentai.org/g/1101107/cac7c8c713/ 
# default url: https://e-hentai.org/g/1101107/cac7c8c713/ for 

HEADERS = {
    'User-Agent' : 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.11 (KHTML, like Gecko) Ubuntu/11.10 Chromium/17.0.963.79 Chrome/17.0.963.79 Safari/535.11'
}

def get_opened_request(url):
    req = urllib.request.Request(url+'?nw=session', headers=HEADERS)
    req_open = urllib.request.urlopen(req)
    return req_open

def main():
    '''Scrapes a gallery from its front page'''
    parser = argparse.ArgumentParser(description='ehscrape parser')
    parser.add_argument('-o', '--output', action='store', default=False,
                        help='Set an output directory manually')
    parser.add_argument('-i', '--input', action='store', default='https://e-hentai.org/g/1101107/cac7c8c713/',
                        help='Provide a link to the gallery\'s page')
    parser.add_argument('-r', '--recover', action='store', default=0,
                        help='Provide an image number to start from')
    parser.add_argument('-u', '--update', action='store_true', default=False,
                        help="Useful for updating galleries, ignores files \
                        whose names are already present.") 
    args = parser.parse_args()
    fp = get_opened_request(args.input)
    print(fp.geturl())
    with open('temp', 'wb') as temp:
        temp.write(fp.read())
    with open('temp', 'rb') as temp:
        soup = BeautifulSoup(temp, "lxml")
    os.remove('temp')
    title = soup.find(name='h1', attrs={'id': 'gn'}).string
    print(title)
    myre = re.compile('Showing\s\d\s-\s\d+\sof\s(?P<number>\d+)\simages')
    imgno = int(myre.match(soup.find(text=myre)).group('number'))
    num_per_page = 40
    d, r = imgno // num_per_page, imgno % num_per_page
    if r:
        pageno = d + 1
    else:
        pageno = d
    if args.output:
        outd = args.output
    else:
        outd = u''.join(title.split('/'))
    if os.path.isdir(outd):
        print(u'The directory {0} already exists.'.format(outd))
        r = input(u'Continue? [y/n]')
        if r in ['y', 'Y', '']:
            curfiles = os.listdir(outd)
        else:
            print('ehscrape aborting.')
            sys.exit()
    else:
        os.mkdir(outd)
    img_pages = []
    for i in range(pageno):
        time.sleep(0.03)
        url = '{0}?p={1}'.format(args.input, str(i))
        page = get_opened_request(url)
        dir_temp = os.path.join(outd, 'temp')
        with open(dir_temp,'wb') as temp:
            temp.write(page.read())
        with open(dir_temp,'rb') as temp:
            soup = BeautifulSoup(temp, "lxml")
        os.remove(dir_temp)
        are = re.compile('\d{6}-\d+')
        are_res = soup.findAll(name='a', attrs={'href': are})
        for a in are_res:
            img_pages.append(a['href'])
    if args.recover:
        args.recover = int(args.recover) - 1
    for ip in img_pages[int(args.recover):]:
        print(ip)
        page = get_opened_request(ip)
        dir_temp = os.path.join(outd, 'temp')
        with open(dir_temp,'wb') as temp:
            temp.write(page.read())
        time.sleep(0.04)
        with open(dir_temp,'rb') as temp:
            soup = BeautifulSoup(temp, "lxml")
        os.remove(dir_temp)
        stre = re.compile(r'(height:\d+px|width:\d+px);(height:\d+px|width:\d+px)')
        srre = re.compile('http://\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}:?\d{1,5}?(/h|/ehg)/\S*(/keystamp)?=\S*')
        imgs = soup.findAll(name='img', attrs={'style':stre, 'src': srre})
        for each in imgs:
            source = get_opened_request(each['src'])
            if 'keystamp' in each['src']:
                filename = each['src'].split('/')[-1]
            elif 'image.php' in each['src']:
                filename = each['src'].split('&n=')[-1]
        if args.update:
            if filename in curfiles:
                print('{0} already present'.format(filename))
            else:
                print(filename)
                with open(os.path.join(outd, filename), 'wb') as image:
                    image.write(source.read())
        else:
            print(filename)
            with open(os.path.join(outd, filename), 'wb') as image:
                image.write(source.read())
        
if __name__ == '__main__':
    main()
