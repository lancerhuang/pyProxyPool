from io import StringIO

import bs4
import pytesseract
import requests
from PIL import Image
import os
import datetime
import csv
import random

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
        #     line = f.readline() 
        #     while line:
        #         line = line.split('\n')[0] # remove the '\n' after data

        #         data = line.split(',')
        #         proxy = data[0]
        #         speed = data[1]
        #         proxy_dict = {}
        #         proxy_dict['proxy'] = proxy
        #         proxy_dict['param'] = speed
                
        #         self.proxies.append( proxy_dict)
        #         line = f.readline()
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

    def __getDomainFromUrl(self, url):
        index = 0
        count = 1
        while( count < 4 and index != -1):
            index = url.find('/', index+1)
            count += 1
        if index == -1:
            raise Exception('URL Contain NO DOMAIN NAME!')
        domain = url[0:index+1]
        return domain
        
    def __grabIpFromMimvp(self, soup):
        ips_on_page = []
        ip_addr_list = soup.select('td.tbl-proxy-ip')

        for ip_addr in ip_addr_list:
            ips_on_page.append(ip_addr.get_text())
    
        return ips_on_page

    def __grabPortFromMimvp(self, url, soup):
        ports_on_page = []
        port_img_list = soup.select('td.tbl-proxy-port img')
        for port_img in port_img_list:
            img_relative_url = port_img.attrs['src']
            img_url = self.__getDomainFromUrl(url) + img_relative_url
            ports_on_page.append( self.__portIdentify(img_url))
        
        return ports_on_page

    def __grabProtocolFromMimvp(self, soup):
        protocols_on_page = []
        protocol_list = soup.select('td.tbl-proxy-type')

        for protocol in protocol_list:
            if 'HTTPS' in protocol.get_text():
                protocols_on_page.append('https')
            else:
                protocols_on_page.append('http')
    
        return protocols_on_page

    # Recognize the image of port number
    def __portIdentify(self,img_url):
        port_num: int = 0
        pic_res = requests.get(img_url)
        f_img = 'temp_img.png'
        with open(f_img,'wb') as f:
            f.write( pic_res.content )
        port_num = pytesseract.image_to_string(Image.open(f_img).convert('L'), config='nobatch digits')
        return port_num

    #======================#
    # 从米扑网站获取免费代理 #
    #======================#
    def importFromMimvp(self):
        url = 'https://proxy.mimvp.com/free.php?proxy=in_hp'
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.text, 'lxml')
        
        ip_list = self.__grabIpFromMimvp(soup)
        port_list = self.__grabPortFromMimvp(url, soup)
        protocol_list = self.__grabProtocolFromMimvp(soup)

        proxies_list = []
        for i in range(0,len(ip_list) - 1):
            proxy_info = {}
            proxy_info[protocol_list[i] + '://' + ip_list[i] + ':' + port_list[i]] = 'N/A' #未测速则设定为'N/A'
            proxies_list.append( proxy_info )

        self.proxies += proxies_list

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
    # aPool.importFromMimvp()
    # aPool.varifyProxies()
    # # aPool.printProxies()
    
    # print('------------------------------------------')
    # aPool.sortProxies()
    # aPool.printProxies()
    
    # aPool.saveProxies()
    # print( aPool.portIdentify('https://proxy.mimvp.com/common/ygrandimg.php?id=2&port=MmziZmtvapW12cDUzMjgx') )
    # print( aPool.getDomainFromUrl('https://proxy.mimvp.com/common/ygrandimg.php?id=2&port=MmziZmtvapW12cDUzMjgx'))
    # modification
    print(aPool.getFastestProxyParam())
    print(aPool.getRandomProxyParam())
    print(aPool.getRandomProxyParam())