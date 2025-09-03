import os
import django
import sys
import json
import html
import re

# ✅ Setup Django environment manually
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'NFS_360.settings')
django.setup()

from django.core.mail import EmailMultiAlternatives
from App_Admin.models import ClientProject, ProviderURL, SuperUserURL, SeekerURL, ProviderStatusView, SeekerStatusView
from django.shortcuts import render,redirect
from django.contrib import messages
import requests
import webbrowser

# def render_page_request(message, request_headers):
#     try:
#         host = request_headers.get('Host', 'localhost')
#         protocol = "https" if "https" in host else "http"
        
#         # Construct the dynamic URL
#         sse_url = f"{protocol}://{host}/admin1_compose_email/"

#         # Send the message to the dynamic URL
#         print(f"Sending SSE Message to {sse_url}: {message}")
#         response = requests.get(sse_url, json={"message": message})

#         #webbrowser.open(sse_url)
#         #print("Page rendered successfully!")
#         # Print the response status
#         #print(f"Response: {response.status_code} - {response.text}")
#         print("Page rendered function complete..!!")
#     except Exception as e:
#         print(f"Failed to send SSE Message: {e}")


def send_emails(data):
    """
    Function to send emails without blocking browser.
    """
    try:
        # ✅ Parse the incoming data
        data = json.loads(data)
        client_name = data['client_name']
        project_name = data['project_name']
        subject = data['subject']
        email_field = data['email_field']
        cc_field = data['cc_field']
        email_body = html.unescape(data['email_body'])
        email_type = data['email_type']
        request = data.get("headers", {})

        client_projects = ClientProject.objects.filter(client_name__icontains=client_name, project_name__icontains=project_name)
        if client_name:
            client_projects = client_projects.filter(client_name__iexact=client_name)
        if project_name:
            client_projects = client_projects.filter(project_name__iexact=project_name)
        print(f"client_projects!!!!!!!!!!!!!!:::::>>>>> {client_projects}")

        client_project_id = [cp.cp_id for cp in client_projects]
        print(f"client_project_id >>>>>>>>>>> {client_project_id}")
        # Decode HTML entities in the email body
        email_body_template = html.unescape(email_body)

        # Parse email addresses
        recipient_list = [email.strip() for email in email_field.split(',') if email.strip()]
        cc_list = [email.strip() for email in cc_field.split(',') if email.strip()]

        if not subject or not recipient_list or not email_body_template:
            messages.error(request, "Subject, Selected Emails, and Email Content are required.")
            print(f"Subject, Selected Emails, and Email Content are required.")
            return redirect('admin1_compose_email')

        
        for email in recipient_list:

            print(f"Email Body with HTML for {email}: {email_body_template}")
            # Strip HTML tags for plain text emails
            # personalize_email_body = strip_tags(email_body_template)
            # #personalize_email_body = html2text.html2text(email_body_template)
            # print(f"Before link Email Body for {email}: {personalize_email_body}")
            # email_body_plain = personalize_email_body
            
            email_body_plain = email_body_template
            print(f"Before link Email Body for {email}: {email_body_plain}")

            # Check for placeholder in the email body
            if '>>>>>' in email_body_plain:

                if email_type == "provider":
                    # Fetch the unique URL for the email
                    provider_url = ProviderURL.objects.filter( cp__in=client_project_id ,provider_email=email).first()
                    print(f"Provider URL: {provider_url.provi_url}")
                    # Replace placeholder with the appropriate link email_type == "provider" email_type == "superuser"
                    if provider_url:
                        prov_link = provider_url.provi_url
                        #prov_link = extract_text_from_html(prov_link)
                        print(f'prov_linkkkkkkk:::::>>>>>>> {prov_link}')
                        email_body_plain = email_body_plain.replace('>>>>>', f'<a href="{prov_link}">{prov_link}</a>')
                        print(f"Email for {email}: Replaced with Provider URL -> {provider_url.provi_url},     link_in_body ->   {prov_link}")
                    else:
                        print(f"No URL found for {email}, keeping placeholder.")

                elif email_type == "superuser":
                    superuser_url = SuperUserURL.objects.filter(cp__in=client_project_id, superuser_email=email).first()
                    print(f"Superuser URL: {superuser_url}")
                    if superuser_url:
                        supe_link = superuser_url.super_url
                        #supe_link = extract_text_from_html(supe_link)
                        email_body_plain = email_body_plain.replace('>>>>>', f'<a href="{supe_link}">{supe_link}</a>')
                        print(f"Email for {email}: Replaced with Superuser URL -> {superuser_url.super_url},     link_in_body ->   {supe_link}")
                    else:
                        print(f"No URL found for {email}, keeping placeholder.")


                elif email_type == "seeker":
                    seeker_url = SeekerURL.objects.filter(cp__in=client_project_id, seeker_email=email).first()
                    print(f"Seeker URL: {seeker_url}")
                    if seeker_url:
                        seeker_link = seeker_url.seeker_url
                        #seeker_link = extract_text_from_html(seeker_link)
                        email_body_plain = email_body_plain.replace('>>>>>', f'<a href="{seeker_link}">{seeker_link}</a>')
                        print(f"Email for {email}: Replaced with Seeker URL -> {seeker_url.seeker_url},     link_in_body ->   {seeker_link}")
                    else:
                        print(f"No URL found for {email}, keeping placeholder.")
                
                elif email_type == "seeker_status":
                    seeker_status_url = SeekerStatusView.objects.filter(client_id__in=client_project_id, provider_email=email).first()
                    print(f"Seeker URL: {seeker_status_url}")
                    if seeker_status_url:
                        seeker_status_link = seeker_status_url.seeker_url
                        #open_status_link = extract_text_from_html(open_status_link)
                        email_body_plain = email_body_plain.replace('>>>>>', f'<a href="{seeker_status_link}">{seeker_status_link}</a>')
                        print(f"Email for {email}: Replaced with Open Status URL -> {seeker_status_url.seeker_url},     link_in_body ->   {seeker_status_link}")
                    else:
                        print(f"No URL found for {email}, keeping placeholder.")

                elif email_type == "provider_status":
                    provider_status_url = ProviderStatusView.objects.filter(client_id__in=client_project_id, provider_email=email).first()
                    print(f"Seeker URL: {provider_status_url}")
                    if provider_status_url:
                        provider_status_link = provider_status_url.provider_url
                        #provider_status_link = extract_text_from_html(provider_status_link)
                        email_body_plain = email_body_plain.replace('>>>>>', f'<a href="{provider_status_link}">{provider_status_link}</a>')
                        print(f"Email for {email}: Replaced with Open Status URL -> {provider_status_url.provider_url},     link_in_body ->   {provider_status_link}")
                    else:
                        print(f"No URL found for {email}, keeping placeholder.")

                else:
                    print(f"Invalid email type '{email_type}' for {email}")


            print(f"Final Email Body for {email}: {email_body_plain}")
            
            url_pattern = r'(http[s]?://[^\s<>"]+|www\.[^\s<>"]+)'
            matches = re.findall(url_pattern, email_body_plain)
            if matches:
                link = matches[0]
                email_body_plain_1 = email_body_plain.replace('<p{url_pattern}>', link)
                print(f'modified>>>>>>>>>>>>>>>>>>>>>>>>>>> {email_body_plain_1}')
            # Send email
            email_message = EmailMultiAlternatives(
                subject=subject,
                body=email_body_plain,  # Use plain text body
                #from_email='anantsol@neucodetalent.com',
                from_email='mylearning@neucodetalent.com',
                to=[email],
                cc=cc_list
            )
            email_message.attach_alternative(email_body_plain, "text/html")
            #email_message.content_subtype = "html"
            #email_message.content_subtype = "plain"  # Ensure plain text email
            email_message.send(fail_silently=False)

        #messages.success(request, "Emails sent successfully with unique links!")
        print(f"Emails sent successfully with unique links!")
        #Trigger Internal HTTP Request to Render Page
        #render_page_request("Emails sent successfully with unique links!", request)
        # return render(request, 'admin1_compose_email.html')
    except Exception as e:
        messages.error(request, f"Error sending email: {str(e)}")


if __name__ == "__main__":
    data = sys.argv[1]
    send_emails(data)
