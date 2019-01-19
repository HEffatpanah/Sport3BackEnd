import datetime

from django.contrib.auth.models import User
from django.db import models
from polymorphic.models import PolymorphicModel


def get_url(action, id):
    return 'http://127.0.0.1:3000/sport3/{0}/{1}'.format(action, id)


# Create your models here.


class FootballLeague(models.Model):
    name = models.CharField(max_length=20)


class BasketballLeague(models.Model):
    name = models.CharField(max_length=20)


class FootballTeam(models.Model):
    name = models.CharField(max_length=40)


class BasketballTeam(models.Model):
    name = models.CharField(max_length=40)


class FootballPlayer(models.Model):
    name = models.CharField(max_length=40)
    birth_date = models.DateTimeField()
    position = models.CharField(max_length=20)
    photo = models.ImageField()


class BasketballPlayer(models.Model):
    name = models.CharField(max_length=40)
    birth_date = models.DateTimeField()
    position = models.CharField(max_length=20)
    photo = models.ImageField()


class FootballHalfSeason(models.Model):
    half = models.BooleanField()
    name = models.CharField(max_length=20)
    league = models.ManyToManyField(FootballLeague)


class BasketballHalfSeason(models.Model):
    half = models.BooleanField()
    name = models.CharField(max_length=20)
    league = models.ManyToManyField(BasketballLeague)


class Match(PolymorphicModel):
    best_player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    league = models.ForeignKey(FootballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(FootballHalfSeason, on_delete=models.CASCADE)

    def create_match_summary_json(self):
        pass


class FootballMatch(Match):
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

    def create_match_summary_json(self):
        return (
            {
                'team1Name': self.team1.name,
                'team1Link': get_url('team', self.team1.id),
                'team2Name': self.team2.name,
                'team2Link': get_url('team', self.team2.id),
                'team1Goal': self.team1_goals,
                'team2Goal': self.team2_goals,
                'date': 'امروز' if self.date_time.date() is datetime.datetime.now().date()
                else 'دیروز' if self.date_time.date() is datetime.datetime.now().date() - datetime.timedelta(days=1)
                else 'فردا' if self.date_time.date() is datetime.datetime.now().date() - datetime.timedelta(days=1)
                else self.date_time.date()
            }
        )


class BasketballMatch(Match):
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
    team1_last_score = models.PositiveSmallIntegerField()
    team2_last_score = models.PositiveSmallIntegerField()
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

    def create_match_summary_json(self):
        pass


class FootballTeamMembers(models.Model):
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    half_season = models.ForeignKey(FootballHalfSeason, on_delete=models.CASCADE)


class BasketballTeamMembers(models.Model):
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    half_season = models.ForeignKey(BasketballHalfSeason, on_delete=models.CASCADE)


class FootballSubstitute(models.Model):
    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()
    in_out = models.BooleanField()  # 1 for in 0 for out


class BasketballSubstitute(models.Model):
    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()
    in_out = models.BooleanField()  # 1 for in 0 for out


class FootballMatchPlayersList(models.Model):
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    match = models.ForeignKey(FootballMatch, on_delete=models.CASCADE)
    main_substitute = models.BooleanField()  # 1 for main 0 for substitute


class BasketballMatchPlayersList(models.Model):
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    player = models.ForeignKey(BasketballPlayer, on_delete=models.CASCADE)
    match = models.ForeignKey(BasketballMatch, on_delete=models.CASCADE)
    main_substitute = models.BooleanField()  # 1 for main 0 for substitute


class FootballHalfSeasonLeagueTeams(models.Model):
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    league = models.ForeignKey(FootballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(FootballHalfSeason, on_delete=models.CASCADE)
    played = models.PositiveSmallIntegerField()
    won = models.PositiveSmallIntegerField()
    drawn = models.PositiveSmallIntegerField()
    lost = models.PositiveSmallIntegerField()
    GF = models.PositiveSmallIntegerField()  # gole zadeh
    GA = models.PositiveSmallIntegerField()  # gole khordeh
    GD = models.SmallIntegerField()  # tafazoleh gol
    points = models.PositiveSmallIntegerField()


class BasketballHalfSeasonLeagueTeams(models.Model):
    team = models.ForeignKey(BasketballTeam, on_delete=models.CASCADE)
    league = models.ForeignKey(BasketballLeague, on_delete=models.CASCADE)
    half_season = models.ForeignKey(BasketballHalfSeason, on_delete=models.CASCADE)
    played = models.PositiveSmallIntegerField()
    won = models.PositiveSmallIntegerField()
    lost = models.PositiveSmallIntegerField()
    GF = models.PositiveSmallIntegerField()  # gole zadeh
    GA = models.PositiveSmallIntegerField()  # gole khordeh
    GD = models.SmallIntegerField()  # tafazoleh gol
    points = models.PositiveSmallIntegerField()


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
    news_number = models.SmallIntegerField()


class Comments(models.Model):
    text = models.CharField(max_length=400)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


class News(PolymorphicModel):
    title = models.CharField(max_length=100)
    body_text = models.TextField()
    date_time = models.DateTimeField()
    tags = models.ManyToManyField(NewsTags)
    sources = models.ManyToManyField(NewsSources)
    main_images = models.ForeignKey(Photos, on_delete=models.CASCADE)
    more_images = models.ManyToManyField(Photos, related_name='news1')

    def create_summary_news_json(self):
        pass


class FootballNews(News):
    football_league = models.ManyToManyField(FootballLeague)
    football_match = models.ManyToManyField(FootballMatch)
    football_player = models.ManyToManyField(FootballPlayer)
    football_team = models.ManyToManyField(FootballTeam)

    def create_summary_news_json(self):
        pass


class BasketballNews(News):
    basketball_league = models.ManyToManyField(BasketballLeague)
    basketball_match = models.ManyToManyField(BasketballMatch)
    basketball_player = models.ManyToManyField(BasketballPlayer)
    basketball_team = models.ManyToManyField(BasketballTeam)

    def create_summary_news_json(self):
        pass
