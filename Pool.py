from io import StringIO

import bs4
import pytesseract
import requests
from PIL import Image
import os
# 访问免费代理获取列表

# 测试代理，移除无法使用的代理

class ProxyPool:
    proxies = set()
    proxy_file = 'proxy_list.txt'

    # 读取文件中的代理列表
    def loadProxies(self):
        if not os.path.exists(self.proxy_file):
            return
        with open(self.proxy_file,'r') as f:
            line = f.readline()
            line = line.split('\\')[0]
            self.proxies.add(line)
        
    # self.proxies中的代理列表保存到文件中
    def saveProxies(self):
        with open(self.proxy_file, 'w') as f:
            for proxy in self.proxies:
                f.write(proxy)
                f.write('\n')

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
        port_num:int = 0
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
            proxies_list.append( protocol_list[i] + '://' + ip_list[i] + ':' + port_list[i] )
        self.proxies.update( proxies_list )

    def printProxies(self):
        for ip in self.proxies:
            print(ip)

    # Test if the proxy in proxy list is good
    # If not, REMOVE IT!
    def varifyProxies(self):
        fail_list = []

        # Test
        for proxy in self.proxies:
            param_proxy = {}
            if 'http://' in proxy:
                param_proxy = {'http':proxy}
            else:
                param_proxy = {'https':proxy}
            try:
                requests.get('http://www.baidu.com', proxies = param_proxy, timeout = 5)
            except:
                # PROXY FAIL
                fail_list.append(proxy)
        
        # Remove failed proxies
        for proxy in fail_list:
            self.proxies.remove(proxy)

if __name__ == '__main__':
    aPool = ProxyPool()
    aPool.loadProxies()
    aPool.importFromMimvp()
    aPool.varifyProxies()
    aPool.saveProxies()
    # print( aPool.portIdentify('https://proxy.mimvp.com/common/ygrandimg.php?id=2&port=MmziZmtvapW12cDUzMjgx') )
    # print( aPool.getDomainFromUrl('https://proxy.mimvp.com/common/ygrandimg.php?id=2&port=MmziZmtvapW12cDUzMjgx'))
