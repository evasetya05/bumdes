from django.contrib import admin
from .models import Department, Position, Employee




@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'company')
    list_filter = ('company',)
    search_fields = ('name', 'company__name')


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'department')
    list_filter = ('department', 'department__company')
    search_fields = ('name', 'department__name')


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'company',
                    'department', 'position', 'is_active')
    list_filter = ('department', 'company', 'is_active')
    search_fields = ('name', )
