"""portalsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import path
from voters.views import createFaciview,createAdminview,createRepview
from voters.views import home_view,precinct_view,redirectview,createacc_view,login_view,scheduling_view,pwrecovery_view,profile_view,clang_view,logout_acc, testview, markvotedview
from adminside.views import ahome_view ,count_view,redir_view
urlpatterns = [
    path('admin/', admin.site.urls),
    path('Home',home_view,name="Home"),
    path('',redirectview,name='home'),
    path('precinct',precinct_view,name='precinct'),
    path('createAcc',createacc_view,name="creation"),
    path('login/',login_view,name="login"),
    path('schedule',scheduling_view,name="schedule"),
    path('recovery',pwrecovery_view,name="recovery"),
    path("profile",profile_view,name="profile"),
    path("langsetting",clang_view,name="language"),
    path("admin-count",count_view,name="adminBallot"),
    path("admn/login",login_view,name='login'),
    path("logout_acc",logout_acc,name='logout'),
    path("test",testview,name='test'),
    path("markvoted/",markvotedview,name='markvoted'),
    path("createFaci",createFaciview,name="createFaci"),
    path("createAdmin",createAdminview,name="createAdmin"),
    path("createRep",createRepview,name="createRep"),
]
