from models import SimpleText
from django.contrib import admin
from django import forms

class SimpleTextAdminForm(forms.ModelForm):
    """SimpleTextAdminForm"""
    class Meta:
        model = SimpleText

class SimpleTextAdmin(admin.ModelAdmin):
    form = SimpleTextAdminForm


admin.site.register(SimpleText, SimpleTextAdmin)