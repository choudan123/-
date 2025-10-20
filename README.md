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
  - [本地开发](#本地开发)
- [配置（.env）](#配置env)
- [数据库与迁移](#数据库与迁移)
- [运行测试](#运行测试)
- [静态文件 & 媒体](#静态文件--媒体)
- [部署建议](#部署建议)
- [发布与安装](#发布与安装)
- [贡献指南](#贡献指南)
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

### 1.技术栈
- **后端**: Python 3.12, Django 5.2.7，Djangorestframework 3.16.1
- **数据库**: MySQL, SQLite (可配置)

### 2.克隆与安装

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


3. 安装依赖：
   pip install -r requirements.txt

   或者如果使用 pip-tools：
   pip install pip-tools
   pip-compile requirements.in
   pip install -r requirements.txt

4. 复制环境变量模板并编辑（请不要将实际密钥提交到仓库）：
   cp .env.example .env
   编辑 `.env`，至少设置以下项（示例见下方）

5. 运行数据库迁移并创建管理员用户：
   python manage.py migrate
   python manage.py createsuperuser

6. 启动开发服务器：
   python manage.py runserver

7. 在浏览器打开 http://127.0.0.1:8000


## 数据库与迁移
- 创建迁移：
  python manage.py makemigrations
- 应用迁移：
  python manage.py migrate
- 若使用 Docker，确保数据库容器可访问后再运行 migrate（可以在 docker-compose.yml 中添加依赖或等待脚本）。

## 运行测试
- 使用 pytest（若使用）：
  pytest
- 使用 Django 自带测试：
  python manage.py test

（在 README 中说明你实际采用的测试工具和如何生成覆盖率报告）

## 静态文件 & 媒体
- 收集静态文件（生产环境）：
  python manage.py collectstatic --noinput
- 配置静态文件托管（使用 WhiteNoise / Nginx / CDN 等）

## 部署建议
- 生产时设置 DEBUG=False 且正确配置 ALLOWED_HOSTS
- 使用 Gunicorn + Nginx，示例：
  gunicorn myproject.wsgi:application --bind 0.0.0.0:8000
- 使用 HTTPS（Let's Encrypt / 商业证书）
- 使用环境变量管理敏感配置
- 使用进程管理（systemd / supervisor / Docker）

## 发布与安装
- 如果发布为包（wheel/sdist），可以放在 GitHub Releases 或 PyPI：
  pip install git+https://github.com/<OWNER>/<REPO>.git@vX.Y.Z
  或
  pip install https://github.com/<OWNER>/<REPO>/releases/download/vX.Y.Z/<wheel-file>.whl

## 贡献指南
欢迎贡献！简单流程：
1. Fork 仓库
2. 新建分支：git checkout -b feat/your-feature
3. 提交并发 PR（请写清变更说明与复现步骤）
4. 通过 CI 与代码审查后合并

可选：在仓库中添加 CONTRIBUTING.md、CODE_OF_CONDUCT.md、PR 模板和 ISSUE 模板。

## 变更日志
请在 Releases / CHANGELOG.md 中记录每次发布的变更摘要。建议使用 SemVer（语义化版本号）。

## 许可证
本项目使用 [MIT](LICENSE)（或替换为你选择的许可）。

## 联系方式
如发现安全问题或需要联系项目维护者，请发送邮件到：your-email@example.com  
项目维护者：@你的 GitHub 用户名

## 附录：常用命令速查
- 创建 venv：python -m venv .venv
- 安装依赖：pip install -r requirements.txt
- 生成 requirements（pip-tools）：pip-compile requirements.in
- 运行迁移：python manage.py migrate
- 启动开发服务器：python manage.py runserver
- 运行测试：pytest 或 python manage.py test
