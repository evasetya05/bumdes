from django.db import models

# apps/parking/models.py
class TicketType(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        app_label = 'parkir'

    def __str__(self):
        return self.name

class ParkingDailyReport(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('posted', 'Posted'),
    )

    date = models.DateField(unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')

    created_by = models.ForeignKey(
        'auth.User', on_delete=models.PROTECT, related_name='parking_reports'
    )
    posted_at = models.DateTimeField(null=True, blank=True)
    journal_entry_id = models.PositiveBigIntegerField(
            null=True, blank=True,
            help_text="ID JournalEntry di Ledger"
        )

 

    def total_bruto(self):
        return sum(i.subtotal() for i in self.items.all())

class ParkingTicketItem(models.Model):
    report = models.ForeignKey(
        ParkingDailyReport, related_name='items', on_delete=models.CASCADE
    )
    ticket_type = models.ForeignKey(TicketType, on_delete=models.PROTECT)

    start_serial = models.IntegerField()
    end_serial = models.IntegerField()
    lembar = models.IntegerField(default=0, blank=True, null=True)
    jumlah = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    description = models.CharField(max_length=255, blank=True, null=True)

    def quantity(self):
        return self.end_serial - self.start_serial + 1

    def subtotal(self):
        return self.quantity() * self.ticket_type.price

class ParkingExpense(models.Model):
    report = models.ForeignKey(
        ParkingDailyReport, related_name='expenses', on_delete=models.CASCADE
    )
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    

class ParkingRevenueRule(models.Model):
    name = models.CharField(max_length=100)  # Pajak, KTH, Dusun, dll
    percentage = models.DecimalField(max_digits=5, decimal_places=2)

    account = models.ForeignKey(
        'ledger.Account', on_delete=models.PROTECT,
        help_text="Akun utang / kewajiban"
    )

    is_active = models.BooleanField(default=True)

