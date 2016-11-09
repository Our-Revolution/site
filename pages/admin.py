from django.contrib import admin
from .models import CandidateRace, InitiativeRace



@admin.register(CandidateRace)
class CandidateRaceAdmin(admin.ModelAdmin):
    list_display = ['candidate', 'candidate_votes', 'last_updated', 'result']
    list_filter = ['result', 'candidate__state']
    search_fields = ['candidate__name', 'candidate__state', 'candidate__office']



@admin.register(InitiativeRace)
class InitiativeRaceAdmin(admin.ModelAdmin):
    list_display = ['initiative', 'initiative_votes', 'last_updated', 'result']
    list_filter = ['result', 'initiative__state']
    search_fields = ['initiative__name', 'initiative__state', 'initiative__title', 'initiative__category']