

from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('omnisight/', include('omnisight.urls')),
    path('omnisight_v2/', include('omnisight_v2.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

