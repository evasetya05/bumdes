from datetime import date

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from .person import Person


class Employee(Person):
    GENDER_CHOICES = [
        ("male", "Laki-laki"),
        ("female", "Perempuan"),
    ]

    PPH21_STATUS_CHOICES = [
        ('TK/0', 'TK/0 - Tidak Kawin, tanpa tanggungan'),
        ('TK/1', 'TK/1 - Tidak Kawin, 1 tanggungan'),
        ('TK/2', 'TK/2 - Tidak Kawin, 2 tanggungan'),
        ('TK/3', 'TK/3 - Tidak Kawin, 3 tanggungan'),
        ('K/0', 'K/0 - Kawin, tanpa tanggungan'),
        ('K/1', 'K/1 - Kawin, 1 tanggungan'),
        ('K/2', 'K/2 - Kawin, 2 tanggungan'),
        ('K/3', 'K/3 - Kawin, 3 tanggungan'),
        ('HB/0', 'HB/0 - Istri bekerja, tanpa tanggungan (penghasilan digabung dengan suami)'),
        ('HB/1', 'HB/1 - Istri bekerja, 1 tanggungan'),
        ('HB/2', 'HB/2 - Istri bekerja, 2 tanggungan'),
        ('HB/3', 'HB/3 - Istri bekerja, 3 tanggungan'),
    ]

    email = models.EmailField(unique=True)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='person')
    company = models.ForeignKey(
        'Company', on_delete=models.SET_NULL, null=True, blank=True)
    department = models.ForeignKey(
        'Department', on_delete=models.SET_NULL, null=True, blank=True)
    position = models.ForeignKey(
        'Position', on_delete=models.SET_NULL, null=True, blank=True)
    manager = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    hire_date = models.DateField(null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        verbose_name='Jenis Kelamin'
    )
    resignation_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='employee_photo', null=True, blank=True)
    kk = models.FileField(upload_to='document/kk', null=True, blank=True)
    ktp = models.FileField(upload_to='document/ktp', null=True, blank=True)
    npwp = models.FileField(upload_to='document/npwp', null=True, blank=True)
    emergency_contact = models.CharField(max_length=225, blank=True)

    bank_name = models.CharField(max_length=100, blank=True)
    bank_account_number = models.CharField(max_length=50, blank=True)

    # Compensation defaults
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    leave_entitlement = models.PositiveSmallIntegerField(default=12, help_text='Hak cuti tahunan (hari)')
    pph21_status = models.CharField(
        max_length=5,
        choices=PPH21_STATUS_CHOICES,
        blank=True,
        default='',
        verbose_name='Status Pajak PPh 21'
    )

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        years = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            years -= 1
        return years

    def current_employment_period(self):
        if not hasattr(self, '_current_employment_period'):
            today = date.today()
            self._current_employment_period = self.employment_periods.filter(
                start_date__lte=today
            ).filter(
                models.Q(end_date__isnull=True) | models.Q(end_date__gte=today)
            ).order_by('-start_date').first()
        return self._current_employment_period

    @property
    def employment_stage(self):
        if self.resignation_date:
            return 'Resigned'

        period = self.employment_periods.order_by('-start_date').first()
        if period:
            return period.get_period_type_display()

        return 'Lepas'


class EmployeeAllowance(models.Model):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='allowances',
    )
    name = models.CharField(max_length=100)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Employee Allowance'
        verbose_name_plural = 'Employee Allowances'

    def __str__(self):
        return f"{self.name} ({self.employee})"


class EmployeeEmploymentPeriod(models.Model):
    class PeriodType(models.TextChoices):
        PROBATION = 'probation', 'Probation'
        CONTRACT = 'contract', 'Contract'
        PERMANENT = 'permanent', 'Permanent'
        LEPAS = 'lepas', 'Lepas'

    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='employment_periods',
    )
    period_type = models.CharField(max_length=20, choices=PeriodType.choices)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    notes = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_date', 'period_type']
        verbose_name = 'Employment Period'
        verbose_name_plural = 'Employment Periods'

    def __str__(self):
        return f"{self.employee} - {self.get_period_type_display()} ({self.start_date} - {self.end_date or 'present'})"
