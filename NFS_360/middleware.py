# from django.shortcuts import redirect
# from App_Admin.models import ProviderURL, SuperUserURL
# from django.urls import reverse

# class UniqueURLMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         # Fetch unique_id from the request's GET parameters
#         unique_id = request.GET.get('id')

#         if unique_id:
#             # Check if the unique_id exists in either ProviderURL or SuperUserURL
#             is_valid_provider = ProviderURL.objects.filter(unique_id=unique_id).exists()
#             is_valid_superuser = SuperUserURL.objects.filter(unique_id=unique_id).exists()

#             # If unique_id is invalid, redirect to an error page or deny access
#             if not is_valid_provider and not is_valid_superuser:
#                 return redirect(reverse('error_page'))  # Define 'error_page' in your urls.py

#         return self.get_response(request)


# from django.apps import apps
# from django.shortcuts import redirect

# class UniqueURLMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         ProviderURL = apps.get_model('App_admin', 'ProviderURL')  # Dynamically fetch the model
#         SuperUserURL = apps.get_model('App_admin', 'SuperUserURL')

#         # Fetch unique_id from the request's GET parameters
#         unique_id = request.GET.get('id')

#         if unique_id:
#             # Check if the unique_id exists in either ProviderURL or SuperUserURL
#             is_valid_provider = ProviderURL.objects.filter(unique_id=unique_id).exists()
#             is_valid_superuser = SuperUserURL.objects.filter(unique_id=unique_id).exists()

#             # If unique_id is invalid, redirect to an error page or deny access
#             if not is_valid_provider and not is_valid_superuser:
#                 return redirect('error_page')  # Define 'error_page' in your urls.py

#         return self.get_response(request)

