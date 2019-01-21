import datetime
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from polymorphic.models import PolymorphicModel


def get_url(action, model):
    return 'http://127.0.0.1:3000/sport3/{0}/{1}'.format(action, model.get_url_id())


# Create your models here.


class HalfSeason(PolymorphicModel):
    def __str__(self):
        return self.name

    def get_url_id(self):
        return self.name + str(self.uid)

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    half = models.BooleanField()
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = (("name",),)


class FootballHalfSeason(HalfSeason):
    pass


class BasketballHalfSeason(HalfSeason):
    pass


class League(PolymorphicModel):
    def __str__(self):
        return self.name

    def get_url_id(self):
        return self.name + str(self.uid)

    def half_season(self):
        pass

    def get_json(self):
        pass

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = (("name",),)


class FootballLeague(League):
    half_season = models.ManyToManyField(FootballHalfSeason)

    def get_json(self):
        season = []
        half_season = self.half_season.all()
        for half_season in half_season:
            season.append(str(self.name) + '(' + str(half_season.name) + ')')
        json = {
            'leagueName': self.name,
            'sessions': season
        }
        return json


class BasketballLeague(League):
    half_season = models.ManyToManyField(BasketballHalfSeason)

    def get_json(self):
        season = []
        half_season = self.half_season.all()
        for half_season in half_season:
            season.append(str(self.name) + '(' + str(half_season.name) + ')')
        json = {
            'leagueName': self.name,
            'sessions': season
        }
        return json


class Team(PolymorphicModel):
    def __str__(self):
        return self.name

    def get_url_id(self):
        return self.name + str(self.uid)

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=40)

    class Meta:
        unique_together = (("name",),)


class FootballTeam(Team):
    pass


class BasketballTeam(Team):
    pass


class Player(PolymorphicModel):
    def __str__(self):
        return self.name

    def get_url_id(self):
        return self.name + str(self.uid)

    def get_json(self):
        pass

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=40)
    birth_date = models.DateTimeField()
    photo = models.ImageField(null=True, blank=True)


class FootballPlayer(Player):
    position = models.CharField(max_length=20)

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


class BasketballPlayer(Player):
    position = models.CharField(max_length=20)

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


class Match(PolymorphicModel):
    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    date_time = models.DateTimeField()

    def __str__(self):
        return self.team1.name + '-' + self.team2.name

    @property
    def result(self):
        pass

    def get_url_id(self):
        return self.team1.name + '-' + self.team2.name + str(self.uid)

    def team1(self):
        pass

    def team2(self):
        pass

    def best_player(self):
        pass

    def league(self):
        pass

    def half_season(self):
        pass

    def get_summary_json(self):
        pass

    def get_json(self):
        pass


