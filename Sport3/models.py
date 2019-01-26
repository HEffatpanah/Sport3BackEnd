import datetime
import uuid
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models import Q
from django.db.models.signals import *
from django.dispatch import receiver
from polymorphic.models import PolymorphicModel
from smart_selects.db_fields import ChainedManyToManyField

from Backend import settings

private_storage = FileSystemStorage(location=settings.PRIVATE_STORAGE_ROOT)


def get_url(action, model):
    aux = model.get_url_id()
    return 'http://127.0.0.1:3000/sport3/{0}/{1}/{2}'.format(action, aux[0], aux[1])


# Create your models here.


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
        aux_json['link'] = get_url('league', half_season)
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
            aux_json['link'] = get_url('leagues', half_season)
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
    current_half_season = models.ForeignKey(HalfSeason, on_delete=models.CASCADE)


class DefaultLeague(models.Model):
    default_league = models.ForeignKey(League, on_delete=models.CASCADE)


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
            'tableHeader': FootballPlayer.get_header(),
            'tableBody': [],
        }
        for team_member in team_members:
            json['tableBody'].append(team_member.get_json())
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
        team_members = BasketballTeamHalfSeasonMembers.objects.filter(team=self)
        json = {
            'tableHeader': BasketballPlayer.get_header(),
            'tableBody': [],
        }
        for team_member in team_members:
            json['tableBody'].append(team_member.player.get_json())
        return json

    def get_matches_json(self):
        matches = BasketballMatch.objects.filter(Q(team1=self) | Q(team2=self))[:20]
        json = []
        for match in matches:
            json.append(match.get_json())
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

    @staticmethod
    def get_header():
        pass

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=40)
    birth_date = models.DateTimeField()
    photo = models.ImageField(storage=private_storage, null=True, blank=True)


class FootballPlayer(Player):
    position = models.CharField(max_length=20)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE, null=True, blank=True)

    @staticmethod
    def get_header():
        return ['نام', 'سن', 'پست', 'عکس']

    def get_json(self):
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


class BasketballPlayer(Player):
    position = models.CharField(max_length=20)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE, null=True, blank=True)

    @staticmethod
    def get_header():
        return ['نام', 'سن', 'پست', 'عکس']

    def get_json(self):
        return (
            {
                'memberInfo': [
                    {'featureName': 'playerName', 'featureValue': self.name, 'featureLink': get_url('player', self)},
                    {'featureName': 'age', 'featureValue': datetime.datetime.now().year - self.birth_date.year,
                     'featureLink': None},
                    {'featureName': 'position', 'featureValue': self.position, 'featureLink': None},
                    {'featureName': 'photo',
                     'featureValue': self.photo,
                     'featureLink': None},
                ]
            }
        )


@receiver(post_save, sender=FootballPlayer)
def save_team_half_season_members(sender, **kwargs):
    print('\n\n\n\n', kwargs['instance'].team.name, '\n\n\n')
    try:
        FootballTeamHalfSeasonMembers.objects.get(player=kwargs['instance'],
                                                  half_season=CurrentHalfSeason.objects.last().current_half_season).delete()
    except:
        pass
    FootballTeamHalfSeasonMembers.objects.create(player=kwargs['instance'], team=kwargs['instance'].team,
                                                 half_season=CurrentHalfSeason.objects.last().current_half_season)


