from io import StringIO

import bs4
import pytesseract
import requests
from PIL import Image
import os
import datetime
import csv
import random
from proxyOnWeb import proxyOnWeb
from Mivip import proxyOnMivip

# 访问免费代理获取列表

# 测试代理，移除无法使用的代理

class ProxyPool:
    proxies = [] # 包含速度，格式类似 [{"proxy":proxy1, "param":speed1},{"proxy":proxy2, "param:speed2},...]
                 # 速度单位是毫秒(ms)
    proxy_file = 'proxy_list.txt'

    # 读取文件中的代理列表
    def loadProxies(self):
        if not os.path.exists(self.proxy_file):
            return
        with open(self.proxy_file,'r') as f:
            reader = csv.reader(f)
            for line in reader:
                if line != []:
                    proxy_dict = {}
                    proxy_dict[line[0]] = line[1]
                    self.proxies.append(proxy_dict)

    # self.proxies中的代理列表保存到文件中
    def saveProxies(self):
        with open(self.proxy_file, 'w') as f:
            writer = csv.writer(f)
            for proxy in self.proxies:
                for key,value in proxy.items():
                    writer.writerow([key,value])

    def importProxyListFromWeb(self, proxyObject):
        proxy_list = proxyObject.getProxyList()
        for proxy in proxy_list:
            proxy_info = {}
            if proxy not in self.proxies:
                proxy_info[proxy]='N/A' #新导入的代理，未测速，设定为'N/A'
                self.proxies.append(proxy_info)
                

    def printProxies(self):
        for proxy_info in self.proxies:
            for k in proxy_info:
                print(k,'\t',proxy_info[k])

    def getSpeed(self, proxy_info):
        for k,v in proxy_info.items():
            return float(v)
        

    def sortProxies(self):
        duplicate_proxy_list = sorted(self.proxies, key=self.getSpeed )
        self.proxies = duplicate_proxy_list


    # Test if the proxy in proxy list is good
    # If not, REMOVE IT!
    def varifyProxies(self):
        fail_list = []
        # Test
        for proxy_info in self.proxies:
            for proxy in proxy_info:
                param_proxy = {}
                if 'http://' in proxy:
                    param_proxy = {'http':proxy}
                else:
                    param_proxy = {'https':proxy}
                try:
                    start_time = datetime.datetime.now()
                    requests.get('http://www.baidu.com', proxies = param_proxy, timeout = 5)
                    end_time = datetime.datetime.now()
                    duration = (end_time - start_time).seconds * 1000 + (float)((end_time - start_time).microseconds/1000)
                    proxy_info[proxy] = duration
                except:
                    # PROXY FAIL
                    fail_list.append(proxy_info)
        # Remove failed proxies
        for proxy_info in fail_list:
            self.proxies.remove( proxy_info )

    def getFastestProxy(self):
        self.sortProxies()
        return self.proxies[0]
    
    def getRandomProxy(self):
        return self.proxies[random.randint(0,len(self.proxies) - 1)]

    def getFastestProxyParam(self):
        proxy = self.getFastestProxy()
        for k in proxy:
            if 'https' in k:
                return {'https':k}
            else:
                return {'http':k}
        
    def getRandomProxyParam(self):
        proxy = self.getRandomProxy()
        for k in proxy:
            if 'https' in k:
                return {'https':k}
            else:
                return {'http':k}
        

if __name__ == '__main__':
    aPool = ProxyPool()
    aPool.loadProxies()
    aProxy = proxyOnMivip()
    aPool.importProxyListFromWeb(aProxy)

    aPool.printProxies()
    aPool.varifyProxies()
    aPool.sortProxies()
    aPool.printProxies()

    print(aPool.getFastestProxyParam())
    print(aPool.getRandomProxyParam())
    print(aPool.getRandomProxyParam())