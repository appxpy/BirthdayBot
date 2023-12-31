from tortoise import fields
from tortoise.models import Model


class User(Model):
    user_id = fields.BigIntField(unique=True)
    username = fields.CharField(max_length=255, null=True)
    full_name = fields.CharField(max_length=255)
    balance = fields.DecimalField(max_digits=32, decimal_places=2, default=0)

    class Meta:
        table = "users"

    def __str__(self):
        return f"[{self.user_id}] {self.full_name}"