class FootballMatch(Match):
    best_player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    league = models.ForeignKey(FootballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(FootballHalfSeason, on_delete=models.CASCADE)
    team1 = models.ForeignKey(FootballTeam, related_name='home_matches', on_delete=models.CASCADE)
    team2 = models.ForeignKey(FootballTeam, related_name='away_matches', on_delete=models.CASCADE)
    team1_corners = models.PositiveSmallIntegerField()
    team2_corners = models.PositiveSmallIntegerField()
    team1_faults = models.PositiveSmallIntegerField()
    team2_faults = models.PositiveSmallIntegerField()
    team1_goals = models.PositiveSmallIntegerField()
    team2_goals = models.PositiveSmallIntegerField()
    team1_goal_positions = models.PositiveSmallIntegerField()
    team2_goal_positions = models.PositiveSmallIntegerField()
    team1_assists = models.PositiveSmallIntegerField()
    team2_assists = models.PositiveSmallIntegerField()

    @property
    def result(self):
        team1_goals = self.team1_goals
        team2_goals = self.team2_goals
        return 0 if team1_goals == team2_goals else -1 if team1_goals < team2_goals else 1

    def get_json(self):
        team1_goals = self.team1_goals
        team2_goals = self.team2_goals
        score, status = (3, 'برد') if team1_goals > team2_goals else (1, 'مساوی') if team1_goals == team2_goals else (
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

    def get_summary_json(self):
        return (
            {
                'team1Name': self.team1.name,
                'team1Link': get_url('team', self.team1),
                'team2Name': self.team2.name,
                'team2Link': get_url('team', self.team2),
                'team1Goal': self.team1_goals,
                'team2Goal': self.team2_goals,
                'date': 'امروز' if self.date_time.date() == datetime.datetime.now().date()
                else 'دیروز' if self.date_time.date() == datetime.datetime.now().date() - datetime.timedelta(days=1)
                else 'فردا' if self.date_time.date() == datetime.datetime.now().date() - datetime.timedelta(days=1)
                else self.date_time.date()
            }
        )


class BasketballMatch(Match):
    best_player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    league = models.ForeignKey(BasketballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(BasketballHalfSeason, on_delete=models.CASCADE)
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

    @property
    def result(self):
        team1_scores = self.team1_final_score
        team2_scores = self.team2_final_score
        return 0 if team1_scores == team2_scores else -1 if team1_scores < team2_scores else 1

    def get_json(self):
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


class TeamHalfSeasonMembers(PolymorphicModel):
    def player(self):
        pass

    def team(self):
        pass

    def half_season(self):
        pass


class FootballTeamHalfSeasonMembers(TeamHalfSeasonMembers):
    player = models.ManyToManyField(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    half_season = models.ManyToManyField(FootballHalfSeason, on_delete=models.CASCADE)


class BasketballTeamHalfSeasonMembers(TeamHalfSeasonMembers):
    player = models.ManyToManyField(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    half_season = models.ManyToManyField(BasketballHalfSeason, on_delete=models.CASCADE)


class Substitute(PolymorphicModel):
    time = models.PositiveSmallIntegerField()

    def match(self):
        pass

    def player(self):
        pass


class FootballSubstitute(Substitute):
    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player_in = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    player_out = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)


class BasketballSubstitute(Substitute):
    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player_in = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    player_out = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)


class MatchPlayersList(PolymorphicModel):
    main_substitute = models.BooleanField()  # 1 for main 0 for substitute

    def team(self):
        pass

    def player(self):
        pass

    def match(self):
        pass


class FootballMatchPlayersList(MatchPlayersList):
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    player = models.ManyToManyField(FootballPlayer, on_delete=models.CASCADE)
    match = models.ManyToManyField(FootballMatch, on_delete=models.CASCADE)


class BasketballMatchPlayersList(MatchPlayersList):
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    player = models.ManyToManyField(BasketballPlayer, on_delete=models.CASCADE)
    match = models.ManyToManyField(BasketballMatch, on_delete=models.CASCADE)


class HalfSeasonLeagueTeams(PolymorphicModel):
    played = models.PositiveSmallIntegerField()
    won = models.PositiveSmallIntegerField()
    lost = models.PositiveSmallIntegerField()
    GF = models.PositiveSmallIntegerField()  # gole zadeh
    GA = models.PositiveSmallIntegerField()  # gole khordeh
    GD = models.SmallIntegerField()  # tafazoleh gol
    points = models.PositiveSmallIntegerField()

    def team(self):
        pass

    def league(self):
        pass

    def half_season(self):
        pass

    def get_json(self):
        pass


class FootballHalfSeasonLeagueTeams(HalfSeasonLeagueTeams):
    drawn = models.PositiveSmallIntegerField()
    team = models.ManyToManyField(FootballTeam)
    league = models.ForeignKey(FootballLeague)
    half_season = models.ForeignKey(FootballHalfSeason)

    def get_json(self):
        json = {
            'leagueName': self.league.name + '(' + half_season.name + ')',
            'tableName': league.name,
            'header': ['تیم', 'بازیها', 'برد', 'مساوی', 'باخت', 'گل زده', 'گل خورده', 'تفاضل گل', 'امتیاز'],
            'tableData': [],
        }

        for team in self.team.all():
            matches = FootballMatch.objects.filter(
                Q(League=self.league, HalfSeason=self.half_season) & Q(Q(team1=team) | Q(team2=team)))
            matches_count = matches.count()
            win = matches.filter(result=1).count()
            draw = matches.filter(result=0).count()
            loose = matches.filter(result=-1).count()
            goalZ = 0
            goalK = 0
            for match in matches:
                goalZ += match.team1_goals if match.team1 == team else match.team2_goals
                goalK += match.team2_goals if match.team1 == team else match.team1_goals
            json['tableData'].append(
                {
                    'teamInfo': [
                        {'featureName': 'teamName', 'featureValue': team.name,
                         'featureLink': get_url('team', team)},
                        {'featureName': 'matches', 'featureValue': matches_count(), 'featureLink': None},
                        {'featureName': 'win', 'featureValue': win, 'featureLink': None},
                        {'featureName': 'draw', 'featureValue': draw, 'featureLink': None},
                        {'featureName': 'loose', 'featureValue': loose, 'featureLink': None},
                        {'featureName': 'goalZ', 'featureValue': goalZ, 'featureLink': None},
                        {'featureName': 'goalK', 'featureValue': goalK, 'featureLink': None},
                        {'featureName': 'goalSub', 'featureValue': goalZ - goalK, 'featureLink': None},
                        {'featureName': 'score', 'featureValue': (win * 3) + draw, 'featureLink': None},
                    ]
                }
            )


class BasketballHalfSeasonLeagueTeams(HalfSeasonLeagueTeams):
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    league = models.ForeignKey(BasketballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(BasketballHalfSeason, on_delete=models.CASCADE)

    def get_json(self, league, half_season):
        json = {
            'tableData': [],
            'leagueName': self.league.name + self.half_season.name,
            'tableName': self.league.name,
            'header': ['تیم', 'بازیها', 'برد', 'مساوی', 'باخت', 'گل زده', 'گل خورده', 'تفاضل گل', 'امتیاز'],
        }

        for team in self.team.all():
            matches = BasketballMatch.objects.filter(
                Q(League=self.league, HalfSeason=self.half_season) & Q(Q(team1=team) | Q(team2=team)))
            matches_count = matches.count()
            win = matches.filter(result=1).count()
            draw = matches.filter(result=0).count()
            loose = matches.filter(result=-1).count()
            goalZ = 0
            goalK = 0
            for match in matches:
                goalZ += match.team1_goals if match.team1 == team else match.team2_goals
                goalK += match.team2_goals if match.team1 == team else match.team1_goals
            json['tableData'].append(
                {
                    'teamInfo': [
                        {'featureName': 'teamName', 'featureValue': team.name,
                         'featureLink': get_url('team', team)},
                        {'featureName': 'matches', 'featureValue': matches_count(), 'featureLink': None},
                        {'featureName': 'win', 'featureValue': win, 'featureLink': None},
                        {'featureName': 'draw', 'featureValue': draw, 'featureLink': None},
                        {'featureName': 'loose', 'featureValue': loose, 'featureLink': None},
                        {'featureName': 'goalZ', 'featureValue': goalZ, 'featureLink': None},
                        {'featureName': 'goalK', 'featureValue': goalK, 'featureLink': None},
                        {'featureName': 'goalSub', 'featureValue': goalZ - goalK, 'featureLink': None},
                        {'featureName': 'score', 'featureValue': (win * 3) + draw, 'featureLink': None},
                    ]
                }
            )


class FootballGoal(models.Model):
    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballAssist(models.Model):
    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballCard(models.Model):
    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballPenalty(models.Model):
    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballThreePoint(models.Model):
    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballTwoPoint(models.Model):
    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballPenaltyFault(models.Model):
    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballPenaltyFailed(models.Model):
    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class Photos(models.Model):
    photo = models.ImageField()


class NewsTags(models.Model):
    name = models.CharField(max_length=50)


class NewsSources(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField()


class SiteUser(User):
    favorite_home_news_number = models.SmallIntegerField()
    favorite_teams = models.ManyToManyField(Team)
    favorite_players = models.ManyToManyField(Player)


class Comments(models.Model):
    text = models.CharField(max_length=400)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class News(PolymorphicModel):
    def get_url_id(self):
        return self.title + str(self.uid)

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    title = models.CharField(max_length=100)
    body_text = models.TextField()
    date_time = models.DateTimeField()
    tags = models.ManyToManyField(NewsTags)
    sources = models.ManyToManyField(NewsSources)
    main_images = models.ForeignKey(Photos, on_delete=models.CASCADE)
    more_images = models.ManyToManyField(Photos, related_name='news1')
    league = models.ManyToManyField(League)
    match = models.ManyToManyField(Match)
    player = models.ManyToManyField(Player)
    team = models.ManyToManyField(Team)

    def get_summary_json(self):
        pass


class FootballNews(News):
    def get_summary_json(self):
        return (
            {
                'title': self.title,
                'link': get_url('news', self),
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
