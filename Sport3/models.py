from django.contrib.auth.models import User
from django.db import models


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


class Match(models.Model):
    best_player = models.ForeignKey(FootballPlayer, on_delete=models.CASCADE)
    date = models.DateTimeField()
    league = models.ForeignKey(FootballLeague, on_delete=models.CASCADE)
    team = models.ForeignKey(FootballTeam, on_delete=models.CASCADE)
    half_season = models.ForeignKey(FootballHalfSeason, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class FootballMatch(Match):
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


class BasketballMatch(Match):
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


class NewsTags(models.Model):
    name = models.CharField(max_length=50)


class NewsSources(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField()


class News(models.Model):
    title = models.CharField(max_length=100)
    body_text = models.TextField()
    date = models.DateField()
    tags = models.ManyToManyField(NewsTags)
    sources = models.ManyToManyField(NewsSources)
    football_league = models.ManyToManyField(FootballLeague)
    basketball_league = models.ManyToManyField(BasketballLeague)
    football_match = models.ManyToManyField(FootballMatch)
    basketball_match = models.ManyToManyField(BasketballMatch)
    football_player = models.ManyToManyField(FootballPlayer)
    basketball_player = models.ManyToManyField(BasketballPlayer)
    football_team = models.ManyToManyField(FootballTeam)
    basketball_team = models.ManyToManyField(BasketballTeam)


class Comments(models.Model):
    text = models.CharField(max_length=400)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time = models.PositiveSmallIntegerField()


