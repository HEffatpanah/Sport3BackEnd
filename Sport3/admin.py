import re

from django.contrib import admin

from Sport3.models import *


class MyModelAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     print('hooooooooy', db_field.name, request, db_field)
    #     if db_field.name == "team1_main_players":
    #         kwargs["queryset"] = self.team1.members.all()
    #     return super(GoalAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)


class GoalAdmin(admin.ModelAdmin):
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        url = request.environ['HTTP_REFERER']
        regex = re.search(r'([\d]+)/change/$', url)
        match = FootballMatch.objects.all()[int(regex.group(1)) - 1]
        if db_field.name == "player":
            kwargs["queryset"] = FootballPlayer.objects.filter(Q(team=match.team1) | Q(team=match.team2))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


admin.site.register(FootballLeague)
admin.site.register(BasketballLeague)
admin.site.register(FootballTeam)
admin.site.register(BasketballTeam)
admin.site.register(FootballPlayer)
admin.site.register(BasketballPlayer)
admin.site.register(HalfSeason)
admin.site.register(FootballMatch)
admin.site.register(BasketballMatch)
# admin.site.register(FootballTeamHalfSeasonMembers)
# admin.site.register(BasketballTeamHalfSeasonMembers)
# admin.site.register(FootballSubstitute)
# admin.site.register(BasketballSubstitute)
# admin.site.register(FootballMatchPlayersList)
# admin.site.register(BasketballMatchPlayersList)
admin.site.register(FootballHalfSeasonLeagueTeams)
# admin.site.register(BasketballHalfSeasonLeagueTeams)
# admin.site.register(FootballGoal)
# admin.site.register(FootballAssist)
# admin.site.register(FootballCard)
# admin.site.register(FootballPenalty)
# admin.site.register(BasketballTwoPoint)
# admin.site.register(BasketballThreePoint)
# admin.site.register(BasketballPenaltyFault)
# admin.site.register(BasketballPenaltyFailed)
admin.site.register(Photos, MyModelAdmin)
admin.site.register(NewsTags, MyModelAdmin)
admin.site.register(NewsSources, MyModelAdmin)
admin.site.register(SiteUser)
admin.site.register(Comments)
admin.site.register(FootballNews)
admin.site.register(BasketballNews)
admin.site.register(CurrentHalfSeason)
admin.site.register(DefaultLeague)
admin.site.register(Goal, MyModelAdmin)
admin.site.register(FootballCard, MyModelAdmin)
admin.site.register(FootballAssist, MyModelAdmin)
admin.site.register(FootballPenalty, MyModelAdmin)
admin.site.register(FootballSubstitute, MyModelAdmin)
admin.site.register(FootballPlayerHalfSeasonStatistics)
