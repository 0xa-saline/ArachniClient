# ArachniClient
scan a url with Arachni Api
```
pip install yaml,requests,DBUtils,pymysql
```
单页面调用Arachni来实现扫描.需要的基本参数

url,

method,get/post/put...and so on

type, form or link

postdata=

首先需要打开Arachni的APi
```
# API:
$ ./bin/Arachni_rest_server  --address 0.0.0.0 --port 8888 --authentication-username admin --authentication-password password

WEB:
$ ./bin/arachni_web -o 0.0.0.0 -p 8888
or
$ ./bin/arachni_web --host 0.0.0.0 --port 8888
```

调用Arachni的思路
```
1.添加任务会返回一个id。记录下来和任务一起入库
#insert 'arachni' ('url','headers','param','token','status','starttime')

2.查看全部的扫描 /scans 循环查看每个id 是否结束.

3.更新id任务的状态，同时如果结束读取报告后删除id.避免重复读取
#update arachni set status = xxx where token = token

#insert ara_vun_info (token,name,severity,description,url,param,payload,requests_info,request_headers,response_headers,response_content,time)

```

没写数据库.只是想到这个思路还赞咯..
