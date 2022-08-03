from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

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

    # material_eger = models.CharField(max_length=500, default='', blank=True)
    # material_krono = models.CharField(max_length=500, default='', blank=True)
    # material_edge = models.CharField(max_length=500, default='', blank=True)

    plates_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edge_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cutting_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    edging_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    others_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    notes = models.TextField(max_length=500, blank=True)

    order_ready = models.BooleanField(default=False)
    order_taken = models.BooleanField(default=False)

    def update(self):

        self.get_total()
        self.get_balance()

        all_plates = Plate.objects.filter(cutID=self.ID)
        for item in all_plates:
            self.plates_total += item.value

        all_edges = Edge.objects.filter(cutID=self.ID)
        for item in all_edges:
            self.edge_total += item.value

        all_cutting = Cutting.objects.filter(cutID=self.ID)
        for item in all_cutting:
            self.cutting_total += item.value

        for item in Edging.objects.filter(cutID=self.ID):
            self.edging_total += item.value

        for item in Other.objects.filter(cutID=self.ID):
            self.others_total += item.value

    def get_total(self):

        self.total_price = 0
        all_objects  = []
        all_objects.extend(Plate.objects.filter(cutID=self.ID))
        all_objects.extend(Edge.objects.filter(cutID=self.ID))
        all_objects.extend(Cutting.objects.filter(cutID=self.ID))
        all_objects.extend(Edging.objects.filter(cutID=self.ID))
        all_objects.extend(Other.objects.filter(cutID=self.ID))

        for item in all_objects:
            self.total_price += item.value

        return self.total_price

    def get_balance(self):

        paid = 0
        all_payments = Payment.objects.filter(cutID=self.ID)

        for item in all_payments:
            paid += item.value

        self.balance = round((paid - self.total_price), 2)

    def __str__(self):
        return str(self.ID)

class Note(models.Model):

    cutID = models.ForeignKey(Order, on_delete=models.CASCADE)

    user = models.CharField(max_length=50, default='n/a')
    date = models.DateTimeField(default=timezone.now)
    content = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return f'{self.user} - {self.content}'


class Plate(models.Model):

    manufacturers = [
        ('Egger', 'Egger'),
        ('Kronospan', 'Kronospan'),
    ]

    cutID = models.ForeignKey(Order, on_delete=models.CASCADE)
    manufacturer = models.CharField(choices=manufacturers, default='Egger', max_length=10)

    material = models.CharField(max_length=50)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.001)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)
    cutted = models.BooleanField(default=False)
    edged = models.BooleanField(default=False)

    def __str__(self):
        return str(self.cutID) + ' / ' + self.material


class Cutting(models.Model):

    cutID = models.ForeignKey(Order, on_delete=models.CASCADE)

    cutting_type = models.CharField(max_length=50)
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.001)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.cutID) + ' / ' + self.cutting_type


class Edge(models.Model):

    cutID = models.ForeignKey(Order, on_delete=models.CASCADE)

    edge_type = models.CharField(max_length=50)
    color_code = models.CharField(max_length=50, default='')
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.001)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    ordered = models.BooleanField(default=False)
    delivered = models.BooleanField(default=False)

    def __str__(self):
        return str(self.cutID) + ' / ' + self.color_code


class Edging(models.Model):

    cutID = models.ForeignKey(Order, on_delete=models.CASCADE)

    edging_type = models.CharField(max_length=50)
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.001)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.cutID) + ' / ' + self.material


class Other(models.Model):

    cutID = models.ForeignKey(Order, on_delete=models.CASCADE)

    description = models.CharField(max_length=50)
    quantity = models.PositiveSmallIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.001)])
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return str(self.cutID) + ' / ' + self.description


class Payment(models.Model):

    payment_methods = [
        ('Cash', 'Cash'),
        ('Card', 'Card'),
        ('Bank', 'Bank'),
    ]

    cutID = models.ForeignKey(Order, on_delete=models.CASCADE)

    value = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.001)])
    payment_method = models.CharField(choices=payment_methods, default='Cash', max_length=10)

    def __str__(self):
        return f'Payment for {self.cutID}'