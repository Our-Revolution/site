from django.contrib import admin
from .models import CandidateRace, InitiativeRace



@admin.register(CandidateRace)
class CandidateRaceAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'candidate_votes', 'last_updated', 'result']
    list_filter = ['result', 'candidate__state']



@admin.register(InitiativeRace)
class InitiativeRaceAdmin(admin.ModelAdmin):
    list_display = ['initiative', 'initiative_votes', 'last_updated', 'result']
    list_filter = ['result', 'initiative__state']