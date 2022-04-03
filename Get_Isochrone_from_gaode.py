# -*- coding: utf-8 -*-
# @Author: Bardbo
# @Date:   2020-10-24 21:29:09
# @Last Modified by:   Bardbo
# @Last Modified time: 2022-04-03 10:19:38

import requests
import json
import pandas as pd
import converter  # 坐标转换的脚本,来自于GitHub https://github.com/gaussic/geo_convert
from tqdm import tqdm


def generateCoor(left_lng, left_lat, right_lng, right_lat, m, n):
    """[1.根据传入的左下坐标和右上坐标, 将围成的矩形划分为m行n列, 返回网格交点的坐标;
        2.此处使用遍历方式产生，读者也可以使用小旭学长视频中的传入小区id的方式产生;
        3.左下、右上的坐标可以使用坐标拾取器拾取，如高德坐标拾取器]

    Args:
        left_lng ([float]): [矩形空间范围左下角的经度坐标]
        left_lat ([float]): [矩形空间范围左下角的纬度坐标]
        right_lng ([float]): [矩形空间范围右上角的经度坐标]
        right_lat ([float]): [矩形空间范围右上角的纬度坐标]
        m ([int]): [行数]
        n ([int]): [列数]

    Returns:
        [list]: [列表中为元组形式的经纬度坐标，矩形网格交点的坐标]
    """
    coor_ls = []
    for i in range(m + 1):
        lat = left_lat + i * (right_lat - left_lat) / m
        lat = round(lat, 6)
        for j in range(n + 1):
            lng = left_lng + j * (right_lng - left_lng) / n
            lng = round(lng, 6)
            coor_ls.append((lng, lat))
    return coor_ls


class GetTripTime:
    def __init__(self,
                 method,
                 center_coor,
                 r=0.18,
                 m=5,
                 n=5,
                 key='47e9cf07fca900b056abf416d6e3b155'):
        """[未使用批量请求接口，未使用多线程，建议更换自己的高德开放平台webAPI key]
        
        Args:
            method ([str]): [出行方式，不同出行方式的请求网址不同，walking、driving、transit、bicycling]
            center_coor ([list or tuple]): [等时圈中心点的经纬度坐标, GCJ02 高德坐标系]
            r (float, optional): [矩形范围的半径，单位为度数]. Defaults to 0.18.
            m (int, optional): [矩形范围划分成m行]. Defaults to 20.
            n (int, optional): [矩形范围划分成n列]. Defaults to 20.
            key (str, optional): [高德webAPIkey，需要注册开发者账号然后申请，建议使用自己的key]
        """
        print('**正在初始化**')
        self.method = method
        self.center_coor = center_coor
        self.r = r
        self.m = m
        self.n = n
        self.key = key

        self.get_coor_ls()
        if self.method == 'walking':
            self.get_time = self.get_walking_time
        elif self.method == 'transit':
            self.get_time = self.get_transit_time
        elif self.method == 'driving':
            self.get_time = self.get_driving_time
        elif self.method == 'bicycling':
            self.get_time = self.get_bicycling_time
        else:
            raise '不支持该种出行方式！请从walking、driving、transit、bicycling中选择'

    def get_coor_ls(self):
        left = (self.center_coor[0] - self.r, self.center_coor[1] - self.r)
        right = (self.center_coor[0] + self.r, self.center_coor[1] + self.r)
        self.coor_ls = generateCoor(left[0], left[1], right[0], right[1],
                                    self.m, self.n)

    # 如下分别为步行，公交，驾车的行程时间获取函数，相关参数含义请参考高德开放平台路径规划API文档
    # 传送门：https://lbs.amap.com/api/webservice/guide/api/direction

    def get_walking_time(self, origin, destination):
        url = f'https://restapi.amap.com/v3/direction/walking?origin={origin}&destination={destination}&key={self.key}'
        try:
            r = requests.get(url)
            rt = json.loads(r.text)
            time = rt['route']['paths'][0]['duration']
        except:
            time = 0
        return time

    # 注意此时的默认范围为湖南省长沙市
    def get_transit_time(self,
                         origin,
                         destination,
                         city='长沙',
                         cityd='长沙',
                         extensions='base',
                         strategy='0',
                         nightflag='0',
                         date=None,
                         time=None):
        url = f'https://restapi.amap.com/v3/direction/transit/integrated?origin={origin}&destination={destination}&key={self.key}' + \
              f'&city={city}&cityd={cityd}&extensions={extensions}&strategy={strategy}&nightflag={nightflag}'
        if date:
            url += f'&date={date}'
        if time:
            url += f'&time={time}'
        try:
            r = requests.get(url)
            rt = json.loads(r.text)
            time = rt['route']['transits'][0]['duration']
        except:
            time = 0
        return time

    # 此处可传递其余参数，详见高德文档
    def get_driving_time(self, origin, destination):
        url = f'https://restapi.amap.com/v3/direction/driving?origin={origin}&destination={destination}&key={self.key}'
        try:
            r = requests.get(url)
            rt = json.loads(r.text)
            time = rt['route']['paths'][0]['duration']
            print(time)
        except:
            time = 0
        return time

    def get_bicycling_time(self, origin, destination):
        url = f'https://restapi.amap.com/v4/direction/bicycling?origin={origin}&destination={destination}&key={self.key}'
        try:
            r = requests.get(url)
            rt = json.loads(r.text)
            time = rt['data']['paths'][0]['duration']
            print(time)
        except:
            time = 0
        return time

    def main(self):
        result = []
        origin = str(self.center_coor[0]) + ',' + str(self.center_coor[1])
        print('**正在获取行程时间数据**')
        for coor in tqdm(self.coor_ls):
            destination = str(coor[0]) + ',' + str(coor[1])
            time = self.get_time(origin=origin, destination=destination)
            coor_wgs84 = converter.gcj02_to_wgs84(coor[0], coor[1])
            result.append((coor_wgs84[0], coor_wgs84[1], time))
        print('**正在保存数据**')
        data = pd.DataFrame(result)
        data.columns = ['lng', 'lat', 'time']
        data['time'] = pd.to_numeric(data['time'])
        data = data[~(data['time'] == 0)]
        center_x_wgs84, center_y_wgs84 = converter.gcj02_to_wgs84(
            self.center_coor[0], self.center_coor[1])
        data.loc['center'] = [center_x_wgs84, center_y_wgs84, 0]
        data.to_csv('time.csv', encoding='utf_8_sig', index=False)
        print(f'**数据保存完毕，共采集到{len(data) - 1}个有效点**')


if __name__ == '__main__':
    method = 'transit'
    center_coor = (113.063964, 28.279842)
    gtt = GetTripTime(method, center_coor)
    gtt.main()