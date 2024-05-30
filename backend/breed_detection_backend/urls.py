from django.contrib import admin
from django.urls import path, include

admin.site.site_header = "Animal breed detector Administration"
admin.site.site_title = "Animal breed detector Administration"
admin.site.index_title = "Animal breed detector Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("animals/", include("animals.urls")),
    path('users/', include('users.urls')),
]
