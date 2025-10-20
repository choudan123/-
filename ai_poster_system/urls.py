"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # 添加这一行，将所有 /api/users/ 开头的请求都转发到 users 应用的 urls.py 文件中处理
    path('api/users/', include('apps.users.urls')),#用户路由
    path('api/membership/', include('apps.membership.urls')), #会员路由
    # path('api/poster_templates/', include('apps.poster_templates.urls')),  #海报模板路由
    path('api/poster/', include('apps.poster.urls')),  #海报生成路由
    path('api/poster_enums/', include('apps.poster_enums.urls')),  #海报提示词路由
    path('api/analytics/', include('apps.analytics.urls'))  #推荐提示词路由
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

