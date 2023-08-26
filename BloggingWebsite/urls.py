"""
URL configuration for BloggingWebsite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from blogs.views import DashboardData
urlpatterns = [
    path('admin/', admin.site.urls),
    path('signup/', DashboardData.signup, name='signup'),
    path('login/', DashboardData.login, name='login'),
    path('logout/', DashboardData.logout, name='logout'),
    path('addComment/', DashboardData.addComment, name='addComment'),
    path('addLike/', DashboardData.addLike, name='addLike'),
    path('createBlog/', DashboardData.createBlog, name='createBlog'),
    path('getBlogsData/', DashboardData.getBlogsData, name='getBlogsData'),
    path('getLikes/', DashboardData.getLikes, name='getLikes'),
    path('getComments/', DashboardData.getComments, name='getComments'),
]
