from django.conf import settings
from apps.core.models import Company

def company_info(request):
    context = {}
    try:
        # Get the first company (you might want to modify this based on your needs)
        company = Company.objects.first()
        if company:
            context['company'] = company
            context['company_name'] = company.name
    except Exception as e:
        # Fallback to default name if company doesn't exist
        context['company_name'] = "BUMDES"
    
    return context
