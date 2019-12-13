# -*- coding: utf-8 -*-
from requests_html import HTMLSession
import csv
import time


session = HTMLSession()

region_base_url = "https://bj.58.com/chuzu/?pagetype=area&PGTID=0d3090a7-0047-6061-e703-c01b27c553e9&ClickID=2"
subway_base_url = "https://bj.58.com/chuzu/sub/?pagetype=ditie&PGTID=0d3090a7-0047-7e25-7e62-9767be294185&ClickID=2"


# 小区存储的文件名
community_file_name = '../data/community.csv'
# 地区数据存储的文件名
region_file_name = '../data/region.csv'
# 地铁站数据存储的文件名
subway_file_name = '../data/subway.csv'
# 房源数据存储的文件名
house_file_name = '../data/house.csv'


def get_region(url):
    """
    获取地区数据
    :param url:
    :return:
    """
    response = session.get(url)
    response.html.render()
    response.encoding = 'utf-8'
    temp = response.html.find('div.search_bd dl', first=True)
    all_region = temp.find('dd a')
    with open(region_file_name, 'w', newline='', encoding='utf-8-sig') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(('region_name', 'town_name', 'street_name'))
        i = 0
        for region in all_region:
            i+=1
            # 第一个是无效链接，须过滤掉
            if i == 1:
                continue
            region_url = region.attrs.get('href', '-')
            region_name = region.text
            print(region_name,region_url)
            time.sleep(5)   #
            towns = get_town(region_url)
            for town in towns:
                town_name = town.text
                print(region_name, town_name)
                csv_writer.writerow((region_name, town_name))


def get_town(region_url):
    """
    从给定的url中获取每个区对应的镇
    :param url:
    :return:
    """
    response = session.get(region_url)
    response.html.render()
    response.encoding = 'utf-8'
    towns = response.html.find('div.arealist a')
    return towns


def get_subway(url):
    response = session.get(url)
    response.html.render()
    response.encoding = 'utf-8'
    temp = response.html.find('div.search_bd dl', first=True)
    subways = temp.find('dd a')
    with open(subway_file_name, 'w', newline='', encoding='utf-8-sig') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(('subway_name', 'subway_station'))
        for subway in subways[1:]:
            subway_url = subway.attrs.get('href', '-')
            subway_name = subway.text
            print(subway_name, subway_url)
            time.sleep(5)  #
            stations = get_subway_station(subway_url)
            for station in stations:
                station_name = station.text
                print(subway_name, station_name)
                csv_writer.writerow((subway_name, station_name))


def get_subway_station(subway_url):
    """
        从给定的url中获取每条地铁线路对应的地铁站
        :param url:
        :return:
    """
    response = session.get(subway_url)
    response.html.render()
    response.encoding = 'utf-8'
    stations = response.html.find('div#sub_one a')
    return stations[1:]


if __name__ == '__main__':
    # get_region(region_base_url)
    get_subway(subway_base_url)