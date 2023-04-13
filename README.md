# 本地以图搜图软件

github地址： [https://github.com/xjhqre/xiSearch](https://github.com/xjhqre/xiSearch)

## 实现方法

使用 [towhee](https://hub.towhee.io/) 实现，界面使用 pyqt5 制作

## 使用方法

可以下载打包好的程序，运行 main.exe ， 或者下载代码运行 main.py 文件

1. 第一次启动程序后，到特征抽取界面设置图片库路径和特征文件保存路径
2. 点击提取特征按钮
4. 到图片搜索界面搜索

> 图片库路径写法：F:/ACG/壁纸/*，表示加载壁纸文件夹下所有图片
> 
> 特征文件保存地址写法：F:/ACG/特征文件，为文件夹路径，会在该文件夹下生成多个特征文件
>
> 支持一般常见格式：jpg、png、gif、jpeg，gif只提取第一帧
>

## 图片展示

![dsdffffffff](https://typora-xjhqre.oss-cn-hangzhou.aliyuncs.com/img/202304121546196.png)

![2](https://typora-xjhqre.oss-cn-hangzhou.aliyuncs.com/img/202304121536495.png)



## BUG解决

1、pytorch OSError: could not get source code

解决方案：https://github.com/pyinstaller/pyinstaller/issues/5729

2、pyinstaller 和 opencv-python 兼容问题

pyinstaller 版本改成 4.9

opencv-python 版本改成 4.5.3.56