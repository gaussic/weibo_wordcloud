import requests
import base64
import re
import urllib
import urllib.parse
import rsa
import json
import binascii
from bs4 import BeautifulSoup


class UserLogin:
    def user_login(self, username, password, pagecount):
        session = requests.session()
        url_prelogin = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=&rsakt=mod&client=ssologin.js(v1.4.5)&_=1364875106625'
        url_login = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.5)'

        resp = session.get(url_prelogin)
        json_data = re.findall(r'(?<=\().*(?=\))', resp.text)[0]
        data = json.loads(json_data)
        print(data)

        servertime = data['servertime']
        nonce = data['nonce']
        pubkey = data['pubkey']
        rsakv = data['rsakv']

        print(urllib.parse.quote(username))
        su = base64.b64encode(username.encode(encoding='utf-8'))

        rsaPublicKey = int(pubkey, 16)
        key = rsa.PublicKey(rsaPublicKey, 65537)
        message = str(servertime) + '\t' + str(nonce) + '\n' + str(password)
        sp = binascii.b2a_hex(rsa.encrypt(message.encode(encoding='utf-8'), key))
        postdata = {
            'entry': 'weibo',
            'gateway': '1',
            'from': '',
            'savestate': '7',
            'userticket': '1',
            'ssoimplelogin': '1',
            'vsnf': '1',
            'vsnval': '',
            'su': su,
            'service': 'miniblog',
            'servertime': servertime,
            'nonce': nonce,
            'pwencode': 'rsa2',
            'sp': sp,
            'encoding': 'UTF-8',
            'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
            'returntype': 'META',
            'rsalv': rsakv,
        }

        resp = session.post(url_login, data=postdata)
        print(resp.status_code)

        print(resp.content.decode('gbk'))
        login_url = re.findall(r'http://weibo.*&retcode=0', resp.text)

        print(login_url)
        respo = session.get(login_url[0])
        uid = re.findall('"uniqueid":"(\d+)",', respo.text)[0]
        url = 'http://weibo.com/u/' + uid
        print(url)
        respo = session.get(url)
        print(respo.text)

if __name__ == '__main__':
    login = UserLogin()
    login.user_login('18817392118', 'dzkang2011', 0)

