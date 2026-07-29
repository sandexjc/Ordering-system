from common.models import BasePayment
from table.service import PaymentWorkflow
from table.models.base import TableItem


class Payment(TableItem, BasePayment):

    """

    Hierarchy:
    BaseModel -> TableItem -> Payment
    BasePayment -> Payment

    --- Fields inherited from BaseModel via TableItem ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    --- Fields inherited from TableItem ---

    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = TableItemManager()

    --- Fields inherited from BasePayment ---

    value = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.00)])
    payment_method = models.CharField(choices=payment_methods, default='Cash', max_length=10)

    """

    # Service layer workflow model speific functionality
    workflow_service_class = PaymentWorkflow

    def __str__(self):
        return f'Payment: {self.value} / Order ID: {self.order_id}'