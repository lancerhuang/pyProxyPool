from io import StringIO
import bs4
import pytesseract
import requests
from PIL import Image
import os
from proxyOnWeb import proxyOnWeb

class proxyOnMivip(proxyOnWeb):
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
    def getProxyList(self):
        url = 'https://proxy.mimvp.com/free.php?proxy=in_hp'
        page = requests.get(url)
        soup = bs4.BeautifulSoup(page.text, 'lxml')
        
        ip_list = self.__grabIpFromMimvp(soup)
        port_list = self.__grabPortFromMimvp(url, soup)
        protocol_list = self.__grabProtocolFromMimvp(soup)

        proxies_list = []
        for i in range(0,len(ip_list) - 1):
            proxies_list.append( protocol_list[i] + '://' + ip_list[i] + ':' + port_list[i] )

        return proxies_list

if __name__ == '__main__':
    aProxy = proxyOnMivip()
    print(aProxy.getProxyList())