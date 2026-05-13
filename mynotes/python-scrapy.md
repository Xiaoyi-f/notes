# scrapy 框架

## 预备知识

**基本爬虫逻辑**

![77864358263](C:\Users\XiaoYi\AppData\Local\Temp\1778643582639.png)

**Scrapy框架逻辑**

![77864374968](C:\Users\XiaoYi\AppData\Local\Temp\1778643749686.png)

1.scheduler调度器(队列) 把 requests --> 引擎 --> 下载中间件 --> 下载器

2.下载器发送请求，获取响应 --> 下载中间件 --> 引擎 --> 爬虫中间件 --> 爬虫

3.爬虫提取url地址 --> 组装成request对象 --> 爬虫中间件 --> 引擎 --> 调度器

4.爬虫提取数据 --> 引擎 --> 管道

5.管道进行数据的处理和保存

Tip: 一般只用手写 spider 和 管道(存储) 

## 快速上手

**scrapy startproject 项目名 --> 创建项目** 

**scrapy genspider 爬虫名 采集域名 --> 创建爬虫**

**|_ from scrapy.http import HttpResponse**

**|_ 手动实现爬虫的parse(self, response: HttpResponse, * * kwargs)函数实现提取数据相关操作(自动请求)**

**|_ resList = response.xpath("xpath")**

|_ response.url response.status response.body.decode('utf-8') response.text response.encoding response.request response.css('css选择器') response.json()

nextUrl = response.urljoin(response.xpath('xpath').extract_first()) -->

 yield scrapy.Request(url=nextUrl, callback=self.响应函数)

**|_ for res in resList:**

​	**item = {}**

​	**item['title'] = res.xpath('xpath').extract_first()**

**scrapy crawl 爬虫文件名 --> 启动爬虫**

**|_ 若报错ssl相关/很可能是版本冲突问题，pip install Twisted==22.10.0,  pip install pyOpenSSL==21.0.0, pip install cryptography==3.4.8** 

**|_ 在pycharm中启动爬虫** 

**|_ from scrapy import cmdline**

**|_ cmdline.execute('scrapy crawl 爬虫文件名'.split())**



**项目文件夹**

**cfg** 

​	配置文件 指定配置 

​	部署项目 配置 

**spiders**  爬虫

**item**  存放要采集调度"字段"

**middlewares**  自定义中间件

**pipelines**  管道文件 存储/输出相关操作

**settings**  配置文件

**|_ 将ROBOTSTXT_OBEY = True 注释掉**

**|_ DEFAULT_REQUEST_HEADERS 设置请求头**

**|_ 所有管道、中间件 必须在配置文件中配置**



**日志等级**

**CRITICAL 严重错误**

**ERROR 一般错误**

**WARNING 警告**

**INFO 一般信息**

**DEBUG 调试信息**









