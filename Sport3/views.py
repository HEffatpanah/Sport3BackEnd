import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework.decorators import api_view

from Sport3.models import *


@api_view(['GET', 'POST'])
def home(request):
    last_football_news = FootballNews.objects.order_by('-date_time')[:10]
    last_basketball_news = BasketballNews.objects.order_by('-date_time')[:10]
    football_matches = FootballMatch.objects.order_by('-date_time')[:50]
    basketball_matches = BasketballMatch.objects.order_by('-date_time')[:50]
    json = {
        'football': {
            'matchesTable': {
                'tableHeader': ['نام تیم', 'نتیجه', 'نام تیم', 'تاریخ'],
                'tableBody': []},
            'newsTable': {
                'last': [],
                'favorite': [], }
        },
        'basketball': {
            'matchesTable': {
                'tableHeader': ['نام تیم', 'نتیجه', 'نام تیم', 'تاریخ'],
                'tableBody': []},
            'newsTable': {
                'last': [],
                'favorite': [], }
        }
    }
    json['football']['matchesTable']['tableBody'].append({'league_season': None, 'matches': []})
    json['basketball']['matchesTable']['tableBody'].append({'league_season': None, 'matches': []})
    for f in football_matches:
        json['football']['matchesTable']['tableBody'][0]['matches'].append(f.get_summary_json())
    for f in basketball_matches:
        json['basketball']['matchesTable']['tableBody'][0]['matches'].append(f.get_summary_json())
    for f in last_football_news:
        json['football']['newsTable']['last'].append(f.get_summary_json())
    for f in last_basketball_news:
        json['basketball']['newsTable']['last'].append(f.get_summary_json())
    return JsonResponse(json)


@api_view(['GET', 'POST'])
def news(request, news_title, news_id):
    json = {
        'newDetail': None,
        'newsData': []
    }
    news = News.objects.get(title=news_title, uid=news_id)
    summery_news = News.objects.order_by('-date_time')[:10]
    json['newDetail'] = news.get_json()
    for summery_news in summery_news:
        json['newsData'].append(summery_news.get_summary_json())

    return JsonResponse(json)


def player():
    pass


def match():
    pass


def league():
    pass


@api_view(['GET'])
def team(request, team_name, team_id):
    json = {
        'membersData': None,
        'matchData': None,
        'newsData': [],
        'teamName': team_name,
        'logo': None,
    }
    team = Team.objects.get(name=team_name, uid=team_id)
    json['logo'] = team.logo.url
    json['membersData'] = team.get_members_json()
    json['matchData'] = team.get_matches_json()
    summery_news = News.objects.filter(tags__name__contains='بازی')
    for summery_news in summery_news:
        json['newsData'].append(summery_news.get_summary_json())
    return JsonResponse(json)


def login():
    pass


def signup():
    pass


def forgotten():
    pass
