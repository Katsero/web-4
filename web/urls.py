from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

handler404 = 'puzzlestore.views.custom_404'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('puzzlestore.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)