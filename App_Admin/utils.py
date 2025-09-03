# from django.urls import reverse
# from django.utils.crypto import get_random_string

# def generate_unique_link(provider):
#     unique_key = get_random_string(length=32)
#     unique_url = reverse('App_User:user1_instructions') + f"?key={unique_key}"
#     provider.unique_url = unique_url
#     provider.save()
#     return unique_url



# from django.urls import reverse
# from django.utils.crypto import get_random_string
# from urllib.parse import urlencode

# def generate_unique_link(provider):
#     # Generate a random key for uniqueness
#     unique_key = get_random_string(length=32)
    
#     # Ensure provider and its related client project exist
#     if provider and provider.cp:
#         # Get client_name and provider_id
#         client_name = provider.cp.client_name.replace(" ", "-").lower()  # URL-friendly client name
#         provider_id = provider.provider_id

#         # Generate the base URL
#         base_url = reverse('App_User:user1_instructions')

#         # Create query parameters
#         query_params = {
#             'key': unique_key,
#             'client_name': client_name,
#             'provider_id': provider_id
#         }
        
#         # Append query parameters to the base URL
#         unique_url = f"{base_url}?{urlencode(query_params)}"
        
#         # Save the unique URL to the provider instance
#         provider.unique_url = unique_url
#         provider.save()

#         return unique_url

#     raise ValueError("Provider or related client project is invalid.")


import uuid
from django.urls import reverse

# def generate_unique_url(request, email, role, cp_id):
#     """
#     Generate a unique URL for the given email, role, and client project ID.
#     """
#     unique_id = uuid.uuid4()
#     if role == "provider":
#         return request.build_absolute_uri(
#             reverse('app_user_instructions') + f"?id={unique_id}&email={email}&cp_id={cp_id}"
#         )
#     elif role == "superuser":
#         return request.build_absolute_uri(
#             reverse('app_user_instructions') + f"?id={unique_id}&email={email}&cp_id={cp_id}"
#         )
#     return None
# def generate_unique_url(request, email, role, cp_id, provider_id=None):
#     """
#     Generate a unique URL for the given email, role, and client project ID.
#     """
#     unique_id = uuid.uuid4()
#     if role == "provider":
#         return request.build_absolute_uri(
#             #reverse('App_User:user1_instructions') + f"?id={unique_id}&email={email}&cp_id={cp_id}&provider_id={provider_id}"
#             reverse('user1_instructions') + f"?id={unique_id}&email={email}&cp_id={cp_id}&provider_id={provider_id}"
#         )
#     elif role == "superuser":
#         return request.build_absolute_uri(
#             #reverse('App_Superuser:superuser1_dashboard') + f"?id={unique_id}&email={email}&cp_id={cp_id}"
#             reverse('superuser1_dashboard') + f"?id={unique_id}&email={email}&cp_id={cp_id}"
#         )
#     return None

# from django.utils.http import urlencode

# def generate_unique_url(request, email, role, cp_id, provider_id=None):
#     """
#     Generate a unique URL for the given email, role, and client project ID.
#     """
#     unique_id = uuid.uuid4()  # Generate a unique ID for the link
#     base_url = request.build_absolute_uri('/')[:-1]  # Get the base URL (e.g., http://127.0.0.1:8000)

#     if role == "provider":
#         # Build provider URL
#         query_params = urlencode({"id": unique_id, "email": email, "cp_id": cp_id, "provider_id": provider_id})
#         return f"{base_url}/user1_instructions/?{query_params}"

#     elif role == "superuser":
#         # Build superuser URL
#         query_params = urlencode({"id": unique_id, "email": email, "cp_id": cp_id})
#         return f"{base_url}/superuser1_dashboard/?{query_params}"

#     return None
from typing import Tuple
from django.utils.http import urlencode
from django.http import HttpRequest
import uuid
from bs4 import BeautifulSoup
import os

def extract_text_from_html(html_content: str) -> str:
    """
    Extracts text from an HTML string using BeautifulSoup.
    
    Args:
        html_content (str): The HTML content string.
    
    Returns:
        str: Extracted plain text from the HTML content.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    return soup.get_text(strip=True)



def generate_unique_url(request: HttpRequest, email: str, role: str, cp_id: int, provider_id: int = None, unique_id: uuid.UUID = None) -> Tuple[str, uuid.UUID]:
    """
    Generate a unique URL for the given email, role, and client project ID, and optionally reuse a provided unique_id.
    
    Args:
        request (HttpRequest): The HTTP request object to get the base URL.
        email (str): The email address to include in the URL.
        role (str): The role for which the URL is generated ('provider' or 'superuser').
        cp_id (int): Client project ID.
        provider_id (int, optional): Provider ID (only for providers). Defaults to None.
        unique_id (UUID, optional): Reuse an existing unique ID. Defaults to None.
    
    Returns:
        tuple: Generated URL and the unique ID.
    """

    # Clean the email input using BeautifulSoup
    email_cleaned = extract_text_from_html(email)

    # Use provided unique_id or generate a new one
    unique_id = unique_id or uuid.uuid4()
    
    # # Get the base URL (e.g., http://127.0.0.1:8000)
    # base_url = request.build_absolute_uri('/')[:-1]
    
    # Get the global base URL from environment variables or default to the request host
    #global_host = os.environ.get('Hostname_Neucode', 'ncprod-gnhjdyhgbpbphsem.eastus2-01.azurewebsites.net')
    global_host = os.environ.get('Hostname_Neucode', 'app.neucodetalent.com')
    base_url = f"https://{global_host}"

    if role == "provider":
        query_params = {
            "id": unique_id,
            "email": email_cleaned,
            "cp_id": cp_id,
            "provider_id": provider_id
        }
        encoded_query = urlencode(query_params)
        #return f"{base_url}/user1_instructions/?{encoded_query}", unique_id

        provider_url = f"{base_url}/user1_instructions/?{encoded_query}"
        print(f"provider_url: {provider_url}")
        # Clean the generated URL

        return extract_text_from_html(provider_url), unique_id


    elif role == "superuser":
        query_params = {
            "id": unique_id,
            "email": email_cleaned,
            "cp_id": cp_id
        }
        encoded_query = urlencode(query_params)
        #return f"{base_url}/superuser1_dashboard/?{encoded_query}", unique_id
        superuser_url = f"{base_url}/superuser1_dashboard/?{encoded_query}"
        # Clean the generated URL
        return extract_text_from_html(superuser_url), unique_id
    

    elif role == "seeker":
        query_params = {
            "id": unique_id,
            "email": email_cleaned,
            "cp_id": cp_id,
            "provider_id": provider_id
        }
        encoded_query = urlencode(query_params)
        #return f"{base_url}/user1_instructions/?{encoded_query}", unique_id
        provider_url = f"{base_url}/user1_instructions/?{encoded_query}"
        # Clean the generated URL
        return extract_text_from_html(provider_url), unique_id

    return None, unique_id



