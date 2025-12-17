from django.db import models

from apps.modules.admin_daerah.models import RT

class AnggotaKoperasi(models.Model):
    JENIS_KELAMIN = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]
    STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
    ]

    nik = models.CharField(max_length=16, unique=True)
    nama_lengkap = models.CharField(max_length=200)
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN)
    email = models.EmailField()
    no_hp = models.CharField(max_length=20)
    rt = models.ForeignKey(
        RT,
        on_delete=models.PROTECT,
        related_name='anggota_koperasi',
        verbose_name='RT',
        blank=True,
        null=True,
    )

    tanggal_daftar = models.DateTimeField(auto_now_add=True)
    status_verifikasi = models.CharField(max_length=10, choices=STATUS, default='pending')

    def __str__(self):
        return f"{self.nama_lengkap} ({self.nik})"

    @property
    def rw(self):
        return self.rt.rw if self.rt_id else None

    @property
    def dusun(self):
        if self.rt_id and self.rt.rw:
            return self.rt.rw.dusun
        return None

