from django.conf.urls import url
from django.urls import path, re_path, include

from Sport3 import views

urlpatterns = [
    re_path(r'home[/]?', views.home, name='home'),
    path('news/<news_title>/<news_id>', views.news, name='news'),
    path('team/<team_name>/<team_id>', views.team, name='team'),
    path('player/<player_name>/<player_id>', views.player, name='player'),
    path('match/<match_name>/<match_id>', views.match, name='match'),
    path('league/<league_name>/<season_name>/<id>', views.league, name='league'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('pass_forgotten', views.forgotten, name='forgotten'),
    path('logout', views.logout, name='logout'),
    url(r'^chaining/', include('smart_selects.urls')),
    path('confirm/<username>/<confirm_id>', views.confirm, name='confirm'),
    path('pass_change/<user_id>', views.change_pass, name='pass_change')
]
