import datetime
import uuid
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Q
from django.db.models.signals import *
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel
from smart_selects.db_fields import ChainedManyToManyField, ChainedForeignKey
from Backend import settings

private_storage = FileSystemStorage(location=settings.PRIVATE_STORAGE_ROOT)


def get_url(action, model):
    aux = model.get_url_id()
    return 'http://127.0.0.1:3000/sport3/{0}/{1}/{2}'.format(action, aux[0], aux[1])


# Create your models here.


class Photos(models.Model):
    def __str__(self):
        return self.photo.name

    photo = models.ImageField(storage=private_storage)


class HalfSeason(models.Model):
    def __str__(self):
        return self.name

    def get_url_id(self):
        return self.name, self.uid

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    half = models.BooleanField()
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = (("name",),)


# class FootballHalfSeason(HalfSeason):
#     pass
#
#
# class BasketballHalfSeason(HalfSeason):
#     pass


class League(PolymorphicModel):
    def __str__(self):
        return self.name

    def get_url_id(self):
        return self.name, self.uid

    def get_current_half_seasons_json(self):
        pass

    def get_old_half_seasons_json(self):
        pass

    def get_teams_json(self, half_season):
        pass

    def get_matches_json(self, half_season):
        pass

    half_season = models.ManyToManyField(HalfSeason)
    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = (("name",),)


class FootballLeague(League):
    teams = models.ManyToManyField('FootballTeam')

    def get_matches_json(self, half_season):
        json = {
            'tableHeader': ['نام تیم', 'نتیجه', 'نام تیم', 'تاریخ'],
            'tableBody': []
        }
        aux_json = {'league_season': self.name + '(' + str(half_season.name) + ')', 'matches': []}
        matches = FootballMatch.objects.filter(league=self, half_season=half_season)
        for match in matches:
            aux_json['matches'].append(match.get_summary_json())
        json['tableBody'].append(aux_json)
        return json

    def get_teams_json(self, half_season):
        json = {'leagueName': self.name + '(' + half_season.name + ')', 'tableName': self.name,
                'header': FootballHalfSeasonLeagueTeams.get_header(), 'tableData': []}
        teams = FootballHalfSeasonLeagueTeams.objects.filter(half_season=half_season, league=self)
        for team in teams:
            json['tableData'].append(team.get_json())
        return json

    def get_current_half_seasons_json(self):
        aux_json = {
            'name': None,
            'link': None,
        }
        half_season = CurrentHalfSeason.objects.last().current_half_season

        aux_json['name'] = self.name + '(' + half_season.name + ')'
        aux_json['link'] = get_url('league/' + self.name, half_season)

        json = {
            'leagueName': self.name,
            'sessions': [aux_json]
        }
        return json

    def get_old_half_seasons_json(self):
        half_seasons = self.half_season.filter(~Q(name=CurrentHalfSeason.objects.last().current_half_season.name))
        aux_json = {
            'name': None,
            'link': None,
        }
        json = {
            'leagueName': self.name,
            'sessions': []
        }
        for half_season in half_seasons:
            aux_json['name'] = str(self.name) + '(' + str(half_season.name) + ')'
            aux_json['link'] = get_url('league/' + self.name, half_season)
            json['sessions'].append(aux_json)

        return json


class BasketballLeague(League):
    teams = models.ManyToManyField('BasketballTeam')

    def get_matches_json(self, half_season):
        json = {
            'tableHeader': ['نام تیم', 'نتیجه', 'نام تیم', 'تاریخ'],
            'tableBody': []
        }
        aux = {'league_season': self.name + '(' + str(half_season.name) + ')', 'matches': []}
        matches = BasketballMatch.objects.filter(league=self, half_season=half_season)
        for match in matches:
            aux['matches'].append(match.get_summary_json())
        json['tableBody'].append(aux)
        return json

    def get_teams_json(self, half_season):
        json = {'leagueName': self.name + '(' + half_season.name + ')', 'tableName': self.name,
                'header': BasketballHalfSeasonLeagueTeams.get_header(), 'tableData': None}
        teams = BasketballHalfSeasonLeagueTeams.objects.filter(half_season=half_season, league=self)
        for team in teams:
            json['tableData'].append(team.get_json())
        return json

    def get_current_half_seasons_json(self):
        aux_json = {
            'name': None,
            'link': None,
        }
        half_season = CurrentHalfSeason.objects.last().current_half_season
        aux_json['name'] = self.name + '(' + half_season.name + ')'
        aux_json['link'] = get_url('league', half_season)
        json = {
            'leagueName': self.name,
            'sessions': [aux_json]
        }
        return json

    def get_old_half_seasons_json(self):
        half_season = self.half_season.filter(~Q(name=CurrentHalfSeason.objects.last().current_half_season.name))
        aux_json = {
            'name': None,
            'link': None,
        }
        for half_season in half_season:
            aux_json['name'] = str(self.name) + '(' + str(half_season.name) + ')'
            aux_json['link'] = get_url('leagues', half_season)
            half_season.append(aux_json)
        json = {
            'leagueName': self.name,
            'sessions': half_season
        }
        return json


class CurrentHalfSeason(models.Model):
    def __str__(self):
        return self.current_half_season.name

    current_half_season = models.ForeignKey(HalfSeason, on_delete=models.CASCADE)


class DefaultLeague(models.Model):
    def __str__(self):
        return self.default_league.name

    default_league = models.ForeignKey(FootballLeague, on_delete=models.CASCADE)


class Team(PolymorphicModel):
    def __str__(self):
        return self.name

    def get_url_id(self):
        return self.name, self.uid

    def get_members_json(self):
        pass

    def get_matches_json(self):
        pass

    def get_news_json(self):
        pass

    logo = models.ImageField(storage=private_storage, default='biel-morro-128512-unsplash.jpg')
    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=40)

    class Meta:
        unique_together = (("name",),)


class FootballTeam(Team):
    # members = models.ManyToManyField(FootballPlayer)

    def get_members_json(self):
        # print(get_last_half_season(HalfSeason))
        team_members = self.footballplayer_set.all()

        json = {
            'tableHeader': FootballPlayer.get_summary_header(),
            'tableBody': [],
        }
        for team_member in team_members:
            json['tableBody'].append(team_member.get_summary_json())
        return json

    def get_matches_json(self):
        matches = FootballMatch.objects.filter(Q(team1=self) | Q(team2=self))[:20]
        json = []
        for match in matches:
            json.append(match.get_json(self))
        return json

    def get_news_json(self):  # ####################################################################################
        news = FootballNews.objects.filter()[:20]
        json = []
        for news in news:
            json.append(news.get_summary_json())
        return json


class BasketballTeam(Team):
    # members = models.ManyToManyField(BasketballPlayer)

    def get_members_json(self):
        # print(get_last_half_season(HalfSeason))
        team_members = self.basketballplayer_set.all()

        json = {
            'tableHeader': BasketballPlayer.get_summary_header(),
            'tableBody': [],
        }
        for team_member in team_members:
            json['tableBody'].append(team_member.get_summary_json())
        return json

    def get_matches_json(self):
        matches = BasketballMatch.objects.filter(Q(team1=self) | Q(team2=self))[:20]
        json = []
        for match in matches:
            json.append(match.get_json(self))
        return json

    def get_news_json(self):  # ####################################################################################
        news = BasketballNews.objects.filter()[:20]
        json = []
        for news in news:
            json.append(news.get_summary_json())
        return json


class Player(PolymorphicModel):
    def team(self):
        pass

    def __str__(self):
        return self.name

    def get_url_id(self):
        return self.name, self.uid

    def get_json(self):
        pass

    def get_summary_json(self):
        pass

    def get_statistics_json(self):
        pass

    @staticmethod
    def get_summary_header():
        pass

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=40)
    birth_date = models.DateTimeField()
    photo = models.ImageField(storage=private_storage, null=True, blank=True)
    height = models.PositiveSmallIntegerField(default=0)
    weight = models.PositiveSmallIntegerField(default=0)
    nationality = models.CharField(max_length=30, default='')


