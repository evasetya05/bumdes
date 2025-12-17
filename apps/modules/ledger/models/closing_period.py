from django.db import models
from django.utils import timezone


class ClosingPeriod(models.Model):
    period = models.CharField(max_length=7, unique=True)  # format: YYYY-MM
    is_closed = models.BooleanField(default=False)
    closed_at = models.DateTimeField(blank=True, null=True)
    closed_by = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['-period']

    def __str__(self):
        return f"{self.period} ({'Closed' if self.is_closed else 'Open'})"

    # ==========================================================
    # 📅 UTILITY
    # ==========================================================
    @classmethod
    def get_current_period(cls):
        """Kembalikan periode saat ini (contoh: '2025-10')."""
        now = timezone.now()
        return now.strftime("%Y-%m")

    @classmethod
    def ensure_period_exists(cls, period=None):
        """Pastikan periode tertentu sudah ada di tabel."""
        if not period:
            period = cls.get_current_period()
        obj, _ = cls.objects.get_or_create(period=period)
        return obj

    @classmethod
    def get_open_period(cls):
        """Ambil periode yang masih open."""
        open_period = cls.objects.filter(is_closed=False).order_by('-period').first()
        if not open_period:
            period_now = cls.get_current_period()
            open_period, _ = cls.objects.get_or_create(period=period_now, is_closed=False)
        return open_period

    # ==========================================================
    # 🔒 CLOSE PERIOD
    # ==========================================================
    def close_period(self, user=None):
        """
        Tutup periode ini, dan masukkan semua jurnal yang belum di-close
        (is_posted=False) ke periode ini, berapapun tanggalnya.
        """
        if self.is_closed:
            print(f"⚠️ Periode {self.period} sudah ditutup.")
            return self

        from ledger.models.journal_entry import JournalEntry  # hindari circular import

        # Ambil semua jurnal yang belum pernah di-close
        unposted_entries = JournalEntry.objects.filter(is_posted=False)

        # Update semuanya ke periode ini
        updated_count = unposted_entries.update(period=self.period, is_posted=True)

        # Tutup periode
        self.is_closed = True
        self.closed_at = timezone.now()
        if user:
            self.closed_by = user
        self.save()

        print(f"✅ Closed {updated_count} jurnal → periode {self.period}")
        return self
