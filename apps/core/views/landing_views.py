from django.shortcuts import render
from django.views import View

class LandingPageView(View):
    template_name = 'landing_page.html'
    
    def get(self, request, *args, **kwargs):
        # This page is accessible to both authenticated and anonymous users
        context = {
            'is_authenticated': request.user.is_authenticated,
        }
        return render(request, self.template_name, context)