class FootballPlayer(Player):
    position = models.CharField(max_length=20)
    team = models.ForeignKey(FootballTeam, on_delete=models.SET_NULL, null=True, blank=True)

    @staticmethod
    def get_summary_header():
        return ['نام', 'سن', 'پست', 'عکس']

    def get_summary_json(self):
        return (
            {
                'memberInfo': [
                    {'featureName': 'playerName', 'featureValue': self.name, 'featureLink': get_url('player', self)},
                    {'featureName': 'age', 'featureValue': datetime.datetime.now().year - self.birth_date.year,
                     'featureLink': None},
                    {'featureName': 'position', 'featureValue': self.position, 'featureLink': None},
                    {'featureName': 'photo',
                     'featureValue': self.photo.url,
                     'featureLink': None},
                ]
            }
        )

    def get_json(self):
        json = {
            'tableName': 'اطلاعات بازیکن',
            'fieldOfSport': 'football',
            'tableData':
                [
                    {'featureName': 'image', 'featureValue': self.photo.url},
                    {'featureName': 'نام', 'featureValue': self.name},
                    {'featureName': 'سن', 'featureValue': datetime.datetime.now().year - self.birth_date.year},
                    {'featureName': 'قد', 'featureValue': self.height},
                    {'featureName': 'وزن', 'featureValue': self.weight},
                    {'featureName': 'تیم فعلی', 'featureValue': self.team.name},
                    {'featureName': 'ملیت', 'featureValue': self.nationality},
                    {'featureName': 'پست', 'featureValue': self.position},
                ],
        }
        return json

    def get_statistics_json(self):
        statistics = FootballPlayerHalfSeasonStatistics.objects.filter(player=self).order_by('half_season__name')
        json = {
            'tableName': 'آمار بازیکن',
            'tableData': [],
            'seasons': [],
        }
        for statistic in statistics:
            aux_json = {
                'data': [
                    {'featureName': 'تعداد گل ها', 'featureValue': statistic.goals_number},
                    {'featureName': 'تعداد پاس گل ها', 'featureValue': statistic.assists_number},
                    {'featureName': 'تعداد کارت های زرد', 'featureValue': statistic.yellow_cards_number},
                    {'featureName': 'تعداد کارت های قرمز', 'featureValue': statistic.red_cards_number},
                ],
                'season': statistic.half_season.name
            }
            json['seasons'].append(
                {
                    'value': statistic.half_season.name,
                    'text': statistic.half_season.name,
                }
            )
            json['tableData'].append(aux_json)

        return json


class BasketballPlayer(Player):
    position = models.CharField(max_length=20)
    team = models.ForeignKey(BasketballTeam, on_delete=models.SET_NULL, null=True, blank=True)

    @staticmethod
    def get_summary_header():
        return ['نام', 'سن', 'پست', 'عکس']

    def get_summary_json(self):
        return (
            {
                'memberInfo': [
                    {'featureName': 'playerName', 'featureValue': self.name, 'featureLink': get_url('player', self)},
                    {'featureName': 'age', 'featureValue': datetime.datetime.now().year - self.birth_date.year,
                     'featureLink': None},
                    {'featureName': 'position', 'featureValue': self.position, 'featureLink': None},
                    {'featureName': 'photo',
                     'featureValue': self.photo.url,
                     'featureLink': None},
                ]
            }
        )

    def get_json(self):
        json = {
            'tableName': 'اطلاعات بازیکن',
            'fieldOfSport': 'football',
            'tableData':
                [
                    {'featureName': 'image', 'featureValue': self.photo.url},
                    {'featureName': 'نام', 'featureValue': self.name},
                    {'featureName': 'سن', 'featureValue': datetime.datetime.now().year - self.birth_date.year},
                    {'featureName': 'قد', 'featureValue': self.height},
                    {'featureName': 'وزن', 'featureValue': self.weight},
                    {'featureName': 'تیم فعلی', 'featureValue': self.team.name},
                    {'featureName': 'ملیت', 'featureValue': self.nationality},
                    {'featureName': 'پست', 'featureValue': self.position},
                ],
        }
        return json

    def get_statistics_json(self):
        statistics = BasketballPlayerHalfSeasonStatistics.objects.filter(player=self).order_by('half_season__name')
        json = {
            'tableName': 'آمار بازیکن',
            'tableData': [],
            'seasons': [],
        }
        for statistic in statistics:
            aux_json = {
                'data': [
                    {'featureName': 'تعداد پرتاب های دو امتیازی', 'featureValue': statistic.two_point_number},
                    {'featureName': 'تعداد پرتاپ های سه امتیازی', 'featureValue': statistic.three_point_number},
                    {'featureName': 'تعداد خطاها', 'featureValue': statistic.faults_number},
                    {'featureName': 'تعداد ریباند ها', 'featureValue': statistic.rebounds_numbers},
                ],
                'season': statistic.half_season.name
            }
            json['seasons'].append(
                {
                    'value': statistic.half_season.name,
                    'text': statistic.half_season.name,
                }
            )
            json['tableData'].append(aux_json)

        return json


@receiver(post_save, sender=FootballPlayer)
def save_team_half_season_members(sender, **kwargs):
    try:
        object = FootballTeamHalfSeasonMembers.objects.get(player=kwargs['instance'],
                                                           half_season=CurrentHalfSeason.objects.last().current_half_season)
    except:
        if kwargs['instance'].team:
            FootballTeamHalfSeasonMembers.objects.create(player=kwargs['instance'], team=kwargs['instance'].team,
                                                         half_season=CurrentHalfSeason.objects.last().current_half_season)
    else:
        if kwargs['instance'].team:
            object.team = kwargs['instance'].team
            object.save()


@receiver(post_save, sender=BasketballPlayer)
def save_team_half_season_members(sender, **kwargs):
    try:
        object = BasketballTeamHalfSeasonMembers.objects.get(player=kwargs['instance'],
                                                             half_season=CurrentHalfSeason.objects.last().current_half_season)
    except:
        if kwargs['instance'].team:
            BasketballTeamHalfSeasonMembers.objects.create(player=kwargs['instance'], team=kwargs['instance'].team,
                                                           half_season=CurrentHalfSeason.objects.last().current_half_season)
    else:
        if kwargs['instance'].team:
            object.team = kwargs['instance'].team
            object.save()


# @receiver(pre_delete, sender=FootballPlayer)
# def delete_team_half_season_members(sender, **kwargs):
#     print('\n\n\n\n', kwargs['instance'].team.name, '\n\n\n')
#
#     aux = FootballTeamHalfSeasonMembers.objects.filter(player=kwargs['instance'])
#     for i in aux:
#         i.delete()


class TeamHalfSeasonMembers(PolymorphicModel):
    def player(self):
        pass

    def team(self):
        pass

    def __str__(self):
        try:
            name = str(self.player.name) + '-' + str(self.team.name)
        except:
            name = 'deleted'
        return name

    def half_season(self):
        pass


class FootballTeamHalfSeasonMembers(TeamHalfSeasonMembers):
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    half_season = models.ForeignKey(HalfSeason, on_delete=models.CASCADE)


class BasketballTeamHalfSeasonMembers(TeamHalfSeasonMembers):
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    half_season = models.ForeignKey(HalfSeason, on_delete=models.CASCADE)


class Goal(models.Model):
    def __str__(self):
        return self.player.name + '-' + str(self.time)

    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class Substitute(PolymorphicModel):
    def __str__(self):
        return self.player_in.name + '-' + self.player_out.name

    time = models.PositiveSmallIntegerField()

    def match(self):
        pass

    def player_in(self):
        pass

    def player_out(self):
        pass


class FootballSubstitute(Substitute):
    player_in = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE, related_name='go_in')
    player_out = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE, related_name='come_out')


class BasketballSubstitute(Substitute):
    player_in = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE, related_name='go_in')
    player_out = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE, related_name='come_out')


