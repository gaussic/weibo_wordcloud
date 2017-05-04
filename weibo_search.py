import json
import re
from functools import reduce

import jieba.analyse
import matplotlib as mpl
import requests
from scipy.misc import imread
from wordcloud import WordCloud, ImageColorGenerator
from PIL import Image
import numpy as np

mpl.use('TkAgg')
import matplotlib.pyplot as plt

url_template = 'http://m.weibo.cn/api/container/getIndex?type=wb&queryVal={}&containerid=100103type=2%26q%3D{}&page={}'


def read_cookie(cookie_path):
    cookie_str = open(cookie_path, 'r', encoding='utf-8').readlines()
    cookie = {}
    for line in cookie_str:
        values = line.strip().split('=')
        cookie[values[0]] = values[1]
    return cookie


def clean_text(text):
    dr = re.compile(r'(<)[^>]+>', re.S)
    dd = dr.sub('', text)
    dr = re.compile(r'#[^#]+#', re.S)
    dd = dr.sub('', dd)
    dr = re.compile(r'@[^ ]+ ', re.S)
    dd = dr.sub('', dd)
    return dd


def fetch_page_generator(queryVal, pagenum):
    cookie = read_cookie('cookie.txt')
    session = requests.Session()
    for page in range(1, pagenum + 1):
        try:
            resp = session.get(url_template.format(queryVal, queryVal, page), cookies=cookie)
            json_data = json.loads(resp.text)
            i = 0
            while json_data['ok'] == 0:
                print(resp.url)
                resp = session.get(url_template.format(queryVal, queryVal, page), cookies=cookie)
                json_data = json.loads(resp.text)
                i += 1
                if i >= 10:
                    break

            mblogs = []
            card_grouop = json_data['cards'][0]['card_group']
            for card in card_grouop:
                mblog = card['mblog']
                blog = {'id': mblog['id'],
                        'text': clean_text(mblog['text']),
                        'userid': mblog['user']['id'],
                        'username': mblog['user']['screen_name'],
                        'reposts_count': mblog['reposts_count'],
                        'comments_count': mblog['comments_count'],
                        'attitudes_count': mblog['attitudes_count']
                        }
                mblogs.append(blog)

            yield mblogs
        except Exception as e:
            yield []


def keywords(mblogs):
    text = []
    for blog in mblogs:
        keyword = jieba.analyse.extract_tags(blog['text'])
        text.extend(keyword)
    return text


def gen_img(texts, img_file):
    data = ' '.join(text for text in texts)
    image_coloring = imread(img_file)
    wc = WordCloud(
        background_color='white',
        mask=image_coloring,
        font_path='/Library/Fonts/STHeiti Light.ttc'
    )
    wc.generate(data)

    plt.figure()
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.show()

    wc.to_file(img_file.split('.')[0] + '_wc.png')


if __name__ == '__main__':
    mblogs = []
    page_generator = fetch_page_generator('苹果', 200)
    for pg in page_generator:
        mblogs.extend(pg)
    print(len(mblogs))
    for i in range(len(mblogs) - 1):
        for j in range(i + 1, len(mblogs)):
            if i != j and mblogs[i]['id'] == mblogs[j]['id']:
                print(i, j)
                print(mblogs[i]['text'])
                print(mblogs[j]['text'])

    func = lambda x, y: x if y in x else x + [y]
    mblogs = reduce(func, [[], ] + mblogs)
    print(len(mblogs))
    text = keywords(mblogs)
    gen_img(text, 'apple.png')
