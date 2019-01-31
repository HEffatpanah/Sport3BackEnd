import json as Json
import string, random
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import *

from Sport3.models import *


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def home(request):
    print(request.user, '\n\n\n')
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
@permission_classes((AllowAny,))
def news(request, news_title, news_id):
    print(request.user)
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
    print(request.user)
    json = {
        'playerInfo': None,
        'playerRecords': None,
        'relatedNewsData': [],
        'newsData': []
    }
    player = get_object_or_404(Player, name=player_name, uid=player_id)
    summery_news = player.get_news(True, True, True)[:10]
    for news in summery_news:
        json['relatedNewsData'].append(news.get_summary_json())
        json['newsData'].append(news.get_slides_json())
    json['playerInfo'] = player.get_json()
    json['playerRecords'] = player.get_statistics_json()
    return JsonResponse(json)


@api_view(['GET'])
@permission_classes((AllowAny,))
def league(request, league_name, season_name, id):
    print(request.user)
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

    football_leagues = FootballLeague.objects.all()
    basketball_leagues = BasketballLeague.objects.all()
    old_leagues = []
    current_leagues = []

    print('qwe\n\n\n\n')
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
    # print(json, '\n\n\n\n')
    # json['current_leagues'] = league.get_current_half_seasons_json()
    # json['old_leagues'] = league.get_old_half_seasons_json()
    return JsonResponse(json)


@api_view(['GET', 'POST'])
@permission_classes((AllowAny,))
def team(request, team_name, team_id):
    print(request.user)
    logged_in = 'no'
    if request.user.is_authenticated:
        logged_in = 'yes'
    json = {
        'membersData': None,
        'matchesData': None,
        'newsData': [],
        'teamName': team_name,
        'logo': None,
        'logged_in': logged_in
    }
    team = Team.objects.get(name=team_name, uid=team_id)
    json['logo'] = team.logo.url
    json['membersData'] = team.get_members_json()
    json['matchData'] = team.get_matches_json()
    summery_news = team.get_news(True, True, True)[:10]
    for news in summery_news:
        json['newsData'].append(news.get_summary_json())
    return JsonResponse(json)


@api_view(['GET'])
@permission_classes((AllowAny,))
def match(request, match_name, match_id):
    json = {
        'matchInfo': None,
        'medias': [],
        'onlineNewsData': [],
        'fringeNewsData': [],
    }
    match = get_object_or_404(Match, uid=match_id)
    json['matchInfo'] = match.get_info_json()

    json['medias'] = match.get_medias_json()
    # summery_news = News.objects.filter(tags__name__contains='بازی')
    # for summery_news in summery_news:
    news = match.get_news_json()
    json['onlineNewsData'] = news['online']
    json['fringeNewsData'] = news['fringe']
    return JsonResponse(json)


@api_view(["POST"])
@permission_classes((AllowAny,))
def login_site(request):
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is None:
        return Response({'message': 'not successful'})
    else:
        if SiteUser.objects.get(username=request.POST['username']).confirmed:
            token, _ = Token.objects.get_or_create(user=user)
            login(request, user)
            return Response({'token': token.key, 'message': 'successful'}, status=HTTP_200_OK)

            # login(request, user)
            # print('jkjkkj', request.user)
            # return Response({'message': 'successful'})
        return Response({'message': 'not confirmed'})


@api_view(["POST"])
@permission_classes((AllowAny,))
def signup(request):
    empty_fields = []
    empty = False
    for key, value in request.POST.items():
        if not value or value == 'false':
            empty_fields.append(key)
            empty = True
    if empty:
        return Response({'fields': empty_fields, 'message': 'empty_fields'})
    if request.POST['password'] != request.POST['confirm_pass']:
        return Response({'message': 'pass and confirm are not equal'})
    try:
        user = SiteUser.objects.create_user(username=request.POST['username'], password=request.POST['password'],
                                            first_name=request.POST['first_name'], last_name=request.POST['last_name'],
                                            email=request.POST['email'])

    except:
        return Response({'message': 'user exists‬'})
    digits = "".join([random.choice(string.digits) for i in range(14)])
    chars = "".join([random.choice(string.ascii_letters) for i in range(15)])
    user.confirm_id = digits + chars
    user.save()
    link = 'http://localhost:3000/sport3/confirm/' + str(user.username) + '/' + str(user.confirm_id)
    send_mail(
        'تایید حساب کاربری',
        'روی لینک زیر کلیک کنید تا حسابتان تایید شود\n\n' + link,
        'khani.ali1376@gmail.com',
        [user.email],
        fail_silently=False,
    )
    return Response({'message': 'user created‬'})


@api_view(["POST"])
@permission_classes((AllowAny,))
def logout_user(request):
    logout(request)
    return Response({'message': 'user logged out‬'})


@api_view(["POST"])
@permission_classes((AllowAny,))
def forgotten(request):
    if SiteUser.objects.filter(username=request.POST['username'], email=request.POST['email']).exists():
        user = SiteUser.objects.get(username=request.POST['username'])
        link = 'http://localhost:3000/sport3/pass_change/' + str(user.confirm_id)
        message = 'برای تغییر رمز روی لینک زیر کلیک کنید\n' + link
        send_mail(
            'فراموشی رمز عبور',
            message,
            'khani.ali1376@gmail.com',
            [user.email],
            fail_silently=False,
        )
        return Response({'message': 'email has been sent successfully'})
    else:
        return Response({'message': 'username or email is wrong'})


@api_view(["GET"])
@permission_classes((AllowAny,))
def confirm(request, username, confirm_id):
    if SiteUser.objects.filter(username=username).exists():
        user = SiteUser.objects.get(username=username)
        if user.confirm_id == confirm_id:
            user.confirmed = True
            user.save()
            return Response({'message': 'account has been confirmed'})
    return Response({'message': 'there is a problem'})


@api_view(["POST"])
@permission_classes((AllowAny,))
def change_pass(request, user_id):
    if request.POST['password'] != request.POST['confirm_pass']:
        return Response({'message': 'pass and confirm are not equal'})
    u = SiteUser.objects.get(confirm_id=user_id)
    # u = SiteUser.objects.get(username=user.username)
    u.set_password(request.POST['password'])
    u.save()
    return Response({'message': 'pass changed'})


@api_view(["POST"])
@permission_classes((AllowAny,))
def subscribe(request):
    data = Json.loads(request.body.decode('utf-8'))
    user = SiteUser.objects.get(username=data['username'])
    if data['type'] == 'team1':
        team = Team.objects.get(name=data['name'])
        user.favorite_teams.add(team)
        user.save()
    elif data['type'] == 'team0':
        team = Team.objects.get(name=data['name'])
        try:
            user.favorite_teams.remove(team)
            user.save()
        except:
            pass
    elif data['type'] == 'player1':
        player = Player.objects.get(name=data['name'])
        user.favorite_players.add(player)
        user.save()
    elif data['type'] == 'player0':
        player = Player.objects.get(name=data['name'])
        try:
            user.favorite_players.remove(player)
            user.save()
        except:
            pass
    return Response({'message': 'subscription action completed'})
