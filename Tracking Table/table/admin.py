from django.contrib import admin
from table import models

admin.site.register(models.Order)
admin.site.register(models.Plate)
admin.site.register(models.Cutting)
admin.site.register(models.Edge)
admin.site.register(models.Edging)
admin.site.register(models.Other)
admin.site.register(models.Payment)
admin.site.register(models.Note)