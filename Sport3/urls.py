from django.urls import path,re_path

from Sport3 import views

urlpatterns = [
    re_path(r'home[/]?', views.home, name='home'),
    path('news/<int:news_id>', views.news, name='news'),
    path('team/<int:team_id>', views.team, name='team'),
    path('player/<int:player_id>', views.player, name='player'),
    path('match/<int:match_id>', views.match, name='match'),
    path('league', views.league, name='league'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('forgotten', views.forgotten, name='forgotten'),
]
