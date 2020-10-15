本次分享的是基于Mapbox地图的等时圈绘制Python脚本，可以直接拿来用，不需要了解代码，下面首先会讲如何使用，然后才会对代码进行解析（不想要看代码的可以不看代码解析的部分，这也是公众号的初心之一，**无套路的贯彻拿来主义**，尽可能的降低学习成本，以后有关技术向的文章尽量写成一个黑盒子，只要给出输入就可以得到输出，而不需要关注中间的过程，人的学习精力是有限的~，当然由于喵喵君本身技术有限，所以可能写的不是很好，**欢迎各位大佬来投稿分享哦**，技术向文章的原则为**免费开源，开袋即食**，其余有趣的文章无要求（目前木有稿费！！）

## 1. 前提条件

说是拿来就用，但前提是装了Python和相关库，不然运行不了啊..

1. 安装好Python，建议按照公众号推文安装Anaconda，不然后面装第三方库更麻烦，传送门https://mp.weixin.qq.com/s/VyO3FfKXlXsPZpXIko5Y1A

2. 安装GeoPandas库，建议按照公众号推文来安装，传送门https://mp.weixin.qq.com/s/pOnJrTCpvl4xIErtq3iOZA
3. 下载本文提供的脚本文件，GitHub地址 https://github.com/Bardbo/Plot_Isochrone

## 2. 开袋即食

前提一定要做，不然运行不了！！

进入前文第三点中下载文件的目录，会有一个文件为 Get_Isochrone_from_mapbox.py，这就是本次的主角，**正文开始**，原则上仅需两步即可（可只看步骤1和3）：

1. 在该文件目录下打开命令行或Powershell，（Shift+右键）
2. 输入命令（建议复制），`python .\Get_Isochrone_from_mapbox.py -h `，回车运行，该命令运行会显示脚本的帮助文档，如下图

