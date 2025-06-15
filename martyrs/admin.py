from django.contrib import admin
from .models import Martyr

@admin.register(Martyr)
class MartyrAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'father_name']
    search_fields = ['first_name', 'last_name']