class FootballAssist(models.Model):
    def __str__(self):
        return self.player.name + '-' + str(self.time)

    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    # team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballCard(models.Model):
    def __str__(self):
        return self.player.name + '-' + self.color

    color = models.CharField(max_length=256,
                             choices=[('first yellow', 'first yellow'), ('second yellow', 'second yellow'),
                                      ('red', 'red')], default='yellow')
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballPenalty(models.Model):
    def __str__(self):
        return self.player.name + '-' + str(self.time)

    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    # team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballThreePoint(models.Model):
    def __str__(self):
        return self.player.name + '-' + str(self.time)

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    # team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballTwoPoint(models.Model):
    def __str__(self):
        return self.player.name + '-' + str(self.time)

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    # team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballPenaltyFault(models.Model):
    def __str__(self):
        return self.player.name + '-' + str(self.time)

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    # team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballFault(models.Model):
    def __str__(self):
        return self.player.name + '-' + str(self.time)

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    # team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballPenaltyFailed(models.Model):
    def __str__(self):
        return self.player.name + '-' + str(self.time)

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    # team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballRebound(models.Model):
    def __str__(self):
        return self.player.name + '-' + str(self.time)

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    # team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class OnlineNews(models.Model):
    title = models.CharField(max_length=200, blank=True)

    def get_summary_json(self):
        return (
            {
                'title': self.title,
                'link': '',
            }
        )


class Match(PolymorphicModel):
    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    date_time = models.DateTimeField()
    half_season = models.ForeignKey(HalfSeason, null=True, on_delete=models.SET_NULL)
    online_news = models.ManyToManyField(OnlineNews, blank=True)

    def __str__(self):
        return self.team1.name + '-' + self.team2.name

    @property
    def result(self):
        pass

    def get_url_id(self):
        return (self.team1.name + '-' + self.team2.name), self.uid

    def team1(self):
        pass

    def team2(self):
        pass

    def best_player(self):
        pass

    def league(self):
        pass

    def get_summary_json(self):
        pass

    def get_json(self, team):
        pass

    def get_info_json(self):
        pass

    def get_medias_json(self):
        pass

    def get_news_json(self):
        pass

    def fringe_news(self):
        pass


