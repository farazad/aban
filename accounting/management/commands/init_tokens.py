from django.core.management.base import BaseCommand
from accounting.models import (
    Asset,
)

class Command(BaseCommand):
    help = "this command creates needed objects for first time running project"

    def add_arguments(self, parser):
        return

    def handle(self, *args, **options):
        usdt = Asset.objects.create(
            name="tether",
            symbol="USDT",
            buy_price = 60000,
            sell_price = 55000,
            order_volume = 1000

        )
        aban = Asset.objects.create(
            name="aban coin",
            symbol="aban",
            buy_price = 4,
            sell_price = 3,
            order_volume = 1000
        )

        self.stdout.write(self.style.SUCCESS("Successfully created basic data"))