from django import template

register = template.Library()

@register.simple_tag
def create_menu(user):
    menu_items = [
        {'label': 'Pembukuan', 'url': 'ledger:ledger_index', 'icon': 'fas fa-book'},
        {'label': 'Parkir', 'url': 'parkir:report_list', 'icon': 'fas fa-book'},
    ]

    return menu_items


@register.filter
def is_owner(user):
    return user.groups.filter(name='Owner').exists()


@register.filter
def is_employee(user):
    return hasattr(user, 'is_employee') and user.is_employee()


@register.filter
def is_active(current_url, match):
    """Tandai menu aktif di template"""
    return 'active' if match in current_url else ''
