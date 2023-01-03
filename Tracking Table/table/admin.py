from django.contrib import admin
from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ExportActionMixin
from table import models

# class OrderResource(resources.ModelResource):

# 	class Meta:
# 		model = models.Order

# class ExportAdmin(ExportActionMixin, admin.ModelAdmin):
# 	resource_classes = [OrderResource]


class ExportAdmin(ExportActionMixin, admin.ModelAdmin):
	pass

admin.site.register(models.Order, ExportAdmin)
admin.site.register(models.Plate, ExportAdmin)
admin.site.register(models.Cutting)
admin.site.register(models.Edge)
admin.site.register(models.Edging)
admin.site.register(models.Other)
admin.site.register(models.Payment)
admin.site.register(models.Note)
admin.site.register(models.Change)
