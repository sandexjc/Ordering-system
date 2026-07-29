from common.models import BasePayment
from vitrine.service import BaseVitrineItemWorkflow
from vitrine.models.base import VitrineItem


class Payment(VitrineItem, BasePayment):

    """

    Hierarchy:
    BaseModel -> VitrineItem -> Payment
    BasePayment -> Payment

    --- Fields inherited from BaseModel via VitrineItem ---

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    --- Fields inherited from VitrineItem ---

    vitrine_id = models.ForeignKey(Vitrine, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = VitrineItemManager()

    --- Fields inherited from BasePayment ---

    value = models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(0.00)])
    payment_method = models.CharField(choices=payment_methods, default='Cash', max_length=10)

    """

    # Service layer workflow model speific functionality
    workflow_service_class = BaseVitrineItemWorkflow

    def __str__(self):
        return f'Payment for Vitrine ID: {self.vitrine_id}'