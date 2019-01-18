import json

from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view

from Sport3.models import *


@api_view(['POST'])
def home():
    last_news = News.objects.order_by('-date_time')[:10]
    football_matches = FootballMatch.objects.order_by('-date_time')


@api_view(['GET'])
def news(request, news_id):
    print('eshah')
    return JsonResponse({'ok': 'yes'})


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
