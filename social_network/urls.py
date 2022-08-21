from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views
from django.urls import include, path

handler404 = "posts.views.page_not_found" # noqa
handler500 = "posts.views.server_error" # noqa

urlpatterns = [
    path('404/', include('posts.urls')),
    path('500/', include('posts.urls')),
    path('admin/', admin.site.urls),
    path('about/', include('django.contrib.flatpages.urls')),
    path('about-author/', views.flatpage, {'url': '/about-author/'}, name='author'),
    path('about-spec/', views.flatpage, {'url': '/about-spec/'}, name='spec'),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls')),
]

urlpatterns += [
    path('about-us/', views.flatpage, {'url': '/about-us/'}, name='about'),
    path('terms/', views.flatpage, {'url': '/terms/'}, name='terms'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)), )
