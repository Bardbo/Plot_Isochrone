# -*- coding: utf-8 -*-
# @Author: Bardbo
# @Date:   2020-10-15 13:41:08
# @Last Modified by:   Bardbo
# @Last Modified time: 2020-10-15 21:00:01

import requests
import json
import geopandas as gpd
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt
import argparse


def get_isochrone_from_mapbox(
    coordinates,
    profile='driving',
    contours_minutes='5,10,15',
    access_token='pk.eyJ1IjoiYmFyZGJvIiwiYSI6ImNrZzkxbnlsZzA5M3gzMnF4NDgwOTV2YjEifQ.WqJJ6FosmvYhPj828tPUDw'
):
    """[使用request发起获取等时圈数据的请求，返回响应结果并保存至r.json中;
    mapbox官方文档：https://docs.mapbox.com/api/navigation/#isochrone]

    Args:
        coordinates ([str]): [坐标, 如 "-118.22258,33.99038"， 坐标系为WGS84]
        profile (str, optional): [可设置为"driving", "walking", "cycling"]. Defaults to 'driving'.
        contours_minutes (str, optional): [等时圈时间间距，单位为分钟，可以使用多个]. Defaults to '5,10,15'.
        access_token (str, optional): [mapbox的token，需注册申请]. Defaults to 'pk.eyJ1IjoiYmFyZGJvIiwiYSI6ImNrZzkxbnlsZzA5M3gzMnF4NDgwOTV2YjEifQ.WqJJ6FosmvYhPj828tPUDw'.

    Returns:
        [dict]: [请求结果]
    """

    # 发起请求
    r = requests.get(
        f"https://api.mapbox.com/isochrone/v1/mapbox/{profile}/" + \
        f"{coordinates}?contours_minutes={contours_minutes}" + \
        f"&polygons=true&access_token={access_token}"
    )

    # 判断请求是否成功
    if r.status_code == requests.codes.ok:
        r = json.loads(r.text)
        # 保存响应的参数结果
        with open('r.json', 'w') as f:
            print("**请求成功, 正在保存请求结果**")
            json.dump(r, f)
        return r
    else:
        r.raise_for_status()


def save_to_shp(coordinates, r, filename='r'):
    """[处理mapbox的响应结果，返回gdf和配色列表，并保存结果文件]

    Args:
        coordinates ([str]): [坐标, 如 "-118.22258,33.99038", 坐标系为WGS84]
        r ([dict]): [mapbox的等时圈响应结果字典]
        filename (str, optional): [gdf文件存储的名字]. Defaults to 'r'.

    Returns:
        [GeoDataFrame]: [存储了Polygon的gdf，拥有time， polygon_id, geometry三列]
        [List]: [存储了gdf中geometry的配色]
    """

    # 创建空的列表容器
    time = []
    polygon_id = []
    geometry = []
    color = []
    # 第一层遍历：遍历不同的时间取值
    for i in range(len(r['features'])):
        # 第二层遍历： 遍历同时间不同的polygon坐标，此处仅返回一个最大范围的polygon，因而无意义
        for j in range(len(r['features'][i]['geometry']['coordinates'])):
            time.append(r['features'][i]['properties']['contour'])
            polygon_id.append(j)
            geometry.append(
                # 构建面层
                Polygon(r['features'][i]['geometry']['coordinates'][j]))
            color.append(r['features'][i]['properties']['fillColor'])

    gdf = gpd.GeoDataFrame()
    gdf['time'] = time
    gdf['polygon_id'] = polygon_id
    gdf.geometry = geometry
    # 保存
    print("**正在保存处理结果文件**")
    gdf.to_file(filename, crs="EPSG:4326")
    return gdf, color


def plot_and_save(gdf, color, fig_name='r'):
    """[绘制等时圈，并保存图片]

    Args:
        gdf ([GeoDataFrame]): [存储了Polygon的gdf，拥有time， polygon_id, geometry三列]
        color ([List]): [存储了gdf中geometry的配色]
        fig_name (str, optional): [保存图片的名称]. Defaults to 'r'.
    """
    gdf.plot(color=color)
    print("**正在保存等时圈图片**")
    plt.savefig(fig_name + '.png', dpi=300)
    plt.show()


def main(
        coordinates,
        profile='driving',
        contours_minutes='5,10,15',
        access_token='pk.eyJ1IjoiYmFyZGJvIiwiYSI6ImNrZzkxbnlsZzA5M3gzMnF4NDgwOTV2YjEifQ.WqJJ6FosmvYhPj828tPUDw',
        filename='r',
        center_name='center_point',
        fig_name='r'):
    print("**正在请求网页**")
    r = get_isochrone_from_mapbox(coordinates, profile, contours_minutes,
                                  access_token)
    print("**正在保存中心点文件**")
    point_gdf = gpd.GeoDataFrame()
    point = coordinates.split(',')
    point_geometry = [Point(float(point[0]), float(point[1]))]
    point_gdf.geometry = point_geometry
    point_gdf.to_file(center_name, crs="EPSG:4326")
    print("**正在处理请求结果**")
    gdf, color = save_to_shp(coordinates, r, filename)
    gdf = gdf.append(
        {
            'time': -1,
            'polygon_id': -1,
            'geometry': point_geometry[0]
        },
        ignore_index=True)
    color.append('black')
    print("**正在绘制等时圈图片**")
    plot_and_save(gdf, color, fig_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--C',
        type=str,
        required=True,
        help=
        '输入WGS84坐标, 如 "-118.22258,33.99038", 请使用等号传递,引号无所谓 如 --C=-118.22258,33.99038'
    )
    parser.add_argument(
        '--P',
        type=str,
        default="driving",
        help='输入出行方式, 可以为"driving", "walking", "cycling"中的任一种, 默认为 "driving"')
    parser.add_argument(
        '--M',
        type=str,
        default='5,10,15',
        help="输入等时圈时间范围，单位是分钟, 默认为'5,10,15', 可传递单一数字，传递多个数字时请使用等号传递")
    parser.add_argument(
        '--T',
        type=str,
        default=
        'pk.eyJ1IjoiYmFyZGJvIiwiYSI6ImNrZzkxbnlsZzA5M3gzMnF4NDgwOTV2YjEifQ.WqJJ6FosmvYhPj828tPUDw',
        help='输入mapbox的token')
    parser.add_argument('--F',
                        type=str,
                        default='r',
                        help='输入GeoPandas文件的保存名字, 默认为r')
    parser.add_argument('--Center',
                        type=str,
                        default='center_point',
                        help='输入坐标点文件的保存名字, 默认为center_point')
    parser.add_argument('--Fig',
                        type=str,
                        default='r',
                        help='输入等时圈图片的保存名字, 默认为r')

    args = parser.parse_args()

    coordinates = args.C
    profile = args.P
    contours_minutes = args.M
    access_token = args.T
    filename = args.F
    center_name = args.Center
    fig_name = args.Fig

    main(coordinates, profile, contours_minutes, access_token, filename,
         center_name, fig_name)
