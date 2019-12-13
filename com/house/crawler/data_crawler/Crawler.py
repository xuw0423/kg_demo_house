# -*- coding: utf-8 -*-
from requests_html import HTMLSession
import csv
import time
import os

session = HTMLSession()


region_base_url = "https://bj.58.com/chuzu"
subway_base_url = "https://bj.58.com/chuzu/sub/"
community_base_url = "https://bj.58.com/xiaoqu/"
house_base_url = "https://bj.58.com/chuzu/"

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
        csv_writer.writerow(('region_name', 'town_name', 'street_name', 'region_url'))
        for region in all_region[1:]:
            region_url = region.attrs.get('href', '-')
            region_name = region.text
            print(region_name, region_url)
            time.sleep(2)  #
            towns = get_town(region_url)
            for town in towns:
                town_name = town.text
                print(region_name, town_name, region_url)
                csv_writer.writerow((region_name, town_name, '-', region_url))


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
    """
    获取地铁线路以及地铁站数据
    :param url:
    :return:
    """
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
        :param subway_url:
        :return:
    """
    response = session.get(subway_url)
    response.html.render()
    response.encoding = 'utf-8'
    stations = response.html.find('div#sub_one a')
    return stations[1:]


# 地铁线路
all_subway_names = ['1号线', '2号线', '3号线', '4号线', '5号线', '6号线', '7号线', '8号线', '9号线', '10号线', '13号线', '14号线(东)',
                    '14号线(西)', '15号线', '16号线', 'S1线', '八通线', '昌平线', '房山线', '机场线', '西郊线', '亦庄线', '燕房线', '8号线南段', '大兴机场线']


def get_community_region_url(url):
    response = session.get(url)
    response.html.render()
    response.encoding = 'utf-8'
    region_values = response.html.find('dl.secitem dd a')
    for region_value in region_values[1:2]:
        region_value.attrs.get('value').strip()
        get_community_by_region(os.path.join(url, str(region_value.attrs.get('value').strip())))


def get_community_by_region(url):
    """
    获取小区的数据
    :param url:
    :return:
    """
    with open(community_file_name, 'w+', newline='', encoding='utf-8-sig') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(('community_name', 'region_name', 'town_name', 'detail_address', 'subway_name',
                             'subway_station', 'subway_distance', 'completion_date_year', 'location_with_center'))
        for page_index in range(1, 71):
            time.sleep(2)
            print(url + '/pn_' + str(page_index))
            response = session.get(url + '/pn_' + str(page_index))
            response.html.render()
            response.encoding = 'utf-8'
            community_list = response.html.find('ul.xq-list-wrap li')
            for community in community_list:
                list_info = community.find('div.list-info')[0]  # 找到小区信息所在的div
                community_name = list_info.find('h2 a')[0].text.strip('&nbsp;').strip()
                base_info_list = list_info.find('p')
                position_info = base_info_list[0].find('span')  # 小区位置信息
                region_name = position_info[0].text.strip()  # 位于那个城区
                town_name = position_info[1].text.strip('/').strip()  # 位于哪个城镇
                detail_address = position_info[2].text.strip('/').strip()  # 详细地址
                # 小区附近地铁的信息
                if len(position_info) > 3:
                    subway_info = position_info[3].text.strip(',').strip()
                    #     ", 距离地铁15号线关庄站171米"
                    for subway in all_subway_names:
                        if subway_info.find(subway) >= 0:
                            subway_name = subway  # 地铁线路
                            subway_station_start_index = subway_info.index(subway_name[-1]) + 1
                            subway_station_end_index = subway_info.index('站')
                            subway_station = subway_info[subway_station_start_index:subway_station_end_index]  # 地铁站
                            subway_distance = subway_info[subway_station_end_index + 1:-1]  # 与地铁站的距离
                # 竣工年份
                if len(base_info_list) > 1:
                    completion_date_year_area = base_info_list[1].find('span span.baseinfo-content')
                if completion_date_year_area is not None and len(completion_date_year_area) > 0:
                    completion_date_year = completion_date_year_area[0].text.strip()[:-1]
                # 与市中心的位置  例如：四五环之间
                location_with_center = list_info.find('div.tabinfo i')[-1].find('i')[0].text.strip()
                print(community_name, region_name, town_name, detail_address, subway_name, subway_station, subway_distance, completion_date_year, location_with_center)
                # 写入csv文件
                csv_writer.writerow((community_name, region_name, town_name, detail_address, subway_name,
                                     subway_station, subway_distance, completion_date_year, location_with_center))


def get_house_by_region(url):
    with open(house_file_name, 'w', newline='', encoding='utf-8-sig') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(('community_name', 'region_name', 'town_name', 'detail_address', 'subway_name',
                             'subway_station', 'subway_distance', 'completion_date_year', 'location_with_center'))


def get_house_region_url(url):
    response = session.get(url)
    response.html.render()
    response.encoding = 'utf-8'
    region_values = response.html.find('dl.search_bd', first=True)
    for region_value in region_values[1:]:
        house_region_url = region_value.attrs.get('href').strip()
        get_house_by_region(house_region_url)


if __name__ == '__main__':
    # get_region(region_base_url)
    # get_subway(subway_base_url)
    # get_community(community_base_url)
    # temp = ", 距离地铁15号线关庄站171米".strip(',').strip()
    # index = temp.index('站')
    # mile = temp[index + 1:-1]
    # print("mile:", mile)
    # print("temp", temp[4:index])
    get_community_region_url(community_base_url)
