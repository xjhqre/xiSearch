# 本地以图搜图软件

github地址： [https://github.com/xjhqre/xiSearch](https://github.com/xjhqre/xiSearch)

## 实现方法

resnet50 提取图片特征向量，numpy 进行向量近似度计算

界面使用 pyqt5 制作

## 使用方法

可以下载打包好的程序，运行 main.exe ， 或者下载代码运行 main.py 文件

1. 第一次启动程序后，到特征抽取界面设置**图片库路径**和**特征文件保存路径**
2. 点击提取特征按钮
3. 点击加载特征
4. 到图片搜索界面搜索

> 图片库路径写法：F:/ACG/壁纸/*，表示加载壁纸文件夹下所有图片
> 
> 特征文件保存地址写法：F:/ACG/特征文件，为文件夹路径，会在该文件夹下生成多个特征文件
>
> 支持一般常见格式：jpg、png、gif、jpeg，gif只提取第一帧
>
> pyinstaller版本：4.5.1

## 图片展示

![image-20230225172034063](https://typora-xjhqre.oss-cn-hangzhou.aliyuncs.com/img/image-20230225172034063.png)

![image-20230224152415795](https://typora-xjhqre.oss-cn-hangzhou.aliyuncs.com/img/image-20230224152415795.png)