# manage-etherpad
这是一个基于flask、bootstrap（UI登录页）、layui（管理页面）整合的Etherpad前台管理页面，并可打包成Docker镜像

这个管理页面没有权限的概念，支持管理的Etherpad也仅仅为独立pad，并不涉及到组和用户，所以主要为单用户（管理员）使用

支持的功有登录、查询、新建、删除、编辑

# 配置

目录`/app/conf/my_condig.py`是基本配置：
``` python
Config = {
    # Etherpad的Web访问地址
    'web_url': 'http://xxx:9000',
    # 要使用的api版本
    'api_version': '1.3.0',
    # Etherpad的APIKEY
    'apikey': '4c987501ef3db61b7cbcd',
    # 定义管理员，可以有多个
    'users': [{
        'username': 'admin',
        'password': 'admin'
    }],
    # 管理程序使用的端口
    'web_port': 9040
}
```
