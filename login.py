import requests
import time
from bs4 import BeautifulSoup
import execjs


def splitUrl(url):
    [host, paramStr] = url.split("?")
    paramList = paramStr.split("&")
    paramDict = {}
    for p in paramList:
        key, value = p.split("=")
        paramDict[key] = value
    return host, paramDict

def login(username,password):
    loginUrl="http://authserver.cqu.edu.cn/authserver/login"
    session=requests.Session()
    #设置访问头
    session.headers={
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Host": "authserver.cqu.edu.cn",
        "Proxy-Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36"
    }
    #获取加密的第二个参数
    res=session.get(loginUrl, params={
        "service": "http://my.cqu.edu.cn/authserver/authentication/cas"
    })

    
    keystr="pwdDefaultEncryptSalt = \""
    startPos=res.text.find(keystr)+len(keystr)
    endPos=res.text.find("\"",startPos)
    aeskey=res.text[startPos:endPos]
    soup=BeautifulSoup(res.text,'html.parser')
    #加密
    def AES(password,aeskey):
        with open("AES.js",'r',encoding='utf-8') as f :
            pwdcl = execjs.compile(f.read())
            ans = pwdcl.call('encryptAES',password,aeskey)
            return ans

    res = session.get("http://authserver.cqu.edu.cn/authserver/needCaptcha.html",params={
        "username":username,
        "pwdEncrypt2": "pwdEncryptSalt",
        "_": "{}".format(int(time.time()*1000))
    })

    res = session.get("http://authserver.cqu.edu.cn/authserver/needCaptcha.html",params={
        "username":username,
        "pwdEncrypt2": "pwdEncryptSalt",
        "_": "{}".format(int(time.time()*1000))
    })

    
    data={
        "username":username,
        "password":AES(password,aeskey),
        "lt":soup.find('input',attrs={'name':'lt'}).attrs['value'],
        "dllt":"userNamePasswordLogin",
        "execution":"e1s1",
        "_eventId":"submit",
        "rmShown":1
    }

    #登录
    res=session.post(loginUrl,params={
        "service": "http://my.cqu.edu.cn/authserver/authentication/cas"
    },data=data)
    
    res = session.get("http://my.cqu.edu.cn/authserver/authentication/cas",params={
        "ticket": "ST-9837340-2wRbd1NutSvMo7Otasal1639217035122-XBvd-cas"
    })
    res = session.get("https://my.cqu.edu.cn/authserver/authentication/cas",params={
        "ticket": "ST-9837340-2wRbd1NutSvMo7Otasal1639217035122-XBvd-cas"
    })

    res = session.get("https://my.cqu.edu.cn/enroll/cas")

    params={
        "client_id": "enroll-prod",
        "response_type": "code",
        "scope": "all",
        "state": "",
        "redirect_uri": "https://my.cqu.edu.cn/enroll/token-index"
    }
    res=session.get("https://my.cqu.edu.cn/authserver/oauth/authorize",params=params)

    refer_url = res.url
    a,b = splitUrl(res.url)

    res = session.get(res.url)
    session.headers["Referer"] = refer_url
    data={
        "client_id": "enroll-prod",
        "client_secret": "app-a-1234",
        "code": b["code"],
        "redirect_uri": "https://my.cqu.edu.cn/enroll/token-index",
        "grant_type": "authorization_code"
    }

    session.headers["Authorization"]="Basic ZW5yb2xsLXByb2Q6YXBwLWEtMTIzNA=="
    url = "https://my.cqu.edu.cn/authserver/oauth/token"
    res=session.post(url,data=data)

    pos=res.text.find(":")+2
    end=res.text.find("\"",pos)
    token=res.text[pos:end]
    session.headers["Authorization"]="Bearer "+token
    res = session.get("https://my.cqu.edu.cn/enroll/Home")
    return session

