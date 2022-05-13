from http.client import ResponseNotReady
from django.contrib import admin
from .models import User, Admin, Voter, Precinct, Facis,Repre
# Register your models here.
admin.site.register(User)
admin.site.register(Admin)
admin.site.register(Voter)
admin.site.register(Precinct)
admin.site.register(Facis)
admin.site.register(Repre)