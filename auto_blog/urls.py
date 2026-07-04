"""
Главный URL-конфиг проекта DrivePro.

Содержит маршруты для административной панели,
приложения блога и обслуживания медиа-файлов.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

urlpatterns = [
    # Панель администратора Django
    path('admin/', admin.site.urls),
    
    # Основное приложение блога
    path('blog/', include('blog.urls')),  
    
    path('accounts/', include('users.urls')),  
]

# Обслуживание загруженных медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )