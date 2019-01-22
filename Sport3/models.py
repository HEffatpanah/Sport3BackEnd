import datetime
import uuid
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Q
from polymorphic.models import PolymorphicModel


def get_url(action, model):
    aux = model.get_url_id()
    print('http://127.0.0.1:3000/sport3/{0}/{1}/{2}'.format(action, aux[0], aux[1]))
    return 'http://127.0.0.1:3000/sport3/{0}/{1}/{2}'.format(action, aux[0], aux[1])


# Create your models here.


class HalfSeason(PolymorphicModel):
    def __str__(self):
        return self.name

    def get_url_id(self):
        return self.name, self.uid

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
        return self.name, self.uid

    def half_season(self):
        pass

    def get_half_seasons_json(self):
        pass

    def get_teams_json(self):
        pass

    def get_matches_json(self):
        pass

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = (("name",),)


class FootballLeague(League):
    half_season = models.ManyToManyField(FootballHalfSeason)

    def get_matches_json(self):
        json = {
            'tableHeader': ['نام تیم', 'نتیجه', 'نام تیم', 'تاریخ'],
            'tableBody': []
        }
        half_seasons = self.half_season.all()
        for half_season in half_seasons:
            aux = {'half_season': self.name + '(' + str(half_season.name) + ')', 'matches': []}
            matches = FootballMatch.objects.filter(league=self, half_season=half_season)
            for match in matches:
                aux['matches'].append(match.get_summary_json())
            json['tableBody'].append(aux)
        return json

    def get_teams_json(self):
        json = {
            'leagueName': None,
            'tableName': self.name,
            'header': FootballHalfSeasonLeagueTeams.get_header(),
            'tableData': None
        }
        half_seasons = self.half_season.all()
        for half_season in half_seasons:
            json['leagueName'] = self.name + '(' + half_season.name + ')'
            teams = FootballHalfSeasonLeagueTeams.objects.filter(half_season=half_season, league=self)
            for team in teams:
                json['tableData'].append(team.get_json())
        return json

    def get_half_seasons_json(self):
        half_season = self.half_season.all()
        for half_season in half_season:
            half_season.append(str(self.name) + '(' + str(half_season.name) + ')')
        json = {
            'leagueName': self.name,
            'sessions': half_season
        }
        return json


class BasketballLeague(League):
    half_season = models.ManyToManyField(BasketballHalfSeason)

    def get_matches_json(self):
        json = {
            'tableHeader': ['نام تیم', 'نتیجه', 'نام تیم', 'تاریخ'],
            'tableBody': []
        }
        matches = BasketballMatch.objects.filter(league=self)
        for match in matches:
            json['tableBody'].append(match.get_summary_json())
        return json

    def get_teams_json(self):
        json = {
            'leagueName': None,
            'tableName': self.name,
            'header': BasketballHalfSeasonLeagueTeams.get_header(),
            'tableData': None
        }
        half_seasons = self.half_season.all()
        for half_season in half_seasons:
            json['leagueName'] = self.name + '(' + half_season.name + ')'
            teams = BasketballHalfSeasonLeagueTeams.objects.filter(half_season=half_season, league=self)
            for team in teams:
                json['tableData'].append(team.get_json())
        return json

    def get_half_seasons_json(self):
        half_season = self.half_season.all()
        for half_season in half_season:
            half_season.append(str(self.name) + '(' + str(half_season.name) + ')')
        json = {
            'leagueName': self.name,
            'sessions': half_season
        }
        return json


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

    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    name = models.CharField(max_length=40)

    class Meta:
        unique_together = (("name",),)


class FootballTeam(Team):
    def get_members_json(self):
        team_members = FootballTeamHalfSeasonMembers.objects.filter(team=self)
        print(team_members.count())
        json = {
            'tableHeader': FootballPlayer.get_header(),
            'tableBody': [],
        }
        for team_member in team_members:
            json['tableBody'].append(team_member.player.get_json())
        return json

    def get_matches_json(self):
        matches = FootballMatch.objects.filter(Q(team1=self) | Q(team2=self))[:20]
        json = []
        for match in matches:
            json.append(match.get_json())
        return json

    def get_news_json(self):  # ####################################################################################
        news = FootballNews.objects.filter()[:20]
        json = []
        for news in news:
            json.append(news.get_summary_json())
        return json


class BasketballTeam(Team):
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
    photo = models.ImageField(null=True, blank=True)


class FootballPlayer(Player):
    position = models.CharField(max_length=20)

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


class Match(PolymorphicModel):
    uid = models.UUIDField(default=uuid.uuid4(), editable=False)
    date_time = models.DateTimeField()

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

    # def half_season(self):
    #     pass


class FootballTeamHalfSeasonMembers(TeamHalfSeasonMembers):
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    # half_season = models.ForeignKey(FootballHalfSeason, on_delete=models.CASCADE)


class BasketballTeamHalfSeasonMembers(TeamHalfSeasonMembers):
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    # half_season = models.ForeignKey(BasketballHalfSeason, on_delete=models.CASCADE)


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
    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player_in = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE, related_name='go_in')
    player_out = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE, related_name='come_out')


class BasketballSubstitute(Substitute):
    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player_in = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE, related_name='go_in')
    player_out = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE, related_name='come_out')


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
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    league = models.ForeignKey(FootballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(FootballHalfSeason, on_delete=models.CASCADE)

    @staticmethod
    def get_header():
        return ['تیم', 'بازیها', 'برد', 'مساوی', 'باخت', 'گل زده', 'گل خورده', 'تفاضل گل', 'امتیاز']

    def get_json(self):
        return {
            'teamInfo': [
                {'featureName': 'teamName', 'featureValue': self.team.name, 'featureLink': get_url('team', self.team)},
                {'featureName': 'matches', 'featureValue': self.played, 'featureLink': None},
                {'featureName': 'win', 'featureValue': self.won, 'featureLink': None},
                {'featureName': 'draw', 'featureValue': self.drawn, 'featureLink': None},
                {'featureName': 'loose', 'featureValue': self.lost, 'featureLink': None},
                {'featureName': 'goalZ', 'featureValue': self.GF, 'featureLink': None},
                {'featureName': 'goalK', 'featureValue': self.GA, 'featureLink': None},
                {'featureName': 'goalSub', 'featureValue': self.GD, 'featureLink': None},
                {'featureName': 'score', 'featureValue': self.points, 'featureLink': None},
            ]
        }


class BasketballHalfSeasonLeagueTeams(HalfSeasonLeagueTeams):
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    league = models.ForeignKey(BasketballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(BasketballHalfSeason, on_delete=models.CASCADE)

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


class FootballGoal(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballAssist(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballCard(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class FootballPenalty(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballThreePoint(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballTwoPoint(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballPenaltyFault(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class BasketballPenaltyFailed(models.Model):
    def __str__(self):
        return self.player.name + '(' + self.team.name + ')'

    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class Photos(models.Model):
    def __str__(self):
        return self.photo.name

    photo = models.ImageField()


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
    main_images = models.ForeignKey(Photos, on_delete=models.CASCADE)
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
            'dateTime': self.date_time,
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


class Comments(models.Model):
    def __str__(self):
        return self.text

    text = models.CharField(max_length=400)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()
    news = models.ForeignKey(News, on_delete=models.CASCADE)
