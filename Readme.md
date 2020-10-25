## 1. 项目说明

基于地图平台的API接口绘制等时圈，支持Mapbox和高德地图。

## 2. 使用方式

1. 下载或克隆本项目
2. 基于Mapbox的等时圈绘制

最简单的绘制方法为，在命令行中输入 `python 你的路径\Get_Isochrone_from_mapbox.py --C=113.013714,28.193858`

在命令行中输入 `python 你的路径\Get_Isochrone_from_mapbox.py -h`可以查看帮助文档（写的不好..也不知道我说清楚了没）

3. 基于高德地图的等时圈绘制

最简单的绘制方法为，在命令行中输入`python 你的路径\Get_Isochrone_from_gaode.py`，获取得到time.csv文件，然后运行plot_isochrone_in_python.ipynb文件绘制等时圈

## 3. 项目文件介绍

1. Get_Isochrone_from_mapbox.py，用于存放基于Mapbox绘制等时圈的脚本
2. Get_Isochrone_from_gaode.py，用于获取基于高德地图的出行时间数据的脚本
3. converter.py，将高德坐标系转为wgs84的脚本，来源于GitHub https://github.com/gaussic/geo_convert
4. plot_isochrone_in_python.ipynb， 基于出行时间数据绘制等时圈的代码
5. time.csv, Get_Isochrone_from_gaode.py文件默认获取的出行时间数据
6. python_isochrone.png，基于默认出行数据绘制的python等时圈图

## 4. ...

感谢这些厉害的地图平台，感谢GitHub的开源者

