#! /usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from time import sleep
from random import choice, uniform
import logging
import csv
import re

import requests
from bs4 import BeautifulSoup


def read_file(filename):
    with open(filename) as input_file:
        return input_file.read()


def get_links_one_page(one_page):
    coin_list = one_page.find_all('div', {'class': ['js-catalog_before-ads', 'js-catalog_after-ads']})
    coins = coin_list[0].find_all('div', {'class': ['item item_table clearfix js-catalog-item-enum item-highlight ',
                                                    'item item_table clearfix js-catalog-item-enum c-b-0 ']})
    coins2 = coin_list[1].find_all('div', {'class': ['item item_table clearfix js-catalog-item-enum item-highlight ',
                                                     'item item_table clearfix js-catalog-item-enum c-b-0 ']})
    coins.extend(coins2)
    coins_links = []
    for coin in coins:
        coins_links.append(
            'https://www.avito.ru' + coin.find('div', {'class': 'description item_table-description'}).find('div', {
            'class': 'item_table-header'}).find('h3').find('a').get('href'))
        write_link_csv(
            'https://www.avito.ru' + coin.find('div', {'class': 'description item_table-description'}).find('div', {
            'class': 'item_table-header'}).find('h3').find('a').get('href'))
    print 'Length is: %d' % len(coins)
    print 'Links is: %d' % len(coins_links)
    return coins_links


def get_data(url_page):
    """get data about one coin"""

    one_coin_page = requests.get(url_page)
    soup_coin_page = BeautifulSoup(one_coin_page.text, "lxml")
    coin_header = soup_coin_page.find('h1', {'class': 'title-info-title'}).text

    if soup_coin_page.find('div', {'class': 'item-description'}):
        coin_text = soup_coin_page.find('div', {'class': 'item-description'}).text
    else:
        coin_text = ''
    coin_data = {
        'coin_header': coin_header,
        'coin_text': coin_text
    }
    return coin_data


def get_html(url, user_agent=None, proxy=None):  # Get one page
    r = requests.get(url, headers=user_agent, proxies=proxy)
    return r.text


def get_ip(html):
    """function for checking proxy"""
    soup = BeautifulSoup(html, 'lxml')
    ip = soup.find('span', {'class': 'ip'}).text.strip()
    ua = soup.find('span', {'class': 'ip'}).find_next_sibling('span').text.strip()
    print ip
    print ua
    print ('________________________')


def check_proxy_and_ua(test_url, proxies, user_agents):
    for i in xrange(10):
        print 'Sleep now'
        sleep(uniform(3, 6))
        proxy = {'http': 'http://' + choice(proxies)}
        user_agent = {'User-Agent': choice(user_agents)}
        print proxy
        try:
            html = get_html(test_url, user_agent, proxy)
            print html
            get_ip(html)
        except:
            logging.warning('PROXY _ FAILED !')


def get_total_pages(html):
    soup = BeautifulSoup(html, "lxml")

    last_page_link = (soup.find('div', {'class': 'pagination-pages clearfix'})
                          .find_all('a', {'class': 'pagination-page'})[-1]
                          .get('href'))

    last_page = last_page_link.split('?p=')[1]
    return int(last_page)