class FootballMatch(Match):
    best_player = models.ForeignKey(FootballPlayer, null=True, on_delete=models.SET_NULL)
    league = models.ForeignKey(FootballLeague, null=True, on_delete=models.SET_NULL)
    match_minutes = models.PositiveSmallIntegerField(default=0)
    team1 = models.ForeignKey(FootballTeam, related_name='home_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(FootballTeam, related_name='away_matches', on_delete=models.CASCADE)
    team1_corners = models.PositiveSmallIntegerField()
    team2_corners = models.PositiveSmallIntegerField()
    team1_possession = models.FloatField(default=0.0)
    team2_possession = models.FloatField(default=0.0)
    team1_faults = models.PositiveSmallIntegerField()
    team2_faults = models.PositiveSmallIntegerField()
    team1_shoots = models.PositiveSmallIntegerField()
    team2_shoots = models.PositiveSmallIntegerField()
    team1_shoots_on_target = models.PositiveSmallIntegerField()
    team2_shoots_on_target = models.PositiveSmallIntegerField()
    team1_main_players = ChainedManyToManyField(FootballPlayer,
                                                horizontal=True,
                                                verbose_name='team1_main_players', chained_field="team1",
                                                chained_model_field="team",
                                                related_name='home_match_main')
    team1_substitute_players = ChainedManyToManyField(FootballPlayer,
                                                      horizontal=True,
                                                      verbose_name='team1_substitute_players', chained_field="team1",
                                                      chained_model_field="team",
                                                      related_name='home_match_substitute')
    team2_main_players = ChainedManyToManyField(FootballPlayer,
                                                horizontal=True,
                                                verbose_name='team2_main_players', chained_field="team2",
                                                chained_model_field="team",
                                                related_name='away_match_main')
    team2_substitute_players = ChainedManyToManyField(FootballPlayer,
                                                      horizontal=True,
                                                      verbose_name='team2_substitute_players', chained_field="team2",
                                                      chained_model_field="team",
                                                      related_name='away_match_substitute')
    team1_goals = models.ManyToManyField(Goal, related_name='home_match', blank=True)
    team2_goals = models.ManyToManyField(Goal, related_name='away_match', blank=True)
    team1_cards = models.ManyToManyField(FootballCard, related_name='home_match', blank=True)
    team2_cards = models.ManyToManyField(FootballCard, related_name='away_match', blank=True)
    team1_penalty = models.ManyToManyField(FootballPenalty, related_name='home_match', blank=True)
    team2_penalty = models.ManyToManyField(FootballPenalty, related_name='away_match', blank=True)
    team1_assists = models.ManyToManyField(FootballAssist, related_name='home_match', blank=True)
    team2_assists = models.ManyToManyField(FootballAssist, related_name='away_match', blank=True)
    team1_substitutes = models.ManyToManyField(FootballSubstitute, related_name='home_match', blank=True)
    team2_substitutes = models.ManyToManyField(FootballSubstitute, related_name='away_match', blank=True)
    medias = models.ManyToManyField(Photos, blank=True)
    fringe_news = models.ManyToManyField('FootballNews', related_name='home_match', blank=True)

    @property
    def result(self):
        team1_goals = self.team1_goals.count()
        team2_goals = self.team2_goals.count()
        return 0 if team1_goals == team2_goals else -1 if team1_goals < team2_goals else 1

    def get_medias_json(self):
        result = []
        for media in self.medias.all():
            result.append({'url': media.photo.url})
        return result

    def get_info_json(self):
        result = {
            'tableName': 'اطلاعات بازی',
            'tableType': 'فوتبال',
            'tableData': None,
        }
        match = {
            'matchMinutes': self.match_minutes,
            'team1': None,
            'team2': None,
            'bestPlayer': {'team': self.best_player.team.name, 'name': self.best_player.name},
        }
        team1 = {
            'generalRecords': [],
            'events': [],
            'players': {'originalPlayers': [], 'substitutesPlayers': []}
        }

        team2 = {
            'generalRecords': [],
            'events': [],
            'players': {'originalPlayers': [], 'substitutesPlayers': []}
        }
        team1['generalRecords'].append({'featureName': 'خطاها', 'featureValue': self.team1_faults}, )
        team1['generalRecords'].append({'featureName': 'کرنرها', 'featureValue': self.team1_corners}, )
        team1['generalRecords'].append({'featureName': 'شوت ها', 'featureValue': self.team1_shoots}, )
        team1['generalRecords'].append(
            {'featureName': 'شوت های در چارچوب', 'featureValue': self.team1_shoots_on_target}, )
        team1['generalRecords'].append({'featureName': 'تعداد گل', 'featureValue': self.team1_goals.count()}, )
        team1['generalRecords'].append({'featureName': 'درصد مالکیت توپ', 'featureValue': self.team1_possession}, )

        team1_yellow_cards = {'featureName': 'yc', 'featureValue': []}
        team1_second_yellow_cards = {'featureName': 'syc', 'featureValue': []}
        team1_red_cards = {'featureName': 'drc', 'featureValue': []}
        for card in self.team1_cards.all():
            if card.color == 'red':
                team1_red_cards['featureValue'].append(card.time)
            if card.color == 'first yellow':
                team1_yellow_cards['featureValue'].append(card.time)
            else:
                team1_second_yellow_cards['featureValue'].append(card.time)

        team1_goals = {
            'featureName': 'g',
            'featureValue': [],
        }
        for goal in self.team1_goals.all():
            team1_goals['featureValue'].append(goal.time)
        team1_assists = {
            'featureName': 'a',
            'featureValue': [],
        }
        for assist in self.team1_assists.all():
            team1_assists['featureValue'].append(assist.time)
        team1_substitutes = {
            'featureName': 's',
            'featureValue': [],
        }
        for substitute in self.team1_substitutes.all():
            team1_substitutes['featureValue'].append(substitute.time)
        team1_penalties = {
            'featureName': 'p',
            'featureValue': [],
        }
        for penalty in self.team1_penalty.all():
            team1_penalties['featureValue'].append(penalty.time)
        team1['events'].append(team1_yellow_cards)
        team1['events'].append(team1_second_yellow_cards)
        team1['events'].append(team1_red_cards)
        team1['events'].append(team1_goals)
        team1['events'].append(team1_assists)
        team1['events'].append(team1_substitutes)
        team1['events'].append(team1_penalties)

        for player in self.team1_main_players.all():
            if self.team1_substitutes.filter(player_out=player).first() is None:
                replace_time = 'null'
            else:
                replace_time = self.team1_substitutes.filter(player_out=player).first().time
            team1['players']['originalPlayers'].append({
                'Name': player.name,
                'Goals': self.team1_goals.filter(player=player).count(),
                'Post': player.position,
                'YellowCards': self.team1_cards.filter(
                    Q(player=player) & Q(Q(color='first yellow') | Q(color='second yellow'))).count(),
                'RedCards': self.team1_cards.filter(player=player, color='red').count(),
                'ReplaceTime': replace_time
            })

        for player in self.team1_substitute_players.all():
            if self.team1_substitutes.filter(player_in=player).first() is None:
                replace_time = 'null'
            else:
                replace_time = self.team1_substitutes.filter(player_in=player).first().time
            team1['players']['substitutesPlayers'].append({
                'Name': player.name,
                'Goals': self.team1_goals.filter(player=player).count(),
                'Post': player.position,
                'YellowCards': self.team1_cards.filter(
                    Q(player=player) & Q(Q(color='first yellow') | Q(color='second yellow'))).count(),
                'RedCards': self.team1_cards.filter(player=player, color='red').count(),
                'ReplaceTime': replace_time
            })
        match['team1'] = team1

        team2['generalRecords'].append({'featureName': 'خطاها', 'featureValue': self.team2_faults}, )
        team2['generalRecords'].append({'featureName': 'کرنرها', 'featureValue': self.team2_corners}, )
        team2['generalRecords'].append({'featureName': 'شوت ها', 'featureValue': self.team2_shoots}, )
        team2['generalRecords'].append(
            {'featureName': 'شوت های در چارچوب', 'featureValue': self.team2_shoots_on_target}, )
        team2['generalRecords'].append({'featureName': 'تعداد گل', 'featureValue': self.team2_goals.count()}, )
        team2['generalRecords'].append({'featureName': 'درصد مالکیت توپ', 'featureValue': self.team2_possession}, )
        team2_yellow_cards = {'featureName': 'yc', 'featureValue': []}
        team2_second_yellow_cards = {'featureName': 'syc', 'featureValue': []}
        team2_red_cards = {'featureName': 'drc', 'featureValue': []}
        for card in self.team2_cards.all():
            if card.color == 'red':
                team2_red_cards['featureValue'].append(card.time)
            if card.color == 'first yellow':
                team2_yellow_cards['featureValue'].append(card.time)
            else:
                team2_second_yellow_cards['featureValue'].append(card.time)
        team2_goals = {
            'featureName': 'g',
            'featureValue': [],
        }
        for goal in self.team2_goals.all():
            team2_goals['featureValue'].append(goal.time)
        team2_assists = {
            'featureName': 'a',
            'featureValue': [],
        }
        for assist in self.team2_assists.all():
            team2_assists['featureValue'].append(assist.time)
        team2_substitutes = {
            'featureName': 's',
            'featureValue': [],
        }
        for substitute in self.team2_substitutes.all():
            team2_substitutes['featureValue'].append(substitute.time)
        team2_penalties = {
            'featureName': 'p',
            'featureValue': [],
        }
        for penalty in self.team2_penalty.all():
            team2_penalties['featureValue'].append(penalty.time)
        team2['events'].append(team2_yellow_cards)
        team2['events'].append(team2_second_yellow_cards)
        team2['events'].append(team2_red_cards)
        team2['events'].append(team2_goals)
        team2['events'].append(team2_assists)
        team2['events'].append(team2_penalties)
        team2['events'].append(team2_substitutes)

        for player in self.team2_main_players.all():
            if self.team2_substitutes.filter(player_out=player).first() is None:
                replace_time = 'null'
            else:
                replace_time = self.team2_substitutes.filter(player_out=player).first().time
            team2['players']['originalPlayers'].append({
                'Name': player.name,
                'Goals': self.team2_goals.filter(player=player).count(),
                'Post': player.position,
                'YellowCards': self.team2_cards.filter(
                    Q(player=player) & Q(Q(color='first yellow') | Q(color='second yellow'))).count(),
                'RedCards': self.team2_cards.filter(player=player, color='red').count(),
                'ReplaceTime': replace_time
            })

        for player in self.team2_substitute_players.all():
            if self.team2_substitutes.filter(player_in=player).first() is None:
                replace_time = 'null'
            else:
                replace_time = self.team2_substitutes.filter(player_in=player).first().time
            team2['players']['substitutesPlayers'].append({
                'Name': player.name,
                'Goals': self.team2_goals.filter(player=player).count(),
                'Post': player.position,
                'YellowCards': self.team2_cards.filter(
                    Q(player=player) & Q(Q(color='first yellow') | Q(color='second yellow'))).count(),
                'RedCards': self.team2_cards.filter(player=player, color='red').count(),
                'ReplaceTime': replace_time
            })
        match['team2'] = team2
        result['tableData'] = match
        return result

    def get_json(self, team):
        team1_goals = self.team1_goals.count()
        team2_goals = self.team2_goals.count()
        if team == self.team1:
            score, status = (3, 'برد') if team1_goals > team2_goals else (
                1, 'مساوی') if team1_goals == team2_goals else (
                0, 'باخت')
            return (
                {
                    'ownerTeamGoal': team1_goals,
                    'opponentTeamGoal': team2_goals,
                    'date': self.date_time.date(),
                    'score': score,
                    'status': status,
                    'opponent': self.team2.name,
                    'opponentLink': get_url('team', self.team2),
                }
            )
        else:
            score, status = (3, 'برد') if team2_goals > team1_goals else (
                1, 'مساوی') if team1_goals == team2_goals else (
                0, 'باخت')
            return (
                {
                    'ownerTeamGoal': team2_goals,
                    'opponentTeamGoal': team1_goals,
                    'date': self.date_time.date(),
                    'score': score,
                    'status': status,
                    'opponent': self.team1.name,
                    'opponentLink': get_url('team', self.team1),
                }
            )

    def get_summary_json(self):
        return (
            {
                'matchLink': get_url('match', self),
                'team1Name': self.team1.name,
                'team1Link': get_url('team', self.team1),
                'team2Name': self.team2.name,
                'team2Link': get_url('team', self.team2),
                'team1Goal': self.team1_goals.count(),
                'team2Goal': self.team2_goals.count(),
                'date': 'امروز' if self.date_time.date() == datetime.datetime.now().date()
                else 'دیروز' if self.date_time.date() == datetime.datetime.now().date() - datetime.timedelta(days=1)
                else 'فردا' if self.date_time.date() == datetime.datetime.now().date() - datetime.timedelta(days=1)
                else self.date_time.date()
            }
        )

    def get_news_json(self):
        online_news = self.online_news.all()
        fringe_news = self.fringe_news.all()
        news_data = {
            'online': [],
            'fringe': []
        }
        for news in online_news:
            news_data['online'].append(news.get_summary_json())
        for news in fringe_news:
            news_data['fringe'].append(news.get_summary_json())
        return news_data


class BasketballMatch(Match):
    best_player = models.ForeignKey(BasketballPlayer, null=True, on_delete=models.SET_NULL)
    league = models.ForeignKey(BasketballLeague, null=True, on_delete=models.SET_NULL)
    match_minutes = models.PositiveSmallIntegerField(default=0)
    team1 = models.ForeignKey(BasketballTeam, related_name='home_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(BasketballTeam, related_name='away_matches', on_delete=models.CASCADE)
    team1_two_points = models.ManyToManyField(BasketballTwoPoint, related_name='home_match', blank=True)
    team2_two_points = models.ManyToManyField(BasketballTwoPoint, related_name='away_matches', blank=True)
    team1_three_points = models.ManyToManyField(BasketballThreePoint, related_name='home_match', blank=True)
    team2_three_points = models.ManyToManyField(BasketballThreePoint, related_name='away_matches', blank=True)
    team1_faults = models.ManyToManyField(BasketballFault, related_name='home_match', blank=True)
    team2_faults = models.ManyToManyField(BasketballFault, related_name='away_matches', blank=True)
    team1_penalty_faults = models.ManyToManyField(BasketballPenaltyFault, related_name='home_match', blank=True)
    team2_penalty_faults = models.ManyToManyField(BasketballPenaltyFault, related_name='away_matches', blank=True)
    team1_final_score = models.PositiveSmallIntegerField()
    team2_final_score = models.PositiveSmallIntegerField()
    team1_first_quarter_score = models.PositiveSmallIntegerField()
    team2_first_quarter_score = models.PositiveSmallIntegerField()
    team1_second_quarter_score = models.PositiveSmallIntegerField()
    team2_second_quarter_score = models.PositiveSmallIntegerField()
    team1_third_quarter_score = models.PositiveSmallIntegerField()
    team2_third_quarter_score = models.PositiveSmallIntegerField()
    team1_fourth_quarter_score = models.PositiveSmallIntegerField()
    team2_fourth_quarter_score = models.PositiveSmallIntegerField()
    team1_rebounds = models.ManyToManyField(BasketballRebound, related_name='home_match', blank=True)
    team2_rebounds = models.ManyToManyField(BasketballRebound, related_name='away_matches', blank=True)
    team1_penalty_failed = models.ManyToManyField(BasketballPenaltyFailed, related_name='home_match', blank=True)
    team2_penalty_failed = models.ManyToManyField(BasketballPenaltyFailed, related_name='away_matches', blank=True)
    team1_substitutes = models.ManyToManyField(BasketballSubstitute, related_name='home_match', blank=True)
    team2_substitutes = models.ManyToManyField(BasketballSubstitute, related_name='away_matches', blank=True)
    team1_main_players = ChainedManyToManyField(BasketballPlayer,
                                                horizontal=True,
                                                verbose_name='team1_main_players', chained_field="team1",
                                                chained_model_field="team",
                                                related_name='home_match_main')
    team1_substitute_players = ChainedManyToManyField(BasketballPlayer,
                                                      horizontal=True,
                                                      verbose_name='team1_substitute_players', chained_field="team1",
                                                      chained_model_field="team",
                                                      related_name='home_match_substitute')
    team2_main_players = ChainedManyToManyField(BasketballPlayer,
                                                horizontal=True,
                                                verbose_name='team2_main_players', chained_field="team2",
                                                chained_model_field="team",
                                                related_name='away_match_main')
    team2_substitute_players = ChainedManyToManyField(BasketballPlayer,
                                                      horizontal=True,
                                                      verbose_name='team2_substitute_players', chained_field="team2",
                                                      chained_model_field="team",
                                                      related_name='away_match_substitute')
    medias = models.ManyToManyField(Photos, blank=True)
    fringe_news = models.ManyToManyField('BasketballNews', related_name='home_match', blank=True)

    @property
    def result(self):
        team1_scores = self.team1_final_score
        team2_scores = self.team2_final_score
        return 0 if team1_scores == team2_scores else -1 if team1_scores < team2_scores else 1

    def get_medias_json(self):
        result = []
        for media in self.medias.all():
            result.append({'url': media.photo.url})
        return result

    def get_info_json(self):
        result = {
            'tableName': 'اطلاعات بازی',
            'tableType': 'بسکتبال',
            'tableData': None,
        }
        match = {
            'matchMinutes': self.match_minutes,
            'team1': None,
            'team2': None,
        }
        team1 = {
            'generalRecords': [],
            'events': [],
            'players': {'originalPlayers': [], 'substitutesPlayers': []}
        }

        team2 = {
            'generalRecords': [],
            'events': [],
            'players': {'originalPlayers': [], 'substitutesPlayers': []}
        }
        team1['generalRecords'].append(
            {'featureName': 'پرتاب های دو امتیازی', 'featureValue': self.team1_two_points.all().count()}, )
        team1['generalRecords'].append(
            {'featureName': 'پرتاپ های سه امتیازی', 'featureValue': self.team1_three_points.all().count()}, )
        team1['generalRecords'].append({'featureName': 'خطاها', 'featureValue': self.team1_faults.all().count()}, )
        team1['generalRecords'].append(
            {'featureName': 'خطاهای پنالتی', 'featureValue': self.team1_penalty_faults.all().count()}, )
        team1['generalRecords'].append({'featureName': 'امتیاز نهایی', 'featureValue': self.team1_final_score}, )
        team1['generalRecords'].append(
            {'featureName': 'امتیاز کواتر اول', 'featureValue': self.team1_first_quarter_score}, )
        team1['generalRecords'].append(
            {'featureName': 'امتیاز کواتر دوم', 'featureValue': self.team1_second_quarter_score}, )
        team1['generalRecords'].append(
            {'featureName': 'امتیاز کواتر سوم', 'featureValue': self.team1_third_quarter_score}, )
        team1['generalRecords'].append(
            {'featureName': 'امتیاز کواتر چهارم', 'featureValue': self.team1_first_quarter_score}, )

        team1_three_points = {'featureName': 'three_point', 'featureValue': []}
        team1_two_points = {'featureName': 'two_point', 'featureValue': []}
        team1_penalty_faults = {'featureName': 'penalty_faults', 'featureValue': []}
        team1_penalty_faileds = {'featureName': 'penalty_faileds', 'featureValue': []}
        team1_substitutes = {'featureName': 's', 'featureValue': []}
        team1_rebounds = {'featureName': 'rebounds', 'featureValue': []}
        for o in self.team1_three_points.all():
            team1_three_points['featureValue'].append(o.time)
        for o in self.team1_two_points.all():
            team1_two_points['featureValue'].append(o.time)
        for o in self.team1_penalty_faults.all():
            team1_penalty_faults['featureValue'].append(o.time)
        for o in self.team1_penalty_failed.all():
            team1_penalty_faileds['featureValue'].append(o.time)
        for o in self.team1_substitutes.all():
            team1_substitutes['featureValue'].append(o.time)
        for o in self.team1_rebounds.all():
            team1_rebounds['featureValue'].append(o.time)

        team1['events'].append(team1_three_points)
        team1['events'].append(team1_two_points)
        team1['events'].append(team1_penalty_faults)
        team1['events'].append(team1_penalty_faileds)
        team1['events'].append(team1_substitutes)
        team1['events'].append(team1_rebounds)

        for player in self.team1_main_players.all():
            if self.team1_substitutes.filter(player_out=player).first() is None:
                replace_time = 'null'
            else:
                replace_time = self.team1_substitutes.filter(player_out=player).first().time
            team1['players']['originalPlayers'].append({
                'Name': player.name,
                'TwoPoints': self.team1_two_points.filter(player=player).count(),
                'ThreePoints': self.team1_three_points.filter(player=player).count(),
                'Rebounds': self.team1_rebounds.filter(player=player).count(),
                'ReplaceTime': replace_time
            })

        for player in self.team1_substitute_players.all():
            if self.team1_substitutes.filter(player_in=player).first() is None:
                replace_time = 'null'
            else:
                replace_time = self.team1_substitutes.filter(player_in=player).first().time
            team1['players']['substitutesPlayers'].append({
                'Name': player.name,
                'TwoPoints': self.team1_two_points.filter(player=player).count(),
                'ThreePoints': self.team1_three_points.filter(player=player).count(),
                'Rebounds': self.team1_rebounds.filter(player=player).count(),
                'ReplaceTime': replace_time
            })
        match['team1'] = team1
        team2['generalRecords'].append(
            {'featureName': 'پرتاب های دو امتیازی', 'featureValue': self.team2_two_points.all().count()}, )
        team2['generalRecords'].append(
            {'featureName': 'پرتاپ های سه امتیازی', 'featureValue': self.team2_three_points.all().count()}, )
        team2['generalRecords'].append({'featureName': 'خطاها', 'featureValue': self.team1_faults.all().count()}, )
        team2['generalRecords'].append(
            {'featureName': 'خطاهای پنالتی', 'featureValue': self.team2_penalty_faults.all().count()}, )
        team2['generalRecords'].append({'featureName': 'امتیاز نهایی', 'featureValue': self.team2_final_score}, )
        team2['generalRecords'].append(
            {'featureName': 'امتیاز کواتر اول', 'featureValue': self.team2_first_quarter_score}, )
        team2['generalRecords'].append(
            {'featureName': 'امتیاز کواتر دوم', 'featureValue': self.team2_second_quarter_score}, )
        team2['generalRecords'].append(
            {'featureName': 'امتیاز کواتر سوم', 'featureValue': self.team2_third_quarter_score}, )
        team2['generalRecords'].append(
            {'featureName': 'امتیاز کواتر چهارم', 'featureValue': self.team2_first_quarter_score}, )

        team2_three_points = {'featureName': 'three_point', 'featureValue': []}
        team2_two_points = {'featureName': 'two_point', 'featureValue': []}
        team2_penalty_faults = {'featureName': 'penalty_faults', 'featureValue': []}
        team2_penalty_faileds = {'featureName': 'penalty_faileds', 'featureValue': []}
        team2_substitutes = {'featureName': 's', 'featureValue': []}
        team2_rebounds = {'featureName': 'rebounds', 'featureValue': []}
        for o in self.team2_three_points.all():
            team2_three_points['featureValue'].append(o.time)
        for o in self.team2_two_points.all():
            team2_two_points['featureValue'].append(o.time)
        for o in self.team2_penalty_faults.all():
            team2_penalty_faults['featureValue'].append(o.time)
        for o in self.team2_penalty_failed.all():
            team2_penalty_faileds['featureValue'].append(o.time)
        for o in self.team2_substitutes.all():
            team2_substitutes['featureValue'].append(o.time)
        for o in self.team2_rebounds.all():
            team2_rebounds['featureValue'].append(o.time)
        team2['events'].append(team2_three_points)
        team2['events'].append(team2_two_points)
        team2['events'].append(team2_penalty_faults)
        team2['events'].append(team2_penalty_faileds)
        team2['events'].append(team2_substitutes)
        team2['events'].append(team2_rebounds)

        for player in self.team2_main_players.all():
            if self.team2_substitutes.filter(player_out=player).first() is None:
                replace_time = 'null'
            else:
                replace_time = self.team2_substitutes.filter(player_out=player).first().time
            team2['players']['originalPlayers'].append({
                'Name': player.name,
                'TwoPoints': self.team2_two_points.filter(player=player).count(),
                'ThreePoints': self.team2_three_points.filter(player=player).count(),
                'Rebounds': self.team2_rebounds.filter(player=player).count(),
                'ReplaceTime': replace_time
            })

        for player in self.team2_substitute_players.all():
            if self.team2_substitutes.filter(player_in=player).first() is None:
                replace_time = 'null'
            else:
                replace_time = self.team2_substitutes.filter(player_in=player).first().time
            team2['players']['substitutesPlayers'].append({
                'Name': player.name,
                'TwoPoints': self.team2_two_points.filter(player=player).count(),
                'ThreePoints': self.team2_three_points.filter(player=player).count(),
                'Rebounds': self.team2_rebounds.filter(player=player).count(),
                'ReplaceTime': replace_time
            })
        match['team2'] = team2
        result['tableData'] = match
        return result

    def get_json(self, team):
        team1_final_score = self.team1_final_score
        team2_final_score = self.team2_final_score
        score, status = (3, 'برد') if team1_final_score > team2_final_score else (
            1, 'مساوی') if team1_final_score == team2_final_score else (0, 'باخت')
        return (
            {
                'matchLink': get_url('match', self),
                'ownerTeamGoal': team1_final_score,
                'opponentTeamGoal': team2_final_score,
                'date': self.date_time.date(),
                'score': score,
                'status': status,
                'opponent': self.team2.name,
                'opponentLink': get_url('team', self.team2),
            }
        )

    def get_summary_json(self):
        return (
            {
                'matchLink': get_url('match', self),
                'team1Name': self.team1.name,
                'team1Link': get_url('team', self.team1),
                'team2Name': self.team2.name,
                'team2Link': get_url('team', self.team2),
                'team1Goal': self.team1_final_score,
                'team2Goal': self.team2_final_score,
                'date': 'امروز' if self.date_time.date() == datetime.datetime.now().date()
                else 'دیروز' if self.date_time.date() == datetime.datetime.now().date() - datetime.timedelta(days=1)
                else 'فردا' if self.date_time.date() == datetime.datetime.now().date() - datetime.timedelta(days=1)
                else self.date_time.date()
            }
        )

    def get_news_json(self):
        online_news = self.online_news.all()
        fringe_news = self.fringe_news.all()
        news_data = {
            'online': [],
            'fringe': []
        }
        for news in online_news:
            news_data['online'].append(news.get_summary_json())
        for news in fringe_news:
            news_data['fringe'].append(news.get_summary_json())
        return news_data


class PlayerHalfSeasonStatistics(PolymorphicModel):
    half_season = models.ForeignKey(HalfSeason, on_delete=models.CASCADE)

    def player(self):
        pass

    # def match(self):
    #     pass


class FootballPlayerHalfSeasonStatistics(PlayerHalfSeasonStatistics):
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    goals_number = models.PositiveSmallIntegerField(default=0)
    yellow_cards_number = models.PositiveSmallIntegerField(default=0)
    red_cards_number = models.PositiveSmallIntegerField(default=0)
    assists_number = models.PositiveSmallIntegerField(default=0)
    # match = models.ForeignKey(FootballMatch, null=True, on_delete=models.SET_NULL)


class BasketballPlayerHalfSeasonStatistics(PlayerHalfSeasonStatistics):
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    two_point_number = models.PositiveSmallIntegerField(default=0)
    three_point_number = models.PositiveSmallIntegerField(default=0)
    faults_number = models.PositiveSmallIntegerField(default=0)
    penalty_faults_number = models.PositiveSmallIntegerField(default=0)
    rebounds_numbers = models.PositiveSmallIntegerField(default=0)
    # match = models.ForeignKey(BasketballMatch, null=True, on_delete=models.SET_NULL)


@receiver(m2m_changed, sender=FootballMatch.team1_goals.through)
@receiver(m2m_changed, sender=FootballMatch.team2_goals.through)
def save_football_player_half_season_goals(sender, **kwargs):
    match = kwargs['instance']
    if kwargs['action'] == 'pre_remove':
        pks = kwargs['pk_set']
        for pk in pks:
            player = Goal.objects.get(pk=pk).player
            statistic = FootballPlayerHalfSeasonStatistics.objects.get(player=player, half_season=match.half_season)
            statistic.goals_number -= 1
            statistic.save()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            player = Goal.objects.get(pk=pk).player
            statistic, created = FootballPlayerHalfSeasonStatistics.objects.get_or_create(player=player,
                                                                                          half_season=match.half_season)
            statistic.goals_number += 1
            statistic.save()


@receiver(m2m_changed, sender=FootballMatch.team1_cards.through)
@receiver(m2m_changed, sender=FootballMatch.team2_cards.through)
def save_football_player_half_season_cards(sender, **kwargs):
    match = kwargs['instance']
    if kwargs['action'] == 'pre_remove':
        pks = kwargs['pk_set']
        for pk in pks:
            card = FootballCard.objects.get(pk=pk)
            player = card.player
            statistic = FootballPlayerHalfSeasonStatistics.objects.get(player=player, half_season=match.half_season)
            if card.color == 'first yellow':
                statistic.yellow_cards_number -= 1
            elif card.color == 'second yellow':
                statistic.yellow_cards_number -= 1
                statistic.red_cards_number -= 1
            elif card.color == 'red':
                statistic.red_cards_number -= 1
            statistic.save()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            card = FootballCard.objects.get(pk=pk)
            player = card.player
            statistic, created = FootballPlayerHalfSeasonStatistics.objects.get_or_create(player=player,
                                                                                          half_season=match.half_season)
            if card.color == 'first yellow':
                statistic.yellow_cards_number += 1
            elif card.color == 'second yellow':
                statistic.yellow_cards_number += 1
                statistic.red_cards_number += 1
            elif card.color == 'red':
                statistic.red_cards_number += 1
            statistic.save()


@receiver(m2m_changed, sender=FootballMatch.team1_assists.through)
@receiver(m2m_changed, sender=FootballMatch.team2_assists.through)
def save_football_player_half_season_assists(sender, **kwargs):
    match = kwargs['instance']
    if kwargs['action'] == 'pre_remove':
        pks = kwargs['pk_set']
        for pk in pks:
            player = FootballAssist.objects.get(pk=pk).player
            statistic = FootballPlayerHalfSeasonStatistics.objects.get(player=player, half_season=match.half_season)
            statistic.assists_number -= 1
            statistic.save()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            player = FootballAssist.objects.get(pk=pk).player
            statistic, created = FootballPlayerHalfSeasonStatistics.objects.get_or_create(player=player,
                                                                                          half_season=match.half_season)
            statistic.assists_number += 1
            statistic.save()


@receiver(m2m_changed, sender=BasketballMatch.team1_two_points.through)
@receiver(m2m_changed, sender=BasketballMatch.team2_two_points.through)
def save_basketball_player_half_season_two_points(sender, **kwargs):
    match = kwargs['instance']
    if kwargs['action'] == 'pre_remove':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballTwoPoint.objects.get(pk=pk).player
            statistic = BasketballPlayerHalfSeasonStatistics.objects.get(player=player, half_season=match.half_season)
            statistic.two_point_number -= 1
            statistic.save()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballTwoPoint.objects.get(pk=pk).player
            statistic, created = BasketballPlayerHalfSeasonStatistics.objects.get_or_create(player=player,
                                                                                            half_season=match.half_season)
            statistic.two_point_number += 1
            statistic.save()


@receiver(m2m_changed, sender=BasketballMatch.team1_three_points.through)
@receiver(m2m_changed, sender=BasketballMatch.team2_three_points.through)
def save_basketball_player_half_season_three_points(sender, **kwargs):
    match = kwargs['instance']
    if kwargs['action'] == 'pre_remove':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballThreePoint.objects.get(pk=pk).player
            statistic = BasketballPlayerHalfSeasonStatistics.objects.get(player=player, half_season=match.half_season)
            statistic.three_point_number -= 1
            statistic.save()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballThreePoint.objects.get(pk=pk).player
            statistic, created = BasketballPlayerHalfSeasonStatistics.objects.get_or_create(player=player,
                                                                                            half_season=match.half_season)
            statistic.three_point_number += 1
            statistic.save()


@receiver(m2m_changed, sender=BasketballMatch.team1_faults.through)
@receiver(m2m_changed, sender=BasketballMatch.team2_faults.through)
def save_basketball_player_half_season_faults(sender, **kwargs):
    match = kwargs['instance']
    if kwargs['action'] == 'pre_remove':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballFault.objects.get(pk=pk).player
            statistic = BasketballPlayerHalfSeasonStatistics.objects.get(player=player, half_season=match.half_season)
            statistic.faults_number -= 1
            statistic.save()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballFault.objects.get(pk=pk).player
            statistic, created = BasketballPlayerHalfSeasonStatistics.objects.get_or_create(player=player,
                                                                                            half_season=match.half_season)
            statistic.faults_number += 1
            statistic.save()


@receiver(m2m_changed, sender=BasketballMatch.team1_rebounds.through)
@receiver(m2m_changed, sender=BasketballMatch.team2_rebounds.through)
def save_basketball_player_half_season_rebounds(sender, **kwargs):
    match = kwargs['instance']
    if kwargs['action'] == 'pre_remove':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballRebound.objects.get(pk=pk).player
            statistic = BasketballPlayerHalfSeasonStatistics.objects.get(player=player, half_season=match.half_season)
            statistic.rebounds_numbers -= 1
            statistic.save()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballRebound.objects.get(pk=pk).player
            statistic, created = BasketballPlayerHalfSeasonStatistics.objects.get_or_create(player=player,
                                                                                            half_season=match.half_season)
            statistic.rebounds_numbers += 1
            statistic.save()


@receiver(m2m_changed, sender=BasketballMatch.team1_penalty_faults.through)
@receiver(m2m_changed, sender=BasketballMatch.team2_penalty_faults.through)
def save_basketball_player_half_season_penalty_faults(sender, **kwargs):
    match = kwargs['instance']
    if kwargs['action'] == 'pre_remove':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballPenaltyFault.objects.get(pk=pk).player
            statistic = BasketballPlayerHalfSeasonStatistics.objects.get(player=player, half_season=match.half_season)
            statistic.penalty_faults_number -= 1
            statistic.save()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballPenaltyFault.objects.get(pk=pk).player
            statistic, created = BasketballPlayerHalfSeasonStatistics.objects.get_or_create(player=player,
                                                                                            half_season=match.half_season)
            statistic.penalty_faults_number += 1
            statistic.save()


class TeamMatchPlayersList(PolymorphicModel):
    main_substitute = models.BooleanField()  # 1 for main 0 for substitute

    def team(self):
        pass

    def player(self):
        pass

    def match(self):
        pass


class FootballMatchPlayersList(TeamMatchPlayersList):
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)


class BasketballMatchPlayersList(TeamMatchPlayersList):
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)


