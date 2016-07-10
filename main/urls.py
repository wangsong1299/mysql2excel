"""main URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

from django.contrib.auth import views as auth_views
import app.views as app_views

from channels.routing import route

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', app_views.index),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}),  
    url(r'^logout/$', auth_views.logout, {'template_name': 'logout.html'}), 
    url(r'^home/$', app_views.home),
    url(r'^uploads/$', app_views.uploads),
    url(r'^downloads/$', app_views.downloads),
]

channel_routing = [
    route("websocket.connect", app_views.ws_connect),
    route("websocket.receive", app_views.ws_receive),
    route("websocket.disconnect", app_views.ws_disconnect),
]