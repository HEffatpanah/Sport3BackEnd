from django.conf.urls import url
from django.urls import path, re_path, include

from Sport3 import views

urlpatterns = [
    re_path(r'home[/]?', views.home, name='home'),
    path('news/<news_title>/<news_id>', views.news, name='news'),
    path('team/<team_name>/<team_id>', views.team, name='team'),
    path('player/<int:player_id>', views.player, name='player'),
    path('match/<int:match_id>', views.match, name='match'),
    path('league/<season_name>/<int:id>', views.league, name='league'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('forgotten', views.forgotten, name='forgotten'),
    url(r'^chaining/', include('smart_selects.urls')),
]
