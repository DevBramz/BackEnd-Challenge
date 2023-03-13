from django.contrib import admin

from org.models import Organization

@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    pass

# Register your models here.
