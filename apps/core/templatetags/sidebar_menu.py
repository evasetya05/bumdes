from django import template

register = template.Library()

@register.simple_tag
def create_menu(user):
    menu_items = [
        {'label': 'Pembukuan', 'url': 'ledger:ledger_index', 'icon': 'fas fa-book'},
    ]
    
    # Only show Admin Daerah menu if user has permission
    if user.is_authenticated and (user.is_staff or user.is_superuser):
        menu_items.append({
            'label': 'Admin Daerah',
            'url': 'admin_daerah:dashboard',  # Changed to point to dashboard
            'icon': 'fas fa-map-marker-alt',
            'submenu': [
                {'label': 'Dashboard', 'url': 'admin_daerah:dashboard', 'icon': 'fas fa-tachometer-alt'},
                {'label': 'Dusun', 'url': 'admin_daerah:dusun_list', 'icon': 'fas fa-map-marked-alt'},
                {'label': 'RW', 'url': 'admin_daerah:rw_list', 'icon': 'fas fa-users'},
                {'label': 'RT', 'url': 'admin_daerah:rt_list', 'icon': 'fas fa-user-friends'},
            ]
        })
    
    # Only show Anggota menu if user has permission
    if user.is_authenticated and (user.is_staff or user.is_superuser):
        menu_items.append({
            'label': 'Anggota',
            'url': 'anggota:list',
            'icon': 'fas fa-users',
        })
    


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
