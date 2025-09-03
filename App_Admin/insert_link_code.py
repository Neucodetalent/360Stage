import os
import django
import sys
import json
from django.core.management.base import BaseCommand
# Manually set up Django environment
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))) # Ensure script runs in the project directory
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NFS_360.settings')  # Set the Django settings module
django.setup()

from App_Admin.models import ClientProject, Seeker, Provider, SuperUser, RelationshipView, ProviderURL, SuperUserURL, SeekerURL, ProviderRelationshipView
from App_Admin.utils import generate_unique_url
from django.http import JsonResponse

import requests

def send_sse_message(message, request_headers):
    try:
        host = request_headers.get('Host', 'localhost')
        protocol = "https" if "https" in host else "http"
        
        # Construct the dynamic URL
        sse_url = f"{protocol}://{host}/send_sse_message/"

        # Send the message to the dynamic URL
        print(f"Sending SSE Message to {sse_url}: {message}")
        response = requests.post(sse_url, json={"message": message})

        # Print the response status
        print(f"Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to send SSE Message: {e}")


def process_insert_link(args):
    
    
    data = json.loads(args)
    print(f"Data-----------:::::>>>>> {data}")
    client_name = data["client_name"]
    project_name = data["project_name"]
    email_type = data["email_type"]
    insert_link = data["insert_link"]
    request = data.get("headers", {})
    print(f"Email Type:--------::::>>>>> {email_type}")
    print(f"Insert_link--------:::::>>>>> {insert_link}")
    print(f"Request---------:::::>>>>> {request}")
    # Fetch client projects
    client_projects = ClientProject.objects.filter(
        client_name__iexact=client_name,
        project_name__iexact=project_name
    )

    if not client_projects.exists():
        return JsonResponse({'error': 'No matching client projects found.'}, status=404)

    if not insert_link:
        return JsonResponse({'message': 'Insert link is not checked. No URLs generated.'})
    
    # # Fetch relationships excluding those with relationship='self' (case-insensitive)
    # valid_relationships = ProviderRelationshipView.objects.filter(cp__in=client_projects).exclude(relationship__iexact='self')
    # valid_relationships_self = RelationshipView.objects.filter(cp__in=client_projects, relationship__iexact='self')
    # # Extract related seeker and provider IDs
    # valid_seeker_ids = valid_relationships_self.values_list('seeker_id', flat=True)
    # valid_provider_ids = valid_relationships.values_list('provider_id', flat=True)

    generated_links = []

    # Process providers
    if email_type == "provider" and insert_link:
        for cp in client_projects:

            print(f"cp************ {cp}")
            providers = Provider.objects.filter(cp=cp.cp_id)
            for provider in providers:
                # Check for duplicates
                print("checking Provider URL!!")
                existing_url = ProviderURL.objects.filter(cp=cp.cp_id, provider_email=provider.provider_email).first()
                if not existing_url:
                    print(f"provider************ {provider.provider_id}")
                    
                    provider_id_relation = ProviderRelationshipView.objects.filter(cp__in=client_projects, provider_id = provider.provider_id).first()
                    if provider_id_relation is None:
                        print(f"No provider relationship found for provider {provider.provider_id}")
                        continue  # Skip to the next provid
                    
                    print(f"provider_id_relation************ {provider_id_relation}")
                    
                    #providers = Provider.objects.filter(cp__in=client_projects, provider_id = provider_id_relation.provider_id).first()  
                    provider_obj = Provider.objects.filter(cp__in=client_projects, provider_id=provider_id_relation.provider_id).first()

                    if provider_obj is None:
                        print(f"No provider found for provider ID {provider_id_relation.provider_id}")
                        continue

                    unique_url, unique_id = generate_unique_url(
                        request, provider_obj.provider_email, "provider", cp.cp_id, provider_obj.provider_id
                    )
                    print(f"unique_url************ {unique_url}")
                    print("Generate link successfully Now going to insert link!!")
                    ProviderURL.objects.create(
                        cp=cp,
                        client_name=cp.client_name,
                        project_name=cp.project_name,
                        provider_id=provider.provider_id,
                        provider_name=f"{provider.provider_first_name} {provider.provider_last_name}",
                        provider_email=provider.provider_email,
                        provi_url=unique_url,
                        unique_id=unique_id
                    )
                    generated_links.append({
                        'email': provider.provider_email,
                        'url': unique_url,
                        'unique_id': str(unique_id)
                    })

    # Process superusers
    if email_type == "superuser" and insert_link:
        for cp in client_projects:
            superuser = SuperUser.objects.filter(cp=cp.cp_id).first()
            print()
            if superuser:
                # Check for duplicates
                print("checking Superuser URL!!")
                existing_url = SuperUserURL.objects.filter(cp=cp.cp_id, superuser_email=superuser.super_user_email).first()
                if not existing_url:
                    unique_url, unique_id = generate_unique_url(
                        request, superuser.super_user_email, "superuser", cp.cp_id
                    )
                    print(f"unique_url************ {unique_url}")
                    print("Generate link successfully Now going to insert link!!")
                    SuperUserURL.objects.create(
                        cp=cp,
                        client_name=cp.client_name,
                        project_name=cp.project_name,
                        superuser_name=f"{superuser.super_user_first_name} {superuser.super_user_last_name}",
                        superuser_email=superuser.super_user_email,
                        super_url=unique_url,
                        unique_id=unique_id
                    )
                    generated_links.append({
                        'email': superuser.super_user_email,
                        'url': unique_url,
                        'unique_id': str(unique_id)
                    })

    # Process seekers
    if email_type == "seeker" and insert_link:
        for cp in client_projects:
            seekers = Seeker.objects.filter(cp=cp.cp_id)
            print(f"cp************ {cp.cp_id}")
            for seeker in seekers:
                # Check for duplicates
                print("checking Seeker URL!!")
                existing_url = SeekerURL.objects.filter(cp=cp.cp_id, seeker_email=seeker.seeker_email).first()
                print(f"existing_url************ {existing_url}")
                if not existing_url:
                    #for provider in providers:
                    seeker_provider_id = RelationshipView.objects.filter(cp__in=client_projects, seeker_id = seeker.seeker_id, relationship__iexact='self').first()
                    
                    if seeker_provider_id is None:
                        print(f"No provider relationship found for seeker {seeker.seeker_id}")
                        continue  # Skip to the next provid

                    provider = Provider.objects.filter(cp__in=client_projects, provider_id = seeker_provider_id.provider_id).first()
                    print(f"provider************ {provider}")
                    unique_url, unique_id = generate_unique_url(
                        request, provider.provider_email, "seeker", cp.cp_id, provider.provider_id
                    )
                    print(f"unique_url************ {unique_url}")
                    print("Generate link successfully Now going to insert link!!")
                    SeekerURL.objects.create(
                        cp=cp,
                        client_name=cp.client_name,
                        project_name=cp.project_name,
                        seeker_id=seeker.seeker_id,
                        seeker_name=f"{seeker.seeker_first_name} {seeker.seeker_last_name}",
                        seeker_email=seeker.seeker_email,
                        seeker_url=unique_url,
                        unique_id=unique_id
                    )
                    

                    generated_links.append({
                        'email': seeker.seeker_email,
                        'url': unique_url,
                        'unique_id': str(unique_id)
                    })

    # # Completion message
    # completion_message = f"✅ Unique URLs for '{client_name}' - '{project_name}' ({email_type}) have been successfully generated and inserted."
    # print("Completion message: ", completion_message)

    # Send Completion Message
    send_sse_message(f"✅ URLs successfully generated for '{client_name}' - '{project_name}'", request)
    print("Background task completed successfully.")

    # return JsonResponse({'message': completion_message, 'status': 'success'})

if __name__ == "__main__":
    process_insert_link(sys.argv[1])