def write_link_csv(data):
    with open('coin_list2.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([data])


def get_all_links(total_page, proxies, user_agents, base_url):
    coin_links = []
    for i in xrange(1, total_page + 1):
        logging.warning('Program sleep. Current page is: ' + str(i))
        sleep(uniform(3, 6))
        logging.warning('Program wake and try page')
        while True:
            try:
                proxy = {'http': 'http://' + choice(proxies)}
                user_agent = {'User-Agent': choice(user_agents)}
                html = get_html(base_url + str(i), user_agent, proxy)
                break
            except:
                logging.warning('Bad User-Agent or Proxy. Try again')
                sleep(uniform(3, 6))

        logging.warning('Program got page number: %d going parse' % i)
        soup = BeautifulSoup(html, "lxml")  # make soup from page
        one_coins_links = get_links_one_page(soup)  # get links of one coin from my first page
        logging.warning('Link has been goteen. Going next')
        coin_links.extend(one_coins_links)
    print 'Total links: %d' % len(coin_links)
    return coin_links


def read_links(file_name):
    with open(file_name, 'rb') as f:
        reader = csv.reader(f)
        your_list = list(reader)
    return your_list


def pars_coin(url_, proxys, useragents):
    html_ = None
    i = 0
    while i < 5:
        print ('Try to connect #_' + str(i))
        proxy = {'http': 'http://' + choice(proxys)}
        user_agent = {'User-Agent': choice(useragents)}
        try:
            logging.warning('Program sleep. Current page is: ' + str(url_))
            sleep(uniform(3, 6))
            html_ = get_html(url_, user_agent, proxy)
            break
        except:
            logging.warning('Bad User-Agent or Proxy. Try again')
            i += 1
            sleep(uniform(3, 6))

    if html_:
        soup = BeautifulSoup(html_, "lxml")
    else:
        url_ = None

    try:
        header = (soup.find('h1', {'class': 'title-info-title'})
                      .find('span', {'class': 'title-info-title-text'})
                      .text
                      .strip())
    except:
        header = ''

    try:
        description = soup.find('div', {'class': 'item-description'}).find('div').find_all('p')
        description2 = []
        for p in description:
            description2.extend(p.text.strip())
    except:
        description2 = ''

    try:
        price = (soup.find('div', {'class': 'item-price'})
                     .find('div', {'class': 'price-value price-value_side-card'})
                     .text.strip())
    except:
        price = ''

    coin = {
        'link': url_,
        'header': header,
        'text': ' '.join(description2),
        'price': price,
    }
    return coin


def write_to_csv(data):
    with open('result_file2.csv', 'a') as f:
        writer = csv.writer(f, delimiter=b'~')
        writer.writerow((data['link'].encode('utf-8'),
                         data['header'].encode('utf-8'),
                         data['text'].encode('utf-8'),
                         data['price'].encode('utf-8')))


def pars_all_coin_page(coin_links, proxies, user_agents):
    for count, coin in enumerate(coin_links[4255:]):
        html_ = pars_coin(coin[0], proxies, user_agents)
        if html_['link']:
            print 'Status %d from %d' % (count, len(coin_links))
            write_to_csv(html_)


def read_data_from_csv():
    reader = csv.DictReader(open('result_file2.csv', 'rb'), ['link', 'header', 'text', 'price'], delimiter=b'~')
    out = [r for r in reader]

    print 'Length of data list is %d' % len(out)

    return out


# below i will make a several result function for different type of resolve
def get_result(data):
    """First resolve ----- parsing only header"""
    no_year = []
    before_2000 = []
    after_2000 = []
    for coin in data:
        link = coin['link']
        year = re.findall(r'[1-2]{1}[0-9]{3}', coin['header'])
        if year:
            if int(year[0]) < 2000:
                before_2000.append({'link': link,
                                    'year': year[0]})
            else:
                after_2000.append({'link': link,
                                   'year': year[0]})
        else:
            no_year.append({'link': link,
                            'year': 'No year'})
    print 'First resolve ----- parsing only header'
    print 'checking total! Len is: %d' % (len(no_year) + len(before_2000) + len(after_2000))
    print 'Количество без даты: %d' % len(no_year)
    print 'Соотношение монет до 2000 и после: %d/%d=%f' % (
        len(before_2000), len(after_2000), float(len(before_2000)) / len(after_2000)
    )


def get_result_2(data):
    """Second resolve ------- parsing header and text"""
    no_year = []
    before_2000 = []
    after_2000 = []
    for coin in data:
        link = coin['link']
        year = re.findall(r'[1-2]{1}[0-9]{3}', coin['header'])
        if year:
            if int(year[0]) < 2000:
                before_2000.append({'link': link,
                                    'year': year[0]})
            else:
                after_2000.append({'link': link,
                                   'year': year[0]})
        else:
            year = re.findall(r'[1-2]{1}[0-9]{3}', coin['text'])
            if year:
                if int(year[0]) < 2000:
                    before_2000.append({'link': link,
                                        'year': year[0]})
                else:
                    after_2000.append({'link': link,
                                       'year': year[0]})
            else:
                no_year.append({'link': link,
                                'year': 'No year'})
    print 'Second resolve ------- parsing header and text'
    print 'checking total! Len is: %d' % (len(no_year) + len(before_2000) + len(after_2000))
    print 'Количество без даты: %d' % len(no_year)
    print 'Соотношение монет до 2000 и после: %d/%d=%f' % (
        len(before_2000), len(after_2000), float(len(before_2000)) / len(after_2000)
    )


def main():
    logging.warning('We are starting the program')

    with open('useragents.txt') as fd:
        user_agents = [line.strip() for line in fd if line.strip()]

    with open('proxy') as fd:
        proxies = [line.strip() for line in fd if line.strip()]

    test_url = 'http://sitespy.ru/my-ip'  #test URL for checking IP
    url = 'https://www.avito.ru/moskva/kollektsionirovanie/monety?p=1'
    base_url = 'https://www.avito.ru/moskva/kollektsionirovanie/monety?p='

    while True:
        try:
            proxy = {'http': 'http://' + choice(proxies)}
            user_agent = {'User-Agent': choice(user_agents)}
            html_init = get_html(url, user_agent, proxy)

            break
        except:
            logging.warning('Bad User-Agent or Proxy. Try again')
            sleep(uniform(3, 6))

    all_coins = get_total_pages(html_init)

    logging.info('Total page with coins: %s' % all_coins)

    # coin_links = get_all_links(all_coins, proxys, useragents, base_url) # get all links of coin and write to csv
    coin_links = read_links('coin_list.csv')
    # pars_all_coin_page(coin_links, proxys, useragents) #parse all coin from list of coins and write to csv

    data = read_data_from_csv()
    print data[0]['price']
    get_result(data)
    get_result_2(data)


if __name__ == '__main__':
    main()
