from django.contrib import admin
from wakatime_data.models import Day, WakatimeData, Profile


admin.site.register(Day)
admin.site.register(WakatimeData)
admin.site.register(Profile)
