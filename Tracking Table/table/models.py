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

    def update(self):

        self.clear()

        for item in Plate.objects.filter(cutID=self.ID):
            self.plates_total += item.value
            self.total_price += item.value

        for item in Edge.objects.filter(cutID=self.ID):
            self.edge_total += item.value
            self.total_price += item.value

        for item in Cutting.objects.filter(cutID=self.ID):
            self.cutting_total += item.value
            self.total_price += item.value

        for item in Edging.objects.filter(cutID=self.ID):
            self.edging_total += item.value
            self.total_price += item.value

        for item in Other.objects.filter(cutID=self.ID):
            self.others_total += item.value
            self.total_price += item.value

        for item in Payment.objects.filter(cutID=self.ID):
            self.paid += item.value

        self.balance = round((self.paid - self.total_price), 2)

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
        ('Other', 'Other'),
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
        return str(self.cutID) + ' / ' + self.edging_type


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