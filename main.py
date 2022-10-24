import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import math
import random
import time
from urllib.parse import quote

LIST_OF_PRODUCTS = ['cadeira gamer', 'iphone 13', 'a origem das especies']
MAX_AMZ_PAGE = 5
BASE_URL = 'https://www.amazon.com.br/s?k='

user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
    'Mozilla/5.0 (Linux; Android 11; SM-G960U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.72 Mobile Safari/537.36'
]

HEADER = {
    'method': 'GET',
    'scheme': 'https',
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'pt-BR,pt;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
    'referer': 'https://www.kabum.com.br/',
    'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': 'Windows',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'x-datadome-clientid': '.keep',
    'User-Agent': ''
}

session = requests.Session()

user_agent = random.choice(user_agents)
HEADER['User-Agent'] = user_agent

session.headers.update(HEADER)


def fetch(url):
    r = session.get(url, headers=HEADER)
    return r


def get_soup(site):
    return BeautifulSoup(site.content, 'html.parser')


def get_amz_products(product, last_page):
    dic_amz_products = {'brand': [], 'price': [], 'url': []}
    url = BASE_URL + quote(product)

    print(url)

    for page in range(1, last_page + 1):
        print(page)

        site_url = url + f'&page={page}'

        print(site_url)
        site = fetch(site_url)

        if site.status_code >= 400:
            print(site.status_code)
            break

        soup = get_soup(site)

        products = soup.findAll('div', {'class': 's-result-item', 'data-component-type': 's-search-result'})

        for product in products:
            name = product.find('h2').get_text().strip()
            dic_amz_products['brand'].append(name)

            int_price = product.find('span', class_=re.compile('a-price-whole'))
            float_price = product.find('span', class_=re.compile('a-price-fraction'))

            if int_price is not None:
                price = (int_price.get_text().strip() + float_price.get_text().strip()).strip()
                dic_amz_products['price'].append(price)
            else:
                dic_amz_products['price'].append('###')

            p_url = product.find('a', class_=re.compile('a-link-normal'))['href']
            p_url = 'https://www.amazon.com.br' + p_url
            dic_amz_products['url'].append(p_url)

        time.sleep(5)

    return dic_amz_products


def main():
    for product in LIST_OF_PRODUCTS:
        amz_products = get_amz_products(product, MAX_AMZ_PAGE)
        df = pd.DataFrame(amz_products)
        df.to_csv(f'./products/{product}.csv', encoding='utf-8', sep=';')

if __name__ == '__main__':
    main()
