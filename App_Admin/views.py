
from django.contrib import messages
import subprocess
import os
import json
from django.http import HttpResponse

# Create your views here.

##################### Page_1: Email_Generation #####################

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from .models import ClientProject, Seeker, Provider, SuperUser, RelationshipView, CliPr, ProviderURL, SuperUserURL, OptimumMinimumCriteriaView, FullRatingDataView, OpenQuestionView, AssessmentNumberView, ProviderRelationshipView, SeekerURL, ProviderStatusView, SeekerStatusView
from .utils import generate_unique_url
from django.db.models import Q

# 1. Email Functinality:
def admin1_compose_email(request):

    return render(request, 'admin1_compose_email.html')

def fetch_client(request):
    clients = ClientProject.objects.values('client_name').distinct()
    client_list = [{'client_name': client['client_name']} for client in clients]
    return JsonResponse({'clients': client_list})

    # try:
    #     # Fetch distinct client names from the ClientProject model
    #     clients = ClientProject.objects.values_list('client_name', flat=True).distinct()
    #     print(f"Clients fetched successfully: {list(clients)}")  # Debugging: Log fetched clients
    # except Exception as e:
    #     # Handle any errors during fetching
    #     messages.error(request, f"Error fetching clients: {str(e)}")
    #     clients = []

    # # Pass the fetched clients to the template for rendering

    # return render(request, 'admin1_compose_email.html', {'clients': clients})

