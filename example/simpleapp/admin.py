from models import SimpleText, SimpleTextTwo
from django.contrib import admin
from django import forms
from concepts.admin import ConceptItemInline

class SimpleTextTwoAdmin(admin.ModelAdmin):
    inlines = [ConceptItemInline, ]


admin.site.register(SimpleText)
admin.site.register(SimpleTextTwo, SimpleTextTwoAdmin)