# 『阴阳师』斗技数据获取

## 功能简介

本项目基于Selenium实现，获取斗技排行榜数据，供后续分析使用。

数据来源网易大神APP，爬虫模拟翻页操作，获取全区前100名玩家的斗技记录，包括斗技时间、阵容、对局结果等。爬虫结果保存在```json```文件和```xlsx```文件中。

## 使用步骤

#### 1、下载chrome驱动 

下载链接在[这里](https://googlechromelabs.github.io/chrome-for-testing/)，注意下载的驱动版本要和浏览器版本匹配。

#### 2、安装python依赖包
```pip install -r requirements.txt```

#### 3、运行

使用```Fiddler```等协议解析工具手工获取```token```和```timestamp```后，作为参数传入```args```，随后运行```main.py```。
