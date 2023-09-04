from django.contrib import admin
from stops.models import Stop

# Register your models here.


@admin.register(Stop)
class StopAdmin(admin.ModelAdmin):
    pass
