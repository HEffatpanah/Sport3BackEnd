import json

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

from Sport3.models import *


@api_view(['GET', 'POST'])
def home(request):
    print('eqerqwerqwerqwerqewr')
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
    for f in football_matches:
        json['football']['matchesTable']['tableBody'].append(f.get_match_summary_json())
    for f in basketball_matches:
        json['basketball']['matchesTable']['tableBody'].append(f.get_match_summary_json())
    for f in last_football_news:
        json['football']['newsTable']['last'].append(f.get_news_summary_json())
    for f in last_basketball_news:
            json['football']['newsTable']['last'].append(f.get_news_summary_json())
    return JsonResponse(json)


@api_view(['GET', 'POST'])
def news(request, news_id):
    # News.objects[:15]
    print('eqerqwerqwerqwerqewr')
    last_football_news = FootballNews.objects.order_by('-date_time')[:10]
    last_basketball_news = BasketballNews.objects.order_by('-date_time')[:10]
    football_matches = FootballMatch.objects.order_by('-date_time')[:50]
    basketball_matches = BasketballMatch.objects.order_by('-date_time')[:50]
    json = {'tableHeader': ['نام تیم', 'نتیجه', 'نام تیم', 'تاریخ'],
            'tableBody': []}
    for f in football_matches:
        json['tableBody'].append(f.create_match_summary_json())
    return JsonResponse(json)
    # if request.method == 'GET':
    #     return JsonResponse({'ok': 'get'})
    # else:
    #     return JsonResponse({'ok': 'post'})


def player():
    pass


def match():
    pass


def league():
    pass


def team():
    pass


def login():
    pass


def signup():
    pass


def forgotten():
    pass
