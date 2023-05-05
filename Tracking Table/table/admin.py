from django.contrib import admin
from import_export import resources
from import_export.fields import Field
from import_export.widgets import ForeignKeyWidget, DateWidget
from import_export.admin import ExportActionMixin
from table import models

class OrderResource(resources.ModelResource):

	ID = Field(attribute='ID', column_name='ID')
	date = Field(attribute='created_date', column_name='Дата на създаване', widget=DateWidget(format='%d.%m.%Y %H:%m'))
	client = Field(attribute='owner', column_name='Име на клиент')
	telephone = Field(attribute='telephone', column_name='Телефон')
	plates_data = Field(attribute='plates_total', column_name='Стойност плочи')
	cutting_data = Field(attribute='cutting_total', column_name='Стойност рязане')
	edge_data = Field(attribute='edge_total', column_name='Стойност кант')
	edging_data = Field(attribute='edging_total', column_name='Стойност кантиране')
	total_value = Field(attribute='total_price', column_name='Обща стойност')
	paid_data = Field(attribute='paid', column_name='Авансово плащане')
	balance_data = Field(attribute='balance', column_name='Баланс')


	class Meta:
		model = models.Order
		fields = (
			'ID', 
			'date', 
			'client', 
			'telephone', 
			'plates_data', 
			'cutting_data',
			'edge_data',
			'edging_data',
			'total_value',
			'paid_data',
			'balance_data',
			)

class ExportOrder(ExportActionMixin, admin.ModelAdmin):
	resource_class = OrderResource

class ExportOther(ExportActionMixin, admin.ModelAdmin):
	# resource_class = PlateResource
	pass


admin.site.register(models.Order, ExportOrder)
admin.site.register(models.Plate, ExportOther)
admin.site.register(models.Cutting, ExportOther)
admin.site.register(models.Edge, ExportOther)
admin.site.register(models.Edging, ExportOther)
admin.site.register(models.Other, ExportOther)
admin.site.register(models.Payment, ExportOther)
admin.site.register(models.Note, ExportOther)
admin.site.register(models.Change, ExportOther)
