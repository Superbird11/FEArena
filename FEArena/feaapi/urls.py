"""FEArena URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.urls import re_path
from .views import arena, teambuilder, user

urlpatterns = [
    re_path(r'csrf/?', user.csrf),
    re_path(r'account/login/?', user.log_in),
    re_path(r'account/create/?', user.create_account),
    re_path(r'account/logout/?', user.log_out),
    re_path(r'teambuilder/teams/(\d+)/?', teambuilder.single_team),
    re_path(r'teambuilder/teams/?', teambuilder.get_teams),
    re_path(r'teambuilder/add/?', teambuilder.build_team),
    re_path(r'arena/request/(\d+)/?', arena.check_match_request_status),
    re_path(r'arena/request/?', arena.request_match),
    re_path(r'arena/([A-Za-z0-9_-]+)/act/?', arena.submit_action),
    re_path(r'arena/([A-Za-z0-9_-]+)/?', arena.get_arena_data),
]