@receiver(pre_delete, sender=FootballPlayer)
def delete_team_half_season_members(sender, **kwargs):
    print('\n\n\n\n', kwargs['instance'].team.name, '\n\n\n')

    aux = FootballTeamHalfSeasonMembers.objects.filter(player=kwargs['instance'])
    for i in aux:
        i.delete()


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
        return self.player.name + '(' + self.team.name + ')'

    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballCard(models.Model):
    def __str__(self):
        return self.player.name

    color = models.CharField(max_length=256,
                             choices=[('first yellow', 'first yellow'), ('second yellow', 'second yellow'),
                                      ('red', 'red')], default='yellow')
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballPenalty(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballThreePoint(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballTwoPoint(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballPenaltyFault(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballPenaltyFailed(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class Match(PolymorphicModel):
    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    date_time = models.DateTimeField()
    half_season = models.ForeignKey(HalfSeason, on_delete=models.CASCADE)

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


class FootballMatch(Match):
    best_player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    league = models.ForeignKey(FootballLeague, on_delete=models.CASCADE)
    team1 = models.ForeignKey(FootballTeam, related_name='home_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(FootballTeam, related_name='away_matches', on_delete=models.CASCADE)
    team1_corners = models.PositiveSmallIntegerField()
    team2_corners = models.PositiveSmallIntegerField()
    team1_faults = models.PositiveSmallIntegerField()
    team2_faults = models.PositiveSmallIntegerField()
    team1_goals = models.ManyToManyField(Goal, related_name='home_match')
    team2_goals = models.ManyToManyField(Goal, related_name='away_match')
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
    team1_cards = models.ManyToManyField(FootballCard, related_name='home_match')
    team2_cards = models.ManyToManyField(FootballCard, related_name='away_match')
    team1_penalty = models.ManyToManyField(FootballPenalty, related_name='home_match')
    team2_penalty = models.ManyToManyField(FootballPenalty, related_name='away_match')
    team1_assists = models.ManyToManyField(FootballAssist, related_name='home_match')
    team2_assists = models.ManyToManyField(FootballAssist, related_name='away_match')
    team1_substitutes = models.ManyToManyField(FootballSubstitute, related_name='home_match')
    team2_substitutes = models.ManyToManyField(FootballSubstitute, related_name='away_match')

    @property
    def result(self):
        team1_goals = self.team1_goals.count()
        team2_goals = self.team2_goals.count()
        return 0 if team1_goals == team2_goals else -1 if team1_goals < team2_goals else 1

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


class BasketballMatch(Match):
    best_player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    league = models.ForeignKey(BasketballLeague, on_delete=models.CASCADE)
    team1 = models.ForeignKey(BasketballTeam, related_name='home_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(BasketballTeam, related_name='away_matches', on_delete=models.CASCADE)
    team1_two_points = models.PositiveSmallIntegerField()
    team2_two_points = models.PositiveSmallIntegerField()
    team1_three_points = models.PositiveSmallIntegerField()
    team2_three_points = models.PositiveSmallIntegerField()
    team1_faults = models.PositiveSmallIntegerField()
    team2_faults = models.PositiveSmallIntegerField()
    team1_penalty_faults = models.PositiveSmallIntegerField()
    team2_penalty_faults = models.PositiveSmallIntegerField()
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
    team1_rebounds = models.PositiveSmallIntegerField()
    team2_rebounds = models.PositiveSmallIntegerField()
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

    @property
    def result(self):
        team1_scores = self.team1_final_score
        team2_scores = self.team2_final_score
        return 0 if team1_scores == team2_scores else -1 if team1_scores < team2_scores else 1

    def get_json(self, team):
        team1_final_score = self.team1_final_score
        team2_final_score = self.team2_final_score
        score, status = (3, 'برد') if team1_final_score > team2_final_score else (
            1, 'مساوی') if team1_final_score == team2_final_score else (0, 'باخت')
        return (
            {
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


class HalfSeasonLeagueTeams(PolymorphicModel):
    # played = models.PositiveSmallIntegerField(default=0)
    # won = models.PositiveSmallIntegerField(default=0)
    # lost = models.PositiveSmallIntegerField(default=0)
    # GF = models.PositiveSmallIntegerField(default=0)  # gole zadeh
    # GA = models.PositiveSmallIntegerField(default=0)  # gole khordeh
    # GD = models.SmallIntegerField(default=0)  # tafazoleh gol
    # points = models.PositiveSmallIntegerField(default=0)

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
            if match.result == 1:
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


class Photos(models.Model):
    def __str__(self):
        return self.photo.name

    photo = models.ImageField(storage=private_storage)


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
    favorite_home_news_number = models.SmallIntegerField()
    favorite_teams = models.ManyToManyField(Team)
    favorite_players = models.ManyToManyField(Player)


class News(PolymorphicModel):
    def __str__(self):
        return self.title

    def get_url_id(self):
        return self.title, self.uid

    def get_summary_json(self):
        pass

    def get_json(self):
        pass

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    title = models.CharField(max_length=100)
    body_text = models.TextField()
    date_time = models.DateTimeField()
    tags = models.ManyToManyField(NewsTags)
    sources = models.ManyToManyField(NewsSources)
    main_images = models.ForeignKey(Photos, null=True, on_delete=models.SET_NULL)
    more_images = models.ManyToManyField(Photos, related_name='news1')
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


class Comments(models.Model):
    def __str__(self):
        return self.text

    text = models.CharField(max_length=400)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()
    news = models.ForeignKey(News, on_delete=models.CASCADE)
