from django.db import models
from ledger.models.account import Account

class JournalEntry(models.Model):
    date = models.DateField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    period = models.CharField(max_length=7, blank=True, null=True)  # format YYYY-MM
    is_posted = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        from ledger.models.closing_period import ClosingPeriod

        # 💡 Hanya isi period jika belum diset
        if not self.period:
            open_period = ClosingPeriod.get_open_period()
            self.period = open_period.period

        super().save(*args, **kwargs)



class JournalItem(models.Model):
    journal_entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name='items')
    account = models.ForeignKey(Account, on_delete=models.PROTECT)
    debit = models.IntegerField(default=0)
    credit = models.IntegerField(default=0)
    note = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.journal_entry.date} - {self.account.account_name}"
