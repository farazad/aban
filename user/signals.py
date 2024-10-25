from decimal import Decimal
from django.db.models.signals import post_save
from django.dispatch import receiver

from accounting.models import Asset, Wallet
from user.models import User


@receiver(post_save, sender=User)
def increase_new_user_balance(sender, instance, *args, **kwargs):
    try:
        if kwargs["created"]:
            Wallet.objects.create(user=instance, balance=100)
    except Exception as error:
        message = f"exception in new_user signals!! \n {str(error)}"
        # TODO must be logged into log systems
        print(message)