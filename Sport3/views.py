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
    news = get_object_or_404(News, title=news_title, uid=news_id)
    summery_news = News.objects.order_by('-date_time')[:10]
    json['newDetail'] = news.get_json()
    for summery_news in summery_news:
        json['newsData'].append(summery_news.get_summary_json())

    return JsonResponse(json)


def player(request, player_name, player_id):
    json = {
        'playerInfo': None,
        'playerRecords': None,
        'relatedNewsData': [],
        'newsData': []
    }
    player = get_object_or_404(Player, name=player_name, uid=player_id)
    summery_news = News.objects.order_by('-date_time')[:10]
    for summery_news in summery_news:
        json['relatedNewsData'].append(summery_news.get_summary_json())
        json['newsData'].append(summery_news.get_slides_json())
    json['playerInfo'] = player.get_json()
    json['playerRecords'] = player.get_statistics_json()
    return JsonResponse(json)


@api_view(['GET'])
def league(request, league_name, season_name, id):
    json = {
        'teams': [],
        'current_leagues': {'football': [], 'basketball': []},
        'old_leagues': {'football': [], 'basketball': []},
        'matchSummaryData': [],
    }
    print(league_name, season_name, id)
    if league_name == 'default' and season_name == 'default' and id == '0':
        league = DefaultLeague.objects.last().default_league
        half_season = CurrentHalfSeason.objects.last().current_half_season
    else:
        i = HalfSeason.objects.all()
        for a in i:
            print(a.name, a.uid)
        print(season_name, id)
        league = get_object_or_404(League, name=league_name)
        half_season = get_object_or_404(HalfSeason, name=season_name, uid=id)

    json['matchSummaryData'] = league.get_matches_json(half_season)
    json['teams'] = [league.get_teams_json(half_season)]

    # print(league, league.uid, '\n\n\n\n')
    football_leagues = FootballLeague.objects.all()
    basketball_leagues = BasketballLeague.objects.all()
    old_leagues = []
    current_leagues = []
    for fleague in football_leagues:
        old_leagues.append(fleague.get_old_half_seasons_json())
        current_leagues.append(fleague.get_current_half_seasons_json())
    json['old_leagues']['football'] = old_leagues
    json['current_leagues']['football'] = current_leagues
    old_leagues = []
    current_leagues = []
    for bleague in basketball_leagues:
        old_leagues.append(bleague.get_old_half_seasons_json())
        current_leagues.append(bleague.get_current_half_seasons_json())
    json['old_leagues']['basketball'] = old_leagues
    json['current_leagues']['basketball'] = current_leagues
    # json['current_leagues'] = league.get_current_half_seasons_json()
    # json['old_leagues'] = league.get_old_half_seasons_json()
    return JsonResponse(json)


@api_view(['GET'])
def team(request, team_name, team_id):
    json = {
        'membersData': None,
        'matchesData': None,
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


@api_view(['GET'])
def match(request, match_name, match_id):
    json = {
        'matchInfo': None,
        'medias': [],
        'newsData': [],
    }
    match = get_object_or_404(Match, uid=match_id)
    json['matchInfo'] = match.get_info_json()
    print('hiii')
    json['medias'] = match.get_medias_json()
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
