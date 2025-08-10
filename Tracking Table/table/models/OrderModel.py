from django.db import models
from django.utils import timezone

# from .PlateModel import Plate
# from .EdgeModel import Edge
# from .CuttingModel import Cutting
# from .EdgingModel import Edging
# from .OtherModel import Other
# from .PaymentModel import Payment

class Order(models.Model):

    client_statuses = [
        ('Internal', 'Internal'),
        ('External', 'External'),
    ]

    ID = models.BigAutoField(primary_key=True)
    created_date = models.DateTimeField(default=timezone.now)
    owner = models.CharField(max_length=50)
    client = models.CharField(choices=client_statuses, default='Internal', max_length=50)
    telephone = models.CharField(max_length=14, blank=True)

    plates_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edge_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cutting_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edging_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    others_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    order_ready = models.BooleanField(default=False)
    order_taken = models.BooleanField(default=False)

    invoice = models.BooleanField(default=False)

    # def update(self):

    #     self.clear()

    #     for item in Plate.objects.filter(cutID=self.ID):
    #         self.plates_total += item.value
    #         self.total_price += item.value

    #     for item in Edge.objects.filter(cutID=self.ID):
    #         self.edge_total += item.value
    #         self.total_price += item.value

    #     for item in Cutting.objects.filter(cutID=self.ID):
    #         self.cutting_total += item.value
    #         self.total_price += item.value

    #     for item in Edging.objects.filter(cutID=self.ID):
    #         self.edging_total += item.value
    #         self.total_price += item.value

    #     for item in Other.objects.filter(cutID=self.ID):
    #         self.others_total += item.value
    #         self.total_price += item.value

    #     for item in Payment.objects.filter(cutID=self.ID):
    #         self.paid += item.value

    #     self.balance = round((self.paid - self.total_price), 2)

    def clear(self):

        self.plates_total = 0
        self.edge_total = 0
        self.cutting_total = 0
        self.edging_total = 0
        self.others_total = 0
        self.paid = 0
        self.total_price = 0

    def __str__(self):
        return str(self.ID)