@receiver(m2m_changed, sender=FootballMatch.team1_substitute_players.through)
@receiver(m2m_changed, sender=FootballMatch.team2_substitute_players.through)
@receiver(m2m_changed, sender=FootballMatch.team1_main_players.through)
@receiver(m2m_changed, sender=FootballMatch.team2_main_players.through)
def save_team_match_members(sender, **kwargs):
    team = kwargs[
        'instance'].team1 if sender == FootballMatch.team1_substitute_players.through or sender == FootballMatch.team1_main_players.through else \
        kwargs['instance'].team2
    main = True if sender == FootballMatch.team1_main_players.through or sender == FootballMatch.team2_main_players.through else False
    if kwargs['action'] == 'post_remove':
        pks = kwargs['pk_set']

        for pk in pks:
            player = FootballPlayer.objects.get(pk=pk)
            FootballMatchPlayersList.objects.get(player=player, match=kwargs['instance'],
                                                 team=team, main_substitute=main).delete()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            player = FootballPlayer.objects.get(pk=pk)
            FootballMatchPlayersList.objects.create(player=player, match=kwargs['instance'],
                                                    team=team, main_substitute=main)


@receiver(m2m_changed, sender=BasketballMatch.team1_substitute_players.through)
@receiver(m2m_changed, sender=BasketballMatch.team2_substitute_players.through)
@receiver(m2m_changed, sender=BasketballMatch.team1_main_players.through)
@receiver(m2m_changed, sender=BasketballMatch.team2_main_players.through)
def save_team_match_members(sender, **kwargs):
    team = kwargs[
        'instance'].team1 if sender == BasketballMatch.team1_substitute_players.through or sender == BasketballMatch.team1_main_players.through else \
        kwargs['instance'].team2
    main = True if sender == BasketballMatch.team1_main_players.through or sender == BasketballMatch.team2_main_players.through else False
    if kwargs['action'] == 'post_remove':
        pks = kwargs['pk_set']

        for pk in pks:
            player = BasketballPlayer.objects.get(pk=pk)
            BasketballMatchPlayersList.objects.get(player=player, match=kwargs['instance'],
                                                   team=team, main_substitute=main).delete()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            player = BasketballPlayer.objects.get(pk=pk)
            BasketballMatchPlayersList.objects.create(player=player, match=kwargs['instance'],
                                                      team=team, main_substitute=main)


