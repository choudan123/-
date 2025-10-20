# 智能海报生成系统

基于Django 5.2.7+Djangorestframework框架，集成Doubao-Seedream-4.0 API的智能海报生成系统

## 技术栈

- Django 5.2.7
- Django REST Framework 3.15.2
- Python 3.12+

## 功能特性

- RESTful API接口
- 海报生成任务管理
- 异步任务处理
- 图片上传与管理

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/choudan123/-.git
cd -
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 创建超级用户

```bash
python manage.py createsuperuser
```

### 6. 运行开发服务器

```bash
python manage.py runserver
```

访问 http://127.0.0.1:8000/api/ 查看API接口
访问 http://127.0.0.1:8000/admin/ 访问管理后台

## API接口

### 海报任务接口

- `GET /api/posters/` - 获取所有海报任务列表
- `POST /api/posters/` - 创建新的海报生成任务
- `GET /api/posters/{id}/` - 获取指定海报任务详情
- `PUT /api/posters/{id}/` - 更新海报任务
- `DELETE /api/posters/{id}/` - 删除海报任务
- `POST /api/posters/{id}/generate/` - 触发海报生成

### 创建海报任务示例

```bash
curl -X POST http://127.0.0.1:8000/api/posters/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "测试海报",
    "prompt": "生成一张科技感的海报"
  }'
```

## 项目结构

```
.
├── config/              # 项目配置目录
│   ├── settings.py     # Django设置
│   ├── urls.py         # 主路由配置
│   ├── wsgi.py        # WSGI配置
│   └── asgi.py        # ASGI配置
├── poster/             # 海报应用
│   ├── models.py      # 数据模型
│   ├── views.py       # 视图
│   ├── serializers.py # 序列化器
│   ├── urls.py        # 路由配置
│   └── admin.py       # 管理后台配置
├── manage.py          # Django管理脚本
├── requirements.txt   # 项目依赖
└── README.md         # 项目说明
```

## 开发说明

### 数据模型

#### PosterTask (海报任务)

- `title`: 标题
- `prompt`: 生成提示词
- `status`: 状态 (pending/processing/completed/failed)
- `image_url`: 图片URL
- `image`: 海报图片文件
- `error_message`: 错误信息
- `created_at`: 创建时间
- `updated_at`: 更新时间

## 许可证

MIT License