# Getting project on the bases of client:
def get_projects_by_client(request, client_name):
    try:
        # Fetch the client object by ID
        # client_name = ClientProject.GET.get('client_name')

        # if client_name.lower() == 'all clients':
        #     projects = list(ClientProject.objects.values('project_name'))
        #     print(f"Projects fetched successfully::::::::::>>>>>> {projects}")  # Debugging: Log fetched projects
        # else:
        projects = list(ClientProject.objects.filter(client_name__iexact=client_name).values('project_name'))
        # Check if projects exist for the given client_name
        if not projects:
            return JsonResponse({'error': f'No projects found for client: {client_name}'}, status=404)
        
        print(projects)
        # Return projects and client name
        return JsonResponse({
            'client_name': client_name,
            'projects': projects
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# View to fetch seekers and statuses dynamically
def get_seekers_and_statuses(request):
    client_name = request.GET.get('client_name', '')
    project_name = request.GET.get('project_name', '')

    client_projects = ClientProject.objects.all()
    if client_name:
        client_projects = client_projects.filter(client_name__iexact=client_name)
    if project_name:
        client_projects = client_projects.filter(project_name__iexact=project_name)

    seekers = Seeker.objects.filter(cp__in=client_projects)
    statuses = ['open', 'in_progress', 'completed']  # Example statuses
    print(f'Seekers data 1::::: {seekers}')
    seekers_data = [{'id': seeker.seeker_id, 'email': seeker.seeker_email} for seeker in seekers]
    print(f'Seekers data 2::::: {seekers_data}')
    return JsonResponse({'seekers': seekers_data, 'statuses': statuses})

def get_filtered_data(request):
    client_name = request.GET.get('client_name', '')
    project_name = request.GET.get('project_name', '')
    #status = request.GET.get('status', '')  # Assuming status is related to seekers or relationships

    # Filter client projects based on the client and project names
    client_projects = ClientProject.objects.all()
    if client_name:
        client_projects = client_projects.filter(client_name__iexact=client_name)
    if project_name:
        client_projects = client_projects.filter(project_name__iexact=project_name)
    
    # Fetch seekers associated with the filtered client projects
    # seekers = Seeker.objects.filter(cp__in=client_projects)
    # providers = Provider.objects.filter(cp__in = client_projects )
    # # Fetch relationships involving these seekers and client projects
    # #relationships = Relationship.objects.filter(cp__in=client_projects, seeker__in=seekers)
    # relationships = RelationshipView.objects.filter( seeker_id__in=seekers, provider_id__in = providers)
    # # If a status is provided, filter the relationships further
    # # if status:
    # #     relationships = relationships.filter(relationship__iexact=status)

    # # Prepare the data to send back as JSON
    # data = []
    # for relationship in relationships:
    #     data.append({
    #         'seeker_name': f"{relationship.seeker_id.seeker_first_name} {relationship.seeker_id.seeker_last_name or ''}".strip(),
    #         'seeker_email': relationship.seeker_id.seeker_email,
    #         'provider_name': f"{relationship.provider_id.provider_first_name} {relationship.provider_id.provider_last_name or ''}".strip(),
    #         'provider_email': relationship.provider_id.provider_email,
    #         'relationship': relationship.relationship,
           
    #     })

    # return JsonResponse({'seekers': data})

    # Retrieve the list of cp_ids from the filtered ClientProjects
    cp_ids = list(client_projects.values_list('cp_id', flat=True))
    print("Filtered ClientProject IDs:::::::::::::::::::::::::::::::::::::::::::::::::::::>>>>>>>>", cp_ids)

    if not cp_ids:
        # If no ClientProjects match the filters, return an empty list
        return JsonResponse({'seekers': []})
    
    # Fetch relationships from RelationshipView where cp is in the filtered cp_ids
    relationships = RelationshipView.objects.filter(cp__in=cp_ids)
    print("Filtered Relationships:::::::::::::::::::::::::::::::::::::::::::::::::::::>>>>>>>>", relationships)


    if not relationships.exists():
        # If no relationships are found, return an empty list
        return JsonResponse({'seekers': []})
    
    # Extract all seeker_ids and provider_ids to optimize database queries
    seeker_ids = relationships.values_list('seeker_id', flat=True)
    provider_ids = relationships.values_list('provider_id', flat=True)
    
    
    # Fetch all relevant Seekers and Providers in bulk
    seekers = Seeker.objects.filter(seeker_id__in=seeker_ids).values(
        'seeker_id', 'seeker_first_name', 'seeker_last_name', 'seeker_email'
    )
    providers = Provider.objects.filter(provider_id__in=provider_ids).values(
        'provider_id', 'provider_first_name', 'provider_last_name', 'provider_email'
    )
    
    print(f"Seekers data fetched-----!!!!:>>> {seekers}")
    
    # Create dictionaries for quick lookup by seeker_id and provider_id
    seekers_dict = {s['seeker_id']: s for s in seekers}
    providers_dict = {p['provider_id']: p for p in providers}
    
    # Prepare the data list to be returned in the JSON response
    data = []
    for relationship in relationships:
        seeker = seekers_dict.get(relationship.seeker_id)
        provider = providers_dict.get(relationship.provider_id)
        
        # Ensure both seeker and provider exist
        if seeker and provider:
            seeker_full_name = f"{seeker['seeker_first_name']} {seeker['seeker_last_name'] or ''}".strip()
            provider_full_name = f"{provider['provider_first_name']} {provider['provider_last_name'] or ''}".strip()
            
            data.append({
                'seeker_name': seeker_full_name if seeker_full_name else 'N/A',
                'seeker_email': seeker['seeker_email'] if seeker['seeker_email'] else 'N/A',
                'provider_name': provider_full_name if provider_full_name else 'N/A',
                'provider_email': provider['provider_email'] if provider['provider_email'] else 'N/A',
                'relationship': relationship.relationship if relationship.relationship else 'N/A',
            })
    
    return JsonResponse({'seekers': data})

# def get_open_inprogress_data(request):
#     client_name = request.GET.get('client_name', '')
#     project_name = request.GET.get('project_name', '')

#     # Fetch ClientProjects based on client_name and project_name filters
#     client_projects = CliPr.objects.all()
    
#     open_inprogress_data = client_projects.filter(client_name__icontains=client_name, project_name__icontains=project_name, status__in=['Open', 'In-Progress'])
#     print(f"Filtered ClientProjects: {client_projects}")

#     # Prepare the data to send back as JSON
#     data = []

#     for project in open_inprogress_data:
#         data.append({
#             'seeker_name': project.seeker_name,
#             'seeker_email': project.seeker_email,
#             'provider_name': project.provider_name,
#             'provider_email': project.provider_email,
#             'relationship': project.relationship,
#             'status': project.status,
#         })

#     # Return the collected data as a JSON response
#     return JsonResponse({'client_projects': data}, safe=False)


# View to fetch seeker emails dynamically
def fetch_emails(request):


    client_name = request.GET.get('client_name', '').strip()
    project_name = request.GET.get('project_name', '').strip()
    status = request.GET.get('status', '').strip().lower()  # Ensure the status is lowercase for consistent filtering

    # Fetch ClientProjects based on client_name and project_name filters
    client_projects = ClientProject.objects.all()
    if client_name:
        client_projects = client_projects.filter(client_name__iexact=client_name)
    if project_name:
        client_projects = client_projects.filter(project_name__iexact=project_name)

    # Debugging logs to check if client_projects is being filtered correctly
    print(f"Filtered ClientProjects: {client_projects}")

    # Fetch relationships excluding those with relationship='self' (case-insensitive)
    valid_relationships = ProviderRelationshipView.objects.filter(cp__in=client_projects).exclude(relationship__iexact='self')
    valid_relationships_self = RelationshipView.objects.filter(cp__in=client_projects, relationship__iexact='self')
    # Extract related seeker and provider IDs
    
    valid_provider_ids = valid_relationships.values_list('provider_id', flat=True)
    valid_seeker_ids = valid_relationships_self.values_list('seeker_id', flat=True)
    # Initialize querysets for seekers and providers, excluding relationships with 'self'
    seekers = Seeker.objects.filter(pk__in=valid_seeker_ids)
    providers = Provider.objects.filter(pk__in=valid_provider_ids)
    super_users = SuperUser.objects.filter(cp__in=client_projects)

    seeker_status_cp = SeekerStatusView.objects.all()
    seeker_status_data = seeker_status_cp.filter(client_name__icontains=client_name, project_name__icontains=project_name, status__in=['Open', 'In-Progress'])
    print(f"Filtered Seeker data:::::------->>>>> {seeker_status_data}")
    
    provider_status_cp = ProviderStatusView.objects.all()
    provider_status_data = provider_status_cp.filter(client_name__icontains=client_name, project_name__icontains=project_name, status__in=['Open', 'In-Progress'])
    print(f"Filtered Provider data::::::------->>>>> {provider_status_data}")

    # Apply status filter (case-insensitive)
    valid_statuses = ['open', 'in-progress', 'completed']
    if status.lower() in [s.lower() for s in valid_statuses]:  # Check case-insensitively
        seekers = seekers.filter(status__iexact=status)
        providers = providers.filter(status__iexact=status)
        
    # Debugging logs to ensure the filtering by status works
    print(f"Filtered Seekers (status={status}): {seekers}")
    print(f"Filtered Providers (status={status}): {providers}")

    # Collect email lists
    seekers_emails = [seeker.seeker_email for seeker in seekers]
    provider_emails = [provider.provider_email for provider in providers]
    super_emails = [super_user.super_user_email for super_user in super_users]

    # Debugging logs to check final output
    print(f"Seekers Emails: {seekers_emails}")
    print(f"Providers Emails: {provider_emails}")
    print(f"Super Users Emails: {super_emails}")

    seeker_status_emails = list(seeker_status_data.values_list('provider_email', flat=True))
    # seeker_status_emails = [seeker_status_data.provider_email for seeker_status_data in seeker_status_data]
    seeker_status_emails = set(seeker_status_emails)
    seeker_status_emails = list(seeker_status_emails)
    print(f"Seeker Status Emails: {seeker_status_emails}")
    
    provider_status_emails = list(provider_status_data.values_list('provider_email', flat=True))
    #provider_status_emails = [provider_status_emails.provider_email for provider_status_emails in provider_status_emails]
    provider_status_emails = set(provider_status_emails)
    provider_status_emails = list(provider_status_emails)
    print(f"Provider Status Data: {provider_status_emails}")

    return JsonResponse({'seeker_emails': seekers_emails, 
                         'provider_emails': provider_emails, 
                         'super_emails': super_emails,
                         'seeker_status_emails':seeker_status_emails,
                         'provider_status_emails':provider_status_emails,
                         })


# # View to fetch CC email options restricted to relationship = 'Manager'
# def get_cc_emails(request):
#     client_name = request.GET.get('client_name')
#     project_name = request.GET.get('project_name')

#     # Filter ClientProject based on client_name and project_name
#     client_projects = ClientProject.objects.all()
#     if client_name:
#         client_projects = client_projects.filter(client_name__icontains=client_name)
#     if project_name:
#         client_projects = client_projects.filter(project_name__icontains=project_name)

#     # Join Relationship and Provider to filter providers with relationship = 'Manager'
#     relationships = Relationship.objects.filter(
#         cp__in=client_projects,  # Match related projects
#         relationship='Manager'   # Filter for 'Manager' relationship
#     ).select_related('provider')  # Optimize query with related field lookup

#     # Collect provider emails from the filtered relationships
#     cc_email_list = [rel.provider.provider_email for rel in relationships]

#     # Return the filtered CC emails
#     return JsonResponse({'ccEmails': cc_email_list})


# 1_1. Unique URL API generation: 
#from .models import Provider
# from .utils import generate_unique_link


# from .utils import generate_unique_url
# from .models import ProviderURL, SuperUserURL


from django.views.decorators.csrf import csrf_exempt
from django.http import StreamingHttpResponse, JsonResponse
import json
import time

sse_messages = []


@csrf_exempt
def send_sse_message(request):
    """
    Receive SSE message from insert_link_code.py and send it to the frontend.
    """
    if request.method == 'POST':
        try:
                # Parse the incoming message from request body
                data = json.loads(request.body.decode('utf-8'))
                message = data.get('message', '')
                
                # Send the message to frontend through SSE
                print("Received message:", message)
                return JsonResponse({'status': 'success', 'message': message})
            
        except Exception as e:
                print(f"Failed to process SSE message: {e}")
                return JsonResponse({'status': 'error', 'message': f"❌ Failed to insert links. Error: {str(e)}"}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)  

# def sse_stream(request):
#     """
#     Stream SSE messages to the frontend in real-time.
#     """
#     def event_stream():
#         while True:
#             # If there are any new messages, send them
#             if sse_messages:
#                 message = sse_messages.pop(0)
#                 yield f"data: {message}\n\n"
#             time.sleep(1)

#     # ✅ Return a streaming response
#     response = StreamingHttpResponse(event_stream(), content_type='text/event-stream')
#     response['Cache-Control'] = 'no-cache'
#     response['X-Accel-Buffering'] = 'no'
#     return response


def insert_link(request):
    try:
        # Extract required parameters
        client_name = request.GET.get('client_name', '').strip()
        project_name = request.GET.get('project_name', '').strip()
        email_type = request.GET.get('email_type', '').strip()
        insert_link = request.GET.get('insert_link', 'false').lower() == 'true'
        print(f"Insert_link Email Type:::::>>>>> {email_type}")
        # Fetch client projects
        client_projects = ClientProject.objects.filter(
            client_name__iexact=client_name,
            project_name__iexact=project_name
        )

        if not client_projects.exists():
            return JsonResponse({'error': 'No matching client projects found.'}, status=404)

        if not insert_link:
            return JsonResponse({'message': 'Insert link is not checked. No URLs generated.'})
        
        # Define the path to the background script
        script_path = os.path.join(os.path.dirname(__file__), 'insert_link_code.py')
        print(f"Script Path:::::>>>>> {script_path}")
        # curr_requsts = dict(request.headers)
        # print(f"Current Request:::::>>>>> {curr_requsts}")

        request_data = {
            "client_name": client_name,
            "project_name": project_name,
            "email_type": email_type,
            "insert_link": insert_link,
            "headers": dict(request.headers)
        }
        print(f"Request Data:::::>>>>> {request_data}")

        # Prepare arguments
        args = json.dumps(request_data)
        print(f"Args:::::>>>>> {args}")
        # Run the script in the background (asynchronous)
        subprocess.Popen(
            ['python', script_path, args]
        )

        return JsonResponse({'message': 'URL generation started in the background.'})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
# def insert_link(request):
#     try:
#         # Extract required parameters
#         client_name = request.GET.get('client_name', '').strip()
#         project_name = request.GET.get('project_name', '').strip()
#         email_type = request.GET.get('email_type', '').strip()
#         insert_link = request.GET.get('insert_link', 'false').lower() == 'true'
#         print(f"Insert_link Email Type:::::>>>>> {email_type}")
#         # Fetch client projects
#         client_projects = ClientProject.objects.filter(
#             client_name__icontains=client_name,
#             project_name__icontains=project_name
#         )

#         if not client_projects.exists():
#             return JsonResponse({'error': 'No matching client projects found.'}, status=404)

#         if not insert_link:
#             return JsonResponse({'message': 'Insert link is not checked. No URLs generated.'})
        
#         # # Fetch relationships excluding those with relationship='self' (case-insensitive)
#         # valid_relationships = ProviderRelationshipView.objects.filter(cp__in=client_projects).exclude(relationship__iexact='self')
#         # valid_relationships_self = RelationshipView.objects.filter(cp__in=client_projects, relationship__iexact='self')
#         # # Extract related seeker and provider IDs
#         # valid_seeker_ids = valid_relationships_self.values_list('seeker_id', flat=True)
#         # valid_provider_ids = valid_relationships.values_list('provider_id', flat=True)

#         generated_links = []

#         # Process providers
#         if email_type == "provider" and insert_link:
#             for cp in client_projects:

#                 print(f"cp************ {cp}")
#                 providers = Provider.objects.filter(cp=cp.cp_id)
#                 for provider in providers:
#                     # Check for duplicates
#                     print("checking Provider URL!!")
#                     existing_url = ProviderURL.objects.filter(cp=cp.cp_id, provider_email=provider.provider_email).first()
#                     if not existing_url:
#                         unique_url, unique_id = generate_unique_url(
#                             request, provider.provider_email, "provider", cp.cp_id, provider.provider_id
#                         )
#                         print("Generate link successfully Now going to insert link!!")
#                         ProviderURL.objects.create(
#                             cp=cp,
#                             client_name=cp.client_name,
#                             project_name=cp.project_name,
#                             provider_id=provider.provider_id,
#                             provider_name=f"{provider.provider_first_name} {provider.provider_last_name}",
#                             provider_email=provider.provider_email,
#                             provi_url=unique_url,
#                             unique_id=unique_id
#                         )
#                         generated_links.append({
#                             'email': provider.provider_email,
#                             'url': unique_url,
#                             'unique_id': str(unique_id)
#                         })

#         # Process superusers
#         if email_type == "superuser" and insert_link:
#             for cp in client_projects:
#                 superuser = SuperUser.objects.filter(cp=cp.cp_id).first()
#                 print()
#                 if superuser:
#                     # Check for duplicates
#                     print("checking Superuser URL!!")
#                     existing_url = SuperUserURL.objects.filter(cp=cp.cp_id, superuser_email=superuser.super_user_email).first()
#                     if not existing_url:
#                         unique_url, unique_id = generate_unique_url(
#                             request, superuser.super_user_email, "superuser", cp.cp_id
#                         )
#                         print("Generate link successfully Now going to insert link!!")
#                         SuperUserURL.objects.create(
#                             cp=cp,
#                             client_name=cp.client_name,
#                             project_name=cp.project_name,
#                             superuser_name=f"{superuser.super_user_first_name} {superuser.super_user_last_name}",
#                             superuser_email=superuser.super_user_email,
#                             super_url=unique_url,
#                             unique_id=unique_id
#                         )
#                         generated_links.append({
#                             'email': superuser.super_user_email,
#                             'url': unique_url,
#                             'unique_id': str(unique_id)
#                         })

#         # Process providers
#         if email_type == "seeker" and insert_link:
#             for cp in client_projects:
#                 seekers = Seeker.objects.filter(cp=cp.cp_id)
#                 print(f"cp************ {cp.cp_id}")
#                 for seeker in seekers:
#                     # Check for duplicates
#                     print("checking Seeker URL!!")
#                     existing_url = SeekerURL.objects.filter(cp=cp.cp_id, seeker_email=seeker.seeker_email).first()
#                     print(f"existing_url************ {existing_url}")
#                     if not existing_url:
#                         #for provider in providers:
#                         seeker_provider_id = RelationshipView.objects.filter(cp__in=client_projects, seeker_id = seeker.seeker_id, relationship__iexact='self').first()
#                         provider = Provider.objects.filter(cp__in=client_projects, provider_id = seeker_provider_id.provider_id).first()
#                         print(f"provider************ {provider}")
#                         unique_url, unique_id = generate_unique_url(
#                             request, provider.provider_email, "seeker", cp.cp_id, provider.provider_id
#                         )
#                         print(f"unique_url************ {unique_url}")
#                         print("Generate link successfully Now going to insert link!!")
#                         SeekerURL.objects.create(
#                             cp=cp,
#                             client_name=cp.client_name,
#                             project_name=cp.project_name,
#                             seeker_id=seeker.seeker_id,
#                             seeker_name=f"{seeker.seeker_first_name} {seeker.seeker_last_name}",
#                             seeker_email=seeker.seeker_email,
#                             seeker_url=unique_url,
#                             unique_id=unique_id
#                         )
                        

#                         generated_links.append({
#                             'email': seeker.seeker_email,
#                             'url': unique_url,
#                             'unique_id': str(unique_id)
#                         })

#         return JsonResponse({
#             'message': 'Unique URLs generated successfully.',
#             'generated_links': generated_links
#         })

#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)
    
# def generate_unique_link(request, provider_email):
#     try:
#         provider = Provider.objects.get(email=provider_email)
#         link = generate_unique_link(provider)
#         return JsonResponse({'success': True, 'link': link})
#     except Provider.DoesNotExist:
#         return JsonResponse({'success': False, 'message': 'Provider not found'})

# # 1_2. Redirect to User Interface:
# from django.shortcuts import render, get_object_or_404
# from .models import Provider

# def user_instructions(request):
#     unique_key = request.GET.get('key')
#     provider = get_object_or_404(Provider, unique_url__contains=unique_key)
#     return render(request, 'user1_instructions.html', {'provider': provider})


# # 1_3. Sending Email:
# from django.core.mail import send_mail
# from .models import Provider

# # def send_feedback_email(request):
# #     if request.method == 'POST':
# #         subject = request.POST['subject']
# #         body = request.POST['emailBody']
# #         client_id = request.POST['client']
# #         project_id = request.POST['project']

# #         providers = Provider.objects.filter(client=client_id, project=project_id)
# #         for provider in providers:
# #             personalized_body = body.replace('>>>>>', f"<a href='{provider.unique_url}'>{provider.unique_url}</a>")
# #             send_mail(subject, personalized_body, 'admin@neucode.com', [provider.email], fail_silently=False)
        
# #         return JsonResponse({'success': True})
# #     return JsonResponse({'success': False, 'message': 'Invalid request'})

from bs4 import BeautifulSoup
def extract_text_from_html(html_content: str) -> str:
    """
    Extracts text from an HTML string using BeautifulSoup.
    
    Args:
        html_content (str): The HTML content string.
    
    Returns:
        str: Extracted plain text from the HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    text_content = soup.get_text(strip=True)

    # Regular expression to match valid URLs
    url_pattern = r'(http[s]?://[^\s<>"]+|www\.[^\s<>"]+)'
    match = re.search(url_pattern, text_content)
    
    # Return the first matched URL or an empty string
    return match.group(0) if match else ""

from django.shortcuts import render, redirect
# from django.core.mail import EmailMessage
# from django.utils.html import strip_tags
from django.contrib import messages
import html
import re
from django.core.mail import EmailMultiAlternatives

#import html2text

# def compose_email(request):
#     if request:
#         # Get form data
#         client_name = request.POST.get('client_name', '').strip() or request.GET.get('client_name', '').strip() 
#         project_name = request.POST.get('project_name', '').strip() or request.GET.get('project_name', '').strip() 
#         print(f"client_name:::::>>>>> {client_name}")
#         print(f"project_name:::::>>>>> {project_name}")
#         subject = request.POST.get('subject', '')
#         email_field = request.POST.get('email_field', '')
#         cc_field = request.POST.get('cc_input', '')
#         email_body = request.POST.get('emailBody', '')  # Contains HTML from TinyMCE
#         email_type = request.POST.get('email_type', '').strip() or request.GET.get('email_type', '').strip() # Email type selected by the user at the frontend
#         print(f"Email type:::::>>>>> {email_type}")
#         #insert_link = request.POST.get('insert_link', 'false').lower() == 'true'

#         client_projects = ClientProject.objects.filter(client_name__icontains=client_name, project_name__icontains=project_name)
#         if client_name:
#             client_projects = client_projects.filter(client_name__icontains=client_name)
#         if project_name:
#             client_projects = client_projects.filter(project_name__icontains=project_name)
#         print(f"client_projects!!!!!!!!!!!!!!:::::>>>>> {client_projects}")

#         client_project_id = [cp.cp_id for cp in client_projects]
#         print(f"client_project_id >>>>>>>>>>> {client_project_id}")
#         # Decode HTML entities in the email body
#         email_body_template = html.unescape(email_body)

#         # Parse email addresses
#         recipient_list = [email.strip() for email in email_field.split(',') if email.strip()]
#         cc_list = [email.strip() for email in cc_field.split(',') if email.strip()]

#         if not subject or not recipient_list or not email_body_template:
#             messages.error(request, "Subject, Selected Emails, and Email Content are required.")
#             return redirect('admin1_compose_email')

#         try:
#             for email in recipient_list:

#                 print(f"Email Body with HTML for {email}: {email_body_template}")
#                 # Strip HTML tags for plain text emails
#                 # personalize_email_body = strip_tags(email_body_template)
#                 # #personalize_email_body = html2text.html2text(email_body_template)
#                 # print(f"Before link Email Body for {email}: {personalize_email_body}")
#                 # email_body_plain = personalize_email_body
                
#                 email_body_plain = email_body_template
#                 print(f"Before link Email Body for {email}: {email_body_plain}")

#                 # Check for placeholder in the email body
#                 if '>>>>>' in email_body_plain:

#                     if email_type == "provider":
#                         # Fetch the unique URL for the email
#                         provider_url = ProviderURL.objects.filter( cp__in=client_project_id ,provider_email=email).first()
#                         print(f"Provider URL: {provider_url.provi_url}")
#                         # Replace placeholder with the appropriate link email_type == "provider" email_type == "superuser"
#                         if provider_url:
#                             prov_link = provider_url.provi_url
#                             prov_link = extract_text_from_html(prov_link)
#                             print(f'prov_linkkkkkkk:::::>>>>>>> {prov_link}')
#                             email_body_plain = email_body_plain.replace('>>>>>', f'<a href="{prov_link}">{prov_link}</a>')
#                             print(f"Email for {email}: Replaced with Provider URL -> {provider_url.provi_url},     link_in_body ->   {prov_link}")
#                         else:
#                             print(f"No URL found for {email}, keeping placeholder.")

#                     elif email_type == "superuser":
#                         superuser_url = SuperUserURL.objects.filter(cp__in=client_project_id, superuser_email=email).first()
#                         print(f"Superuser URL: {superuser_url}")
#                         if superuser_url:
#                             supe_link = superuser_url.super_url
#                             #supe_link = extract_text_from_html(supe_link)
#                             email_body_plain = email_body_plain.replace('>>>>>', f'<a href="{supe_link}">{supe_link}</a>')
#                             print(f"Email for {email}: Replaced with Superuser URL -> {superuser_url.super_url},     link_in_body ->   {supe_link}")
#                         else:
#                             print(f"No URL found for {email}, keeping placeholder.")


#                     elif email_type == "seeker":
#                         seeker_url = SeekerURL.objects.filter(cp__in=client_project_id, seeker_email=email).first()
#                         print(f"Seeker URL: {seeker_url}")
#                         if seeker_url:
#                             seeker_link = seeker_url.seeker_url
#                             #seeker_link = extract_text_from_html(seeker_link)
#                             email_body_plain = email_body_plain.replace('>>>>>', f'<a href="{seeker_link}">{seeker_link}</a>')
#                             print(f"Email for {email}: Replaced with Seeker URL -> {seeker_url.seeker_url},     link_in_body ->   {seeker_link}")
#                         else:
#                             print(f"No URL found for {email}, keeping placeholder.")
                    
                    
#                     else:
#                         print(f"Invalid email type '{email_type}' for {email}")


#                 print(f"Final Email Body for {email}: {email_body_plain}")
                
#                 url_pattern = r'(http[s]?://[^\s<>"]+|www\.[^\s<>"]+)'
#                 matches = re.findall(url_pattern, email_body_plain)
#                 if matches:
#                     link = matches[0]
#                     email_body_plain_1 = email_body_plain.replace('<p{url_pattern}>', link)
#                     print(f'modified>>>>>>>>>>>>>>>>>>>>>>>>>>> {email_body_plain_1}')
#                 # Send email
#                 email_message = EmailMultiAlternatives(
#                     subject=subject,
#                     body=email_body_plain,  # Use plain text body
#                     from_email='anantsol@neucodetalent.com',
#                     to=[email],
#                     cc=cc_list
#                 )
#                 email_message.attach_alternative(email_body_plain, "text/html")
#                 #email_message.content_subtype = "html"
#                 #email_message.content_subtype = "plain"  # Ensure plain text email
#                 email_message.send(fail_silently=False)

#             messages.success(request, "Emails sent successfully with unique links!")
#         except Exception as e:
#             messages.error(request, f"Error sending email: {str(e)}")

#         JsonResponse({"message": "Report generation started successfully!"})

#     return render(request, 'admin1_compose_email.html')

def compose_email(request):
    if request:
        # Get form data
        client_name = request.POST.get('client_name', '').strip() or request.GET.get('client_name', '').strip() 
        project_name = request.POST.get('project_name', '').strip() or request.GET.get('project_name', '').strip() 
        print(f"client_name:::::>>>>> {client_name}")
        print(f"project_name:::::>>>>> {project_name}")
        subject = request.POST.get('subject', '')
        email_field = request.POST.get('email_field', '')
        cc_field = request.POST.get('cc_input', '')
        email_body = request.POST.get('emailBody', '')  # Contains HTML from TinyMCE
        email_type = request.POST.get('email_type', '').strip() or request.GET.get('email_type', '').strip() # Email type selected by the user at the frontend
        print(f"Email type:::::>>>>> {email_type}")
        #insert_link = request.POST.get('insert_link', 'false').lower() == 'true'

        # ✅ Pack data as JSON
        data = {
            "client_name": client_name,
            "project_name": project_name,
            "subject": subject,
            "email_field": email_field,
            "cc_field": cc_field,
            "email_body": email_body,
            "email_type": email_type,
            "headers": dict(request.headers)
        }

        # ✅ Convert to JSON String
        json_data = json.dumps(data)

        # Path to your script
        script_path = os.path.join(os.path.dirname(__file__), 'send_email_task.py')
        print(f"Access Script_path!!!!!!!!!!!! {script_path}")

        # ✅ Trigger the Background Subprocess
        subprocess.Popen([
            'python', 
            script_path, 
            json_data
        ])

        # ✅ Immediately Return Success Without Blocking
        messages.success(request, "✅ Emails are being sent in the background. You can continue working.")
        print("✅ Emails are being sent in the background. You can continue working.")
        return redirect('admin1_compose_email')
        # return JsonResponse({"message": "Emails are being sent in the background. You can continue working."})
        # return redirect('email_message')

    return render(request, 'admin1_compose_email.html')


# ##################### Page_2: Generate Reports #####################

# # 2. Report Generation Functionality:
def admin2_generate_reports(request):
    return render(request, 'admin2_generate_reports.html')

def fetch_client_fromview(request):
    clients = CliPr.objects.values('client_name').distinct()
    client_list = [{'client_name': client['client_name']} for client in clients]
    return JsonResponse({'clients': client_list})

# Getting project on the bases of client:
def get_projects_by_client_fromview(request, client_name):
    try:
        # Fetch the client object by ID
        # client_name = ClientProject.GET.get('client_name')

        # Fetch projects associated with the client
        projects = list(CliPr.objects.filter(client_name__iexact=client_name).values('project_name').distinct())

        # Check if projects exist for the given client_name
        if not projects:
            return JsonResponse({'error': f'No projects found for client: {client_name}'}, status=404)
        
        print(projects)
        # Return projects and client name
        return JsonResponse({
            'client_name': client_name,
            'projects': projects
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def report_generation_table_fromview(request):
    client_name = request.GET.get('client_name', '')
    project_name = request.GET.get('project_name', '')
    

    # Filter client projects based on the client and project name
    # QuerySet to filter the client projects based on provided parameters
    client_projects = CliPr.objects.all()
    if client_name:
        client_projects = client_projects.filter(client_name__iexact=client_name)
    if project_name:
        client_projects = client_projects.filter(project_name__iexact=project_name)

    
    criteria = OptimumMinimumCriteriaView.objects.filter(cp_id__in=client_projects)

    # min_eligible = 'Yes'
    # optimum_criteria= 'Yes'
    # Prepare the list to collect the response
    data = []

    for project in criteria:
        data.append({
            'seeker_name': project.seeker_name,
            'seeker_email': project.seeker_email,
            'min_eligible': project.minimum_criteria,
            'optimum_criteria': project.optimum_criteria,
        })
    # for project in client_projects:
    #     data.append({
    #         'seeker_name': project.seeker_name,
    #         'seeker_email': project.seeker_email,
    #         'min_eligible': min_eligible,
    #         'optimum_criteria': optimum_criteria,
    #     })

    # Return the collected data as a JSON response
    return JsonResponse({'client_projects': data}, safe=False)

# from django.db.models import F

# def report_generation_table_fromview(request):
#     client_name = request.GET.get('client_name', '')
#     project_name = request.GET.get('project_name', '')

#     # Filter client projects based on the client and project name
#     client_projects = CliPr.objects.all()
#     if client_name:
#         client_projects = client_projects.filter(client_name__icontains=client_name)
#     if project_name:
#         client_projects = client_projects.filter(project_name__icontains=project_name)

#     # Join the client_projects and OptimumMinimumCriteriaView based on cp_id and seeker_id
#     criteria = OptimumMinimumCriteriaView.objects.filter(
#         cp_id__in=client_projects.values('cp_id'),
#         seeker_id__in=client_projects.values('seeker_id')
#     ).annotate(
#         seeker_name=F('cp_id__seeker_name'),
#         seeker_email=F('cp_id__seeker_email')
#     )

#     # Prepare the list to collect the response
#     data = [
#         {
#             'seeker_name': item.seeker_name,
#             'seeker_email': item.seeker_email,
#             'optimum_criteria': item.Optimum_Criteria,
#             'min_criteria': item.Minimum_Criteria,
#         }
#         for item in criteria
#     ]

#     # Return the collected data as a JSON response
#     return JsonResponse({'client_projects': data}, safe=False)

import os
import subprocess
import pandas as pd
import pickle
from django.shortcuts import redirect
from django.contrib import messages

def convert_full_rating_to_dataframe(client_name, project_name):
    # Validate inputs
    if not client_name or not project_name:
        raise ValueError("client_name and project_name are required.")
 
    try:
        print(f'convert_full_rating_to_dataframe::::::::>>>>>> going on!!!!!!')

        # Predefined columns for FullRatingDataView
        full_rating_columns = [
            'cp_id', 'client_name', 'project_name', 'seeker_name', 'seeker_email',
            'provider_email', 'relationship', 'question_text', 'competency', 'feedback_value'
        ]

        # Predefined columns for OpenQuestionView
        open_question_columns = [
            'cp_id', 'client_name', 'project_name', 'seeker_name', 'seeker_email',
            'provider_email', 'relationship', 'question_text', 'feedback_text'
        ]

        assessment_number_view = ['cp_id', 'client_name', 'project_name', 'assessment_type']

        # Fetch data from FullRatingDataView
        full_rating_data = FullRatingDataView.objects.filter(
            client_name=client_name, project_name=project_name
        ).values(*full_rating_columns)

        # Convert to DataFrame or create an empty DataFrame with predefined columns
        full_rating_df = pd.DataFrame(full_rating_data)
        if full_rating_df.empty:
            full_rating_df = pd.DataFrame(columns=full_rating_columns)

        print(f'full_rating_df in function::::::::>>>>>> {full_rating_df}')

        # Fetch data from OpenQuestionView
        open_question_data = OpenQuestionView.objects.filter(
            client_name=client_name, project_name=project_name
        ).values(*open_question_columns)

        # Convert to DataFrame or create an empty DataFrame with predefined columns
        open_question_df = pd.DataFrame(open_question_data)
        if open_question_df.empty:
            open_question_df = pd.DataFrame(columns=open_question_columns)

        print(f'open_question_df in function::::::::>>>>>> {open_question_df}')

        # Fetch data from AssessmentNumberView
        assessment_number_data = AssessmentNumberView.objects.filter(
            client_name=client_name, project_name=project_name
        ).values(*assessment_number_view)

        # Convert to DataFrame or create an empty DataFrame with predefined columns
        p_assessment_number_df = pd.DataFrame(assessment_number_data)
        if p_assessment_number_df.empty:
            p_assessment_number_df = pd.DataFrame(columns=assessment_number_view)

        print(f'assessment_number_df in function::::::::>>>>>> {p_assessment_number_df}')


        # # Filter data from FullRatingDataView
        # full_rating_data = FullRatingDataView.objects.filter(
        #     client_name=client_name, project_name=project_name
        # ).values(
        #     'cp_id', 'client_name', 'project_name', 'seeker_name', 'seeker_email',
        #     'provider_email', 'relationship', 'question_text', 'competency', 'feedback_value'
        # )
 
        # # Convert FullRatingDataView queryset to DataFrame
        # full_rating_df = pd.DataFrame(full_rating_data)
        # print(f'full_rating_df in function::::::::>>>>>> {full_rating_df}')
 
        # # Filter data from OpenQuestionView
        # open_question_data = OpenQuestionView.objects.filter(
        #     client_name=client_name, project_name=project_name
        # ).values(
        #     'cp_id', 'client_name', 'project_name', 'seeker_name', 'seeker_email',
        #     'provider_email', 'relationship', 'question_text', 'feedback_text'
        # )
 
        # # Convert OpenQuestionView queryset to DataFrame
        # open_question_df = pd.DataFrame(open_question_data)
        # print(f'open_question_df in function::::::::>>>>>> {open_question_df}')
        # Return the DataFrames
        return full_rating_df, open_question_df, p_assessment_number_df
 
    except Exception as e:
        raise RuntimeError(f"An error occurred: {str(e)}")

# 2_1. Report Generation Function:
# def run_generate_reports(request):

#     client_name = request.GET.get('client_name', '').strip()
#     project_name = request.GET.get('project_name', '').strip()
    
#     # Debugging: Log the received parameters
#     print(f"Received client_name: {client_name}, project_name: {project_name}")
    
#     # Fetch and process the data as needed
#     convert_full_rating_to_dataframe(client_name, project_name)
#     try:
#         # Path to your script
#         script_path = os.path.join(os.path.dirname(__file__), 'generating_reports.py')
        
#         # Execute the script
#         subprocess.run(['python', script_path], check=True)
        
#         # Add a success message
#         messages.success(request, "Reports generated successfully!")
#     except Exception as e:
#         # Add an error message in case of failure
#         messages.error(request, f"Error generating reports: {e}")
#     return redirect('admin2_generate_reports')  # Redirect back to the same page

def run_generate_reports(request):
    client_name = request.GET.get('client_name', '').strip()
    project_name = request.GET.get('project_name', '').strip()

    # Debugging: Log the received parameters
    print(f"Received client_name: {client_name}, project_name: {project_name}")

    try:
        # Fetch and process the data as needed
        full_rating_df, open_question_df, p_assessment_number_df = convert_full_rating_to_dataframe(client_name, project_name)
        print(f'full_rating_df:: {full_rating_df}')
        print(f'open_question_df:: {open_question_df}')
        print(f'assessment_number_df:: {p_assessment_number_df}')
        # Save DataFrames to temporary files
        temp_dir = os.path.join(os.path.dirname(__file__), 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        # full_rating_path = os.path.join(temp_dir, 'full_rating_df.pkl')
        # open_question_path = os.path.join(temp_dir, 'open_question_df.pkl')

        # full_rating_df.to_pickle(full_rating_path)
        # open_question_df.to_pickle(open_question_path)

        full_rating_path = os.path.join(temp_dir, 'full_rating_df.xlsx')
        open_question_path = os.path.join(temp_dir, 'open_question_df.xlsx')
        p_assessment_number_path = os.path.join(temp_dir, 'p_assessment_number_df.xlsx')

        # Save the DataFrames as Excel files
        full_rating_df.to_excel(full_rating_path, index=False, header=True)
        open_question_df.to_excel(open_question_path, index=False, header=True)
        p_assessment_number_df.to_excel(p_assessment_number_path, index=False, header=True)

        print(f"File Created: full_rating_path={full_rating_path}, open_question_path={open_question_path}, p_assessment_number_path={p_assessment_number_path}")

        # Path to your script
        script_path = os.path.join(os.path.dirname(__file__), 'generating_reports.py')
        print(f"Access Script_path!!!!!!!!!!!! {script_path}")

        # Execute the script and pass file paths as arguments
        # subprocess.Popen(['nohup','python', script_path, full_rating_path, open_question_path, p_assessment_number_path
        # ] , stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        subprocess.Popen(
                    ['python', script_path, full_rating_path, open_question_path, p_assessment_number_path]
                )
        # Add a success message
        return JsonResponse({"message": "Report generation started successfully!"})

    except Exception as e:
        # Add an error message in case of failure
        return JsonResponse({"error": f"Error generating reports: {e}"}, status = 500)
        #messages.error(request, f"Error generating reports: {e}")

    # finally:
    #     # Clean up temporary files if needed
    #     if os.path.exists(temp_dir):
    #         try:
    #             shutil.rmtree(temp_dir)
    #             print(f"Temporary directory cleaned: {temp_dir}")
    #         except Exception as cleanup_error:
    #             print(f"Error cleaning temporary directory: {cleanup_error}")

    #return render(request, 'admin2_generate_reports.html')




# ##################### Page_3: Dashboard #####################

# # 3. Dashboard Functionality:
def admin3_dashboard(request):
    return render(request, 'admin3_dashboard.html')


from django.db.models import Count
from django.http import JsonResponse

def overall_dashboard_header(request):
    # Total participants
    total_participants = CliPr.objects.count()

    # Status-wise count
    overall_counts = CliPr.objects.values('status').annotate(count=Count('status'))

    data = {
        'participants': total_participants,
        'open': next((item['count'] for item in overall_counts if item['status'] == 'Open'), 0),
        'in_progress': next((item['count'] for item in overall_counts if item['status'] == 'In-Progress'), 0),
        'completed': next((item['count'] for item in overall_counts if item['status'] == 'Completed'), 0),
    }
    return JsonResponse(data)


def filtered_dashboard_header(request):
    client_name = request.GET.get('client_name', '')
    project_name = request.GET.get('project_name', '')

    queryset = CliPr.objects.all()

    if client_name:
        queryset = queryset.filter(client_name__iexact=client_name)
    if project_name:
        queryset = queryset.filter(project_name__iexact=project_name)

    # Total participants after filtering
    total_participants = queryset.count()

    # Status-wise count
    filtered_counts = queryset.values('status').annotate(count=Count('status'))

    data = {
        'participants': total_participants,
        'open': next((item['count'] for item in filtered_counts if item['status'] == 'Open'), 0),
        'in_progress': next((item['count'] for item in filtered_counts if item['status'] == 'In-Progress'), 0),
        'completed': next((item['count'] for item in filtered_counts if item['status'] == 'Completed'), 0),
    }
    return JsonResponse(data)

def get_filtered_data_fromview(request):
    client_name = request.GET.get('client_name', '')
    project_name = request.GET.get('project_name', '')
    status_op = request.GET.get('status', '')
    # QuerySet to filter the client projects based on provided parameters
    client_projects = CliPr.objects.all()
    if client_name:
        client_projects = client_projects.filter(client_name__iexact=client_name)
    if project_name:
        client_projects = client_projects.filter(project_name__iexact=project_name)
    if status_op:
        client_projects = client_projects.filter(status__icontains=status_op)
    # Prepare the list to collect the response
    data = []

    for project in client_projects:
        data.append({
            'seeker_name': project.seeker_name,
            'seeker_email': project.seeker_email,
            'provider_name': project.provider_name,
            'provider_email': project.provider_email,
            'relationship': project.relationship,
            'status': project.status,
        })

    # Return the collected data as a JSON response
    return JsonResponse({'client_projects': data}, safe=False)