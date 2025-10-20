# 智能海报生成系统

<p align="center">
  <b>快速、准确的生成海报</b>
</p>
<p align="center">
  <a href="#"><img src="https://img.shields.io/badge/python-3.12%2B-blue" alt="Python" /></a>
  <a href="#"><img src="https://img.shields.io/badge/django-5.2.5+-green" alt="Django" /></a>
  <a href="#"><img src="https://img.shields.io/badge/restframework-3.16.1-red" alt="Djangoframework" /></a>
  <a href="#"><img src="https://img.shields.io/badge/license-MIT-blue" alt="License" /></a>
  <a href="#"><img src="https://img.shields.io/badge/ci-GitHub_Actions-blueviolet" alt="CI" /></a>
</p>


## 目录
- [简介](#简介)
- [特性亮点](#特性亮点)
- [快速开始](#快速开始)
  - [前提](#技术栈)
  - [克隆与安装](#克隆与安装)
  - [项目配置](#项目配置)
  - [初始化数据库](#初始化数据库)
  - [配置密钥](#配置密钥)
  - [配置支付宝沙箱环境](#配置支付宝沙箱环境)
  - [运行项目](#运行项目)
- [静态文件 & 媒体](#静态文件--媒体)

- [变更日志](#变更日志)
- [许可证](#许可证)
- [联系方式](#联系方式)

## 简介
基于本项目采用Django+djangorestframework框架，搭建users、poster_enums、poster、membership、analytics模块来实现功能。

1.**users**：提供用户注册、登录、个人信息管理、刷新和校验token（用于保持登录状态）、上传头像视图。

2.**membership**：提供创建、删除会员套餐，创建订单、获取订单，获取用户会员信息，支付宝沙箱支付、异步通知回调实现订单支付状态变化、同步回调定向到前端页面。

3.**poster**：提供海报生成（目前只完成了自定义生成模块，完全由用户自己输入提示词），海报生成记录，会员权限判断，上传参考图片接口。

4.**poster_enums**:提供海报生成需要的提示词枚举包含场景、风格、尺寸等方案，并组合成为提示词。

5.**analytics**：提供用户行为记录（浏览、选择类型、选择风格、生成、下载），并计算衰减函数，用户能获得更合适的提示词。

## 特性亮点

- **强大的图像生成功能**：支持多种图像生成模式，文生图、图文生图、单图和组图的生成模式选择。
- **完善的会员支付**：采用支付宝沙箱模拟支付，易于直接部署生产环境。
- **智能提示词推荐**：支持应用场景->海报类型->风格的智能推荐。

## 快速开始

### 技术栈
- **后端**: Python 3.12, Django 5.2.7，Djangorestframework 3.16.1
- **数据库**: MySQL, SQLite (可配置)

### 克隆与安装

```bash
#克隆项目
git clone https://github.com/choudan123/AIposter.git
cd AIposter

#虚拟环境
conda create -n myenv python=3.12
conda activate myenv

#安装依赖
pip install -r requirements.txt
```

### 项目配置
 打开 `ai_poster_system/settings.py` 文件，找到 `DATABASES` 配置项，修改为您的 MySQL 连接信息。
 
  ```python
  DATABASES = {
      'default': {
          'ENGINE': 'django.db.backends.mysql',
          'NAME': '你的数据库名',
          'USER': 'root',
          'PASSWORD': 'your_password',
          'HOST': '127.0.0.1',
          'PORT': 3306,
      }
  }
  ```
 在 MySQL 中创建数据库:
  ```sql
  CREATE DATABASE `your_database` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```

### 初始化数据库

```bash
python manage.py makemigrations
python manage.py migrate

# 创建一个超级管理员账户
python manage.py createsuperuser
```

### 配置密钥

```bash

# 配置你的API_key

ARK_API_KEY=your_apikey

```

### 配置支付宝沙箱环境

```bash

# 支付宝配置 - 沙箱环境
ALIPAY_CONFIG = {
    'app_id': '9021000156671602',  # 沙箱环境默认应用ID（你可以用自己的）
    'app_private_key': '''-----BEGIN RSA PRIVATE KEY-----
你的app私钥
-----END RSA PRIVATE KEY-----''',
    'alipay_public_key': '''-----BEGIN PUBLIC KEY-----
你的支付公钥
-----END PUBLIC KEY-----''',

    'sign_type': 'RSA2',
    'debug': True,  # 沙箱环境设为True
    'gateway_url': 'https://openapi-sandbox.dl.alipaydev.com/gateway.do',  # 沙箱网关
    'notify_url': '你的内网穿透链接/api/membership/alipay/notify/',  # 异步通知URL
    'return_url': 'http://127.0.0.1:5173/profile?payment=success',  # 同步跳转URL

}

```
### 运行项目

```bash
# 启动开发服务器
python manage.py runserver
```

## 静态文件 & 媒体
- 收集静态文件（生产环境）：
  python manage.py collectstatic --noinput
- 配置静态文件托管（使用 WhiteNoise / Nginx / CDN 等）



## 变更日志


## 许可证
本项目使用 [MIT](LICENSE)

## 联系方式
**2218370849@qq.com**