![1help](https://i.loli.net/2020/10/15/do5AsFCQ81h2kU6.png)

如--C,--P等均为脚本所支持的参数，除了--C参数是必须传入的，其余均为可选，参数此处不做详细介绍

3. 使用帮助文档中所提供的坐标绘制等时圈

继续在命令行中输入命令（建议复制）`python .\Get_Isochrone_from_mapbox.py --C=-118.22258,33.99038`，回车运行，即获得该坐标位置的等时圈图，不出意外的话应该和下图一样

![2示例图片](https://i.loli.net/2020/10/15/kS4GAgEtfiabZ3J.png)

4. 至此就绘制完了等时圈，可发现目录下多出了两个文件夹，一个json文件和一张图片。其中center_point文件夹内存储了坐标点的shp文件，是一种矢量文件，可在ArcGIS中进行编辑；r文件夹内存储了等时圈面层的shp文件，可自行编辑，如更换颜色等；r.json为mapbox网页响应的结果；r.png则是等时圈图片。

## 3. 详解

### 参数详解

所有参数的传入均与前文步骤3相似，--C表示坐标点（等时圈的起点），--P表示可选则的等时圈时间计算方式，也即三种出行方式，驾车、步行和骑行，--M表示等时圈绘制的时间范围，**--T为Mapbox网站注册申请的token（建议是自己去申请一个，不然容易出问题）**，--F是矢量等时圈面层shp保存文件的名称，--Center是坐标点文件shp的保存名称，--Fig是等时圈图片的保存名称。

**举例：**如果需要获取长沙火车站的10，20，30分钟的步行等时圈，将面层的文件名改为walk，将点层文件名改为train_station，图片名称改为t，应该在py文件目录的命令行中输入`python .\Get_Isochrone_from_mapbox.py --C=113.013714,28.193858 --P walking --M=10,20,30 --F walk --Center train_station --Fig t`

此处的坐标通过高德坐标拾取器获得 https://lbs.amap.com/console/show/picker ，需指出的是高德地图所使用坐标系为GCJ-02，Mapbox地图所使用的坐标系为WGS84，因此会存在十米到百米不等的偏差，虽然对于长时间的等时圈来说影响不大，但实践中仍**建议直接使用WGS84坐标**，如OSM和Mapbox本身

### 原理交流

1. 等时圈绘制原理

实际上等时圈的绘制是基于路径规划的，只是Mapbox自身提供了等时圈API接口，而高德地图等没有提供（基于高德地图的路径规划API的等时圈绘制下次找时间整理一下推送给大家）

举个例子来讲吧：假如要获取长沙火车站的15分钟步行等时圈，我们可以打开高德地图，设置长沙火车站为起点（红点），然后在火车站的周边选一些点，比如周边的茶颜悦色（绿点）和网吧（蓝点），利用高德的导航得出相应点位的步行时间，假设刚好砸偶到茶颜悦色的时间为10分钟，走到网吧的时间为20分钟，把他们连起来就成了20分钟和10分钟的等时圈，然后按照这些来做插值，就可以得出15分钟的这个等时圈（红色），选的点越多则插值与真实值越相似，但是也相对来说没那么平滑（灵魂画手的草图，如与事实雷同，纯属巧合）。

![3.例子](https://i.loli.net/2020/10/15/q58joHytZkGLRXx.png)

高德需要自己去通过路径规划API接口获得点的时间，然后再手动去做插值（比如利用ArcGIS软件，用Python也行）才能得出等时圈，而Mapbox的等时圈API就帮我们把这个过程给做了，只要发起请求就可以获得等时圈了。但是，高德地图提供了公交、货运等的路径规划，因此可以做公交和货运等的等时圈，而Mapbox就仅支持驾车、步行和骑行了。

2. Python调用API接口

首先提供API接口的网站都把如何去调用写的很详细了，至少Mapbox的等时圈接口写的很详细，Mapbox官方文档传送门：https://docs.mapbox.com/api/navigation/#isochrone

实际上调用API接口就像是访问网页，只是官方文档告诉了我们按它的来更改网页的URL地址（更改其中的参数）可以进入不同页面，不同的页面即不同的返回结果。

比如官方文档提供了这样一个URL地址：https://api.mapbox.com/isochrone/v1/mapbox/driving/-118.22258,33.99038?contours_minutes=5,10,15&contours_colors=6706ce,04e813,4286f4&polygons=true&access_token=pk.eyJ1IjoiYmFyZGJvIiwiYSI6ImNrZzkxbnlsZzA5M3gzMnF4NDgwOTV2YjEifQ.WqJJ6FosmvYhPj828tPUDw 我们可以将其复制到浏览器中看看会打开一个什么页面，里面的contours_minutes等就是官方文档给我们提供的参数，可以更改等号后面的数值来看看有什么不同（当然这里看不出来什么不同，哈哈哈，因为返回的页面是等时圈面层的边界坐标，全是数字）

本文提供的Python脚本就是使用requests库模拟浏览器的访问，获取返回的页面数据，然后再对获取到的等时圈面层坐标数据进行处理和可视化。

别的其它的API调用原理也是这样的，就是访问官方提供的URL地址，然后我们照它的做它就会给我们返回数据，更改URL地址的参数就会返回不同的数据，只是我们可以使用程序来帮助我们访问网页，然后处理网页返回的数据。（此外，一般网站都会有一些隐藏的API接口）

### 代码简单介绍

首先是导入库，没啥好说的，如果按照之前的推文进行下载的话都没问题，所用到的库功能写在下面的注释里

```python
import requests # 用来模拟访问网页，发起请求，获得数据
import json # 用来加载网页返回的数据，保存json格式的数据
import geopandas as gpd # 用来存储几何形状数据，自带了基于matplolib库的绘图
from shapely.geometry import Point, Polygon # 用来创建点和面，通过坐标对创建
import matplotlib.pyplot as plt # 用来绘图和保存图片
import argparse # 一个传入命令行参数的库，解析命令行参数
```

然后py文件中除了`main`函数外，有`get_isochrone_from_mapbox`、`save_to_shp`、`plot_and_save`这三个函数，函数的输入和输出等都写在注释里了。

1. `get_isochrone_from_mapbox`函数是使用`request`库的`get`方式发起请求，请求成功则保存相应的返回结果至json文件
2. `save_to_shp`函数，使用`for`循环取出返回结果中的等时圈面层坐标，并使用`shapely`库的`Polygon`函数创建面层，并使用`GeoPandas`库设置投影和保存
3. `plot_and_save`函数，则是绘制图片和保存图片
4. `main`函数则是将这三个函数整合在了一起，然后添加了保存坐标点的几行代码

此次的代码相对较简单，写了较多的注释，具体的可以看下源码哈~

### ArcGISPro

运行py文件获得的两个文件夹内的shp文件可以使用ArcGIS打开，进行编辑和可视化，择日再写有关ArcGIS的教程。分享ArcGISPro2.5版 百度云https://pan.baidu.com/s/1Y0J3SkBt8p-9ERCor-g9ng 提取码：p14h（侵删，来源于地信网，有条件建议支持正版哈哈）

下次见！