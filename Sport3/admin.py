from django.contrib import admin

from Sport3.models import *


class MyModelAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        return {}


# Register your models here.
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
# admin.site.register(Photos)
# admin.site.register(NewsTags)
# admin.site.register(NewsSources)
admin.site.register(SiteUser)
admin.site.register(Comments)
admin.site.register(FootballNews)
admin.site.register(BasketballNews)
admin.site.register(CurrentHalfSeason)
admin.site.register(Goal, MyModelAdmin)
admin.site.register(FootballCard, MyModelAdmin)
admin.site.register(FootballAssist, MyModelAdmin)
# admin.site.register(, MyModelAdmin)
