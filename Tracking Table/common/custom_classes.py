from django.core import serializers
from table import models
from table import forms
import json

class OrderObject:

	def __init__(self, order):
		self.order = order
		self.material_eger = models.Plate.objects.filter(order_id=order, manufacturer='Egger')
		self.material_krono = models.Plate.objects.filter(order_id=order, manufacturer='Kronospan')
		self.material_other = models.Plate.objects.filter(order_id=order, manufacturer='Other')
		self.material_edge = models.Edge.objects.filter(order_id=order)
		self.other_services = models.Other.objects.filter(order_id=order)
		self.notes = models.Note.objects.filter(order_id=order)
		self.plate_forms = forms.PlateProgressFormSet(instance=order)
		self.edge_forms = forms.EdgeProgressFormSet(instance=order)
		self.order_progress = forms.OrderProgressForm(instance=order)

	def __str__(self):
	    return str(self.order)

class OrderDetails:

	def __init__(self, order):
		self.order = order
		self.order_plates = models.Plate.objects.filter(order_id=order)
		self.material_eger = models.Plate.objects.filter(order_id=order, manufacturer='Egger')
		self.material_krono = models.Plate.objects.filter(order_id=order, manufacturer='Kronospan')
		self.material_other = models.Plate.objects.filter(order_id=order, manufacturer='Other')
		self.material_edge = models.Edge.objects.filter(order_id=order)

	def get_order(self):
		return json.loads(serializers.serialize('json', [self.order]))

	def get_plates(self):
		return json.loads(serializers.serialize('json', self.order_plates))

	def get_edges(self):
		return json.loads(serializers.serialize('json', self.material_edge))

	def __str__(self):
		return str(self.result)
