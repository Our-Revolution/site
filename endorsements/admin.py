from django.contrib import admin
from .models import *


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'office', 'state']
    list_filter = ['state']
    search_fields = ['name', 'state']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Initiative)
class InitiativeAdmin(admin.ModelAdmin):
    list_display = ['name', 'state']
    list_filter = ['state', 'category']
    search_fields = ['name', 'state', 'category']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