class HalfSeasonLeagueTeams(PolymorphicModel):
    def team(self):
        pass

    def league(self):
        pass

    def half_season(self):
        pass

    def get_json(self):
        pass


class FootballHalfSeasonLeagueTeams(HalfSeasonLeagueTeams):
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    league = models.ForeignKey(FootballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(HalfSeason, on_delete=models.CASCADE)

    @staticmethod
    def get_header():
        return ['تیم', 'بازیها', 'برد', 'مساوی', 'باخت', 'گل زده', 'گل خورده', 'تفاضل گل', 'امتیاز']

    def get_json(self):
        # played = FootballLeague.footballmatch_set.filter(Q(team1=self.team) | Q(team2=self.team)).count()
        # won = FootballLeague.footballmatch_set.filter(
        #     Q(Q(team1=self.team) & Q(result=1)) | Q(Q(team2=self.team) & Q(result=-1))).count()
        # drawn = FootballLeague.footballmatch_set.filter(
        #     Q(Q(team1=self.team) | Q(team2=self.team)) & Q(result=0)).count()
        # lost = FootballLeague.footballmatch_set.filter(
        #     Q(Q(team1=self.team) & Q(result=-1)) | Q(Q(team2=self.team) & Q(result=1))).count()
        matches1 = FootballMatch.objects.filter(half_season=self.half_season, league=self.league, team1=self.team)
        matches2 = FootballMatch.objects.filter(half_season=self.half_season, league=self.league, team2=self.team)
        played = matches1.count() + matches2.count()
        won = 0
        drawn = 0
        lost = 0
        GF = 0
        GA = 0
        # won = matches1.filter(result=1).count() + matches2.filter(result=-1).count()
        for match in matches1:
            GF += match.team1_goals.count()
            GA += match.team2_goals.count()
            if match.result == 1:
                won += 1
            elif match.result == 0:
                drawn += 1
            else:
                lost += 1
        for match in matches2:
            GF += match.team2_goals.count()
            GA += match.team1_goals.count()
            if match.result == -1:
                won += 1
            elif match.result == 0:
                drawn += 1
            else:
                lost += 1
        # drawn = matches1.filter(result=0).count() + matches2.filter(result=0).count()
        # lost = played - won - drawn

        # for match in matches1:
        #     GF += match.team1_goals.count()
        #     GA += match.team2_goals.count()
        # for match in matches2:
        #     GF += match.team2_goals.count()
        #     GA += match.team1_goals.count()
        return {
            'teamInfo': [
                {'featureName': 'teamName', 'featureValue': self.team.name, 'featureLink': get_url('team', self.team)},
                {'featureName': 'matches', 'featureValue': played, 'featureLink': None},
                {'featureName': 'win', 'featureValue': won, 'featureLink': None},
                {'featureName': 'draw', 'featureValue': drawn, 'featureLink': None},
                {'featureName': 'loose', 'featureValue': lost, 'featureLink': None},
                {'featureName': 'goalZ', 'featureValue': GF, 'featureLink': None},
                {'featureName': 'goalK', 'featureValue': GA, 'featureLink': None},
                {'featureName': 'goalSub', 'featureValue': GF - GA, 'featureLink': None},
                {'featureName': 'score', 'featureValue': (won * 3) + drawn, 'featureLink': None},
            ]
        }


class BasketballHalfSeasonLeagueTeams(HalfSeasonLeagueTeams):
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    league = models.ForeignKey(BasketballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(HalfSeason, on_delete=models.CASCADE)

    @staticmethod
    def get_header():
        return ['تیم', 'بازیها', 'برد', 'باخت', 'گل زده', 'گل خورده', 'تفاضل گل', 'امتیاز']

    def get_json(self):
        return {
            'teamInfo': [
                {'featureName': 'teamName', 'featureValue': self.team.name, 'featureLink': get_url('team', self.team)},
                {'featureName': 'matches', 'featureValue': self.played, 'featureLink': None},
                {'featureName': 'win', 'featureValue': self.won, 'featureLink': None},
                {'featureName': 'loose', 'featureValue': self.lost, 'featureLink': None},
                {'featureName': 'goalZ', 'featureValue': self.GF, 'featureLink': None},
                {'featureName': 'goalK', 'featureValue': self.GA, 'featureLink': None},
                {'featureName': 'goalSub', 'featureValue': self.GD, 'featureLink': None},
                {'featureName': 'score', 'featureValue': self.points, 'featureLink': None},
            ]
        }


@receiver(m2m_changed, sender=FootballLeague.teams.through)
def save_league_teams(sender, **kwargs):
    if kwargs['action'] == 'post_remove':
        pks = kwargs['pk_set']

        for pk in pks:
            team = FootballTeam.objects.get(pk=pk)
            FootballHalfSeasonLeagueTeams.objects.get(league=kwargs['instance'],
                                                      half_season=CurrentHalfSeason.objects.last().current_half_season,
                                                      team=team).delete()
    if kwargs['action'] == 'post_add':
        pks = kwargs['pk_set']
        for pk in pks:
            team = FootballTeam.objects.get(pk=pk)
            FootballHalfSeasonLeagueTeams.objects.create(league=kwargs['instance'],
                                                         half_season=CurrentHalfSeason.objects.last().current_half_season,
                                                         team=team)


class NewsTags(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    url = models.URLField()

    def get_json(self):
        return {'name': self.name, 'link': self.url}


class NewsSources(models.Model):
    def __str__(self):
        return self.name

    name = models.CharField(max_length=50)
    url = models.URLField()

    def get_json(self):
        return {'name': self.name, 'link': self.url}


class SiteUser(User):
    favorite_home_news_number = models.SmallIntegerField(null=True)
    favorite_teams = models.ManyToManyField(Team)
    favorite_players = models.ManyToManyField(Player)
    confirm_id = models.CharField(max_length=30, editable=False, default='')
    confirmed = models.BooleanField(default=False)


class News(PolymorphicModel):
    def __str__(self):
        return self.title

    def get_url_id(self):
        return self.title, self.uid

    def get_summary_json(self):
        pass

    def get_json(self):
        pass

    def get_slides_json(self):
        pass

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    title = models.CharField(max_length=100)
    body_text = models.TextField()
    date_time = models.DateTimeField()
    tags = models.ManyToManyField(NewsTags, blank=True)
    sources = models.ManyToManyField(NewsSources, blank=True)
    main_images = models.ForeignKey(Photos, null=True, on_delete=models.SET_NULL)
    more_images = models.ManyToManyField(Photos, related_name='news1', blank=True)
    # league = models.ManyToManyField(League)
    # match = models.ManyToManyField(Match)
    # player = models.ManyToManyField(Player)
    # team = models.ManyToManyField(Team)


class FootballNews(News):
    def get_summary_json(self):
        return (
            {
                'title': self.title,
                'link': get_url('news', self),
            }
        )

    def get_json(self):
        json = {
            'moreImagesUrl': [],
            'image_url': self.main_images.photo.url,
            'title': self.title,
            'dateTime': self.date_time.strftime("%H:%M:%S  %d-%m-%Y"),
            'sources': [],
            'tages': [],
            'body': self.body_text,
            'comments': None
        }
        more_images = self.more_images.all()
        sources = self.sources.all()
        tags = self.tags.all()
        for image in more_images:
            json['moreImagesUrl'].append(image.photo.url)
        for source in sources:
            json['sources'].append(source.get_json())
        for tag in tags:
            json['tages'].append(tag.get_json())
        return json

    def get_slides_json(self):
        return (
            {
                'title': self.title,
                'link': get_url('news', self),
                'image': self.main_images.photo.url,
                'headLine': self.body_text[:100]
            }
        )


class BasketballNews(News):
    def get_summary_json(self):
        return (
            {
                'title': self.title,
                'link': get_url('news', self),
            }
        )

    def get_json(self):
        json = {
            'moreImagesUrl': [],
            'image_url': self.main_images.photo.url,
            'title': self.title,
            'dateTime': self.date_time.strftime("%H:%M:%S  %d-%m-%Y"),
            'sources': [],
            'tages': [],
            'body': self.body_text,
            'comments': None
        }
        more_images = self.more_images.all()
        sources = self.sources.all()
        tags = self.tags.all()
        for image in more_images:
            json['moreImagesUrl'].append(image.photo.url)
        for source in sources:
            json['sources'].append(source.get_json())
        for tag in tags:
            json['tages'].append(tag.get_json())
        return json

    def get_slides_json(self):
        return (
            {
                'title': self.title,
                'link': get_url('news', self),
                'image': self.main_images.url,
                'headLine': self.body_text[:100]
            }
        )


class Comments(models.Model):
    def __str__(self):
        return self.text

    text = models.CharField(max_length=400)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()
    news = models.ForeignKey(News, on_delete=models.CASCADE)
