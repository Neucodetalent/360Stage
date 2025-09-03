from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from App_Admin.models import UserDateView, ProviderURL, UserSeekerView ,UserProviderView, Question, FeedbackUI, UniqueSeekerProviderView
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
#from datetime import timedelta
# Create your views here.

# user1_instructions:

def user1_instructions(request):

    cp_id = request.GET.get('cp_id')  # Assuming cp_id is passed as a GET parameter
    email = request.GET.get('email')  # Other parameters can be extracted similarly
    provider_id = request.GET.get('provider_id')
    id = request.GET.get('id')

    
    # Fetch data from the UserDateView for the given cp_id
    user_data = get_object_or_404(UserDateView, cp_id=cp_id)

    # # Check if project_end_date exceeds the current date
    #if user_data.project_end_date and user_data.project_end_date <= timezone.now().date():
    if user_data.project_end_date and user_data.project_end_date < timezone.now().date():
        # If the project has ended, prevent the page from opening
        return HttpResponse("<h3 style='color:red; text-align:center;'>The Feedback deadline has passed. You cannot access this page.</h3>")
    
    # Extract evolve_title and deadline
    evolve_title = user_data.client_name
    evolve_project = user_data.project_name
    deadline = user_data.project_end_date.strftime('%d-%m-%Y')  # Format the date as required

    context = {
        'evolve_title': evolve_title,
        'evolve_project': evolve_project,
        'deadline': deadline,
        'cp_id': cp_id,
        'email': email,
        'provider_id': provider_id,
        'unique_id': id,
    }
    
    print(f"Context Data: {context}")
    
    return render(request, 'user1_instructions.html', context)

## user2_provider:

# def user2_provider(request):
#     unique_id = request.GET.get('id')
#     email = request.GET.get('email')
#     cp_id = request.GET.get('cp_id')
#     provider_id = request.GET.get('provider_id')

#     # # Optional: Validate query parameters
#     # if not unique_id or not email or not cp_id or not provider_id:
#     #     return render(request, 'error_page.html', {'message': 'Missing or invalid parameters.'})

#     # Optional: Fetch provider details
#     seeker = get_object_or_404(UserSeekerView, cp_id=cp_id, provider_id=provider_id)
#     user_id = seeker.user_id
#     print(user_id)
#     seeker_id = get_object_or_404(UserSeekerView, cp_id=cp_id, provider_id=provider_id, user_id = user_id)
#     context = {
#         'unique_id': unique_id,
#         'email': email,
#         'cp_id': cp_id,
#         'provider_id': provider_id, 
#         #'seekers': seeker,
#         'seeker_id':seeker_id.seeker_id,
#     }
#     print(f"Context Data: {context}")
#     return render(request, 'user2_provider.html', context)

def user2_provider(request):
    unique_id = request.GET.get('id')
    email = request.GET.get('email')
    cp_id = request.GET.get('cp_id')
    provider_id = request.GET.get('provider_id')
    provider_id = int(provider_id) if provider_id else None
    print(f"provider_id>>>>______:::::: {provider_id}")

    # # Optional: Validate query parameters
    # if not unique_id or not email or not cp_id or not provider_id:
    #     return render(request, 'error_page.html', {'message': 'Missing or invalid parameters.'})
    # Fetch all seekers for the given cp_id and provider_id

    seekers = UserSeekerView.objects.filter(cp_id=cp_id, provider_id=provider_id)
    print(f"seekers>>>>______:::::: {seekers}")
    print(f"Seekers Query: {seekers.query}")
    print(f"Seekers Results: {list(seekers)}")
    # Optional: Fetch provider details
    seeker_provider_list = list(UniqueSeekerProviderView.objects.filter(cp_id=cp_id).values_list('provider_id', flat=True))
    print(seeker_provider_list)
    print(f'seeker_provider_list: >>>>>>>!!!!!>>>>>> : {seeker_provider_list}')

    # Initialize seekerid
    seekerid = None

    # Check if provider_id exists in the list of provider_ids
    if provider_id in seeker_provider_list:
        seekerid_obj = UniqueSeekerProviderView.objects.filter(cp_id=cp_id, provider_id=provider_id).first()
        print(f'seekerid_obj: >>>>>>>: {seekerid_obj}')
        seekerid = seekerid_obj.seeker_id
        print(f'seekerid: >>>>>>>: {seekerid}')
    else:
        seekerid = None

    context = {
        'unique_id': unique_id,
        'email': email,
        'cp_id': cp_id,
        'provider_id': provider_id,
        'seekers': seekers,
        'seekerid':seekerid,
    }
    print(f"Context Data: {context}")
    return render(request, 'user2_provider.html', context)

# def user_table_filtered_data(request):
#     cp_id = request.GET.get('cp_id')
#     provider_id = request.GET.get('provider_id')

#     # if not cp_id or not provider_id:
#     #     return JsonResponse({'error': 'Missing parameters'}, status=400)

#     seekers = UserSeekerView.objects.filter(cp_id=cp_id, provider_id=provider_id).values(
#         'seeker_id', 'seeker_name', 'seeker_email', 'relationship', 'status'
#     )
#     return JsonResponse({'client_projects': list(seekers)})

# def user3_seeking(request):
#     unique_id = request.GET.get('id')
#     email = request.GET.get('email')
#     cp_id = request.GET.get('cp_id')
#     provider_id = request.GET.get('provider_id')
#     print(f'provider_id: >>>>>>>: {provider_id}')
#     seeker_id = request.GET.get('seeker_id')
#     print(f'seeker_id: >>>>>>>: {seeker_id}')

#     # Check if seeker_id is provided
#     if seeker_id==None:
#         print("No seeker_id provided.")
#         return render(request, 'user_no_data.html', {
#             'message': 'Seeker ID is missing. Please provide a valid Seeker ID.',
#         })
#     # Optional: Validate query parameters
#     # if not unique_id or not email or not cp_id or not provider_id:
#     #     return render(request, 'error_page.html', {'message': 'Missing or invalid parameters.'})
#     # Optional: Fetch provider details
#     # provider = get_object_or_404(UserProviderView, cp_id=cp_id, provider_id=provider_id)
#     providers = UserProviderView.objects.filter(cp_id=cp_id, seeker_id= seeker_id)

#     #if not seeker_id.exists():
#         # If the project has ended, prevent the page from opening
#         # return HttpResponse("<h3 style='color:black; text-align:center;'>The Feedback page dont have any Data. You cannot access this page.</h3>")
#         # context = {
#         # 'unique_id': unique_id,
#         # 'email': email,
#         # 'cp_id': cp_id,
#         # 'provider_id': provider_id,
#         # 'seeker_id': seeker_id,
#         # }
#         # return render(request, 'user3_seeking.html', context)

#     # provider_seeker = UniqueSeekerProviderView.objects.filter(cp_id=cp_id, provider_id=provider_id).values_list('seeker_id', flat=True)
#     # print(provider_seeker)

#     # Check if providers are found
#     if not providers.exists():
#         print("No data found for the given seeker_id.")
#         return render(request, 'user_no_data.html', {
#             'message': 'No data available for the provided Seeker ID. Please try again.',
#         })

#     context = {
#         'unique_id': unique_id,
#         'email': email,
#         'cp_id': cp_id,
#         'provider_id': provider_id,
#         'providers': providers,
#     }
#     print(f"Context Data User3: {context}")
#     return render(request, 'user3_seeking.html', context)




def user3_seeking(request):
    unique_id = request.GET.get('id')
    email = request.GET.get('email')
    cp_id = request.GET.get('cp_id')
    provider_id = request.GET.get('provider_id')
    seeker_id = request.GET.get('seeker_id')

    
    print(f'provider_id: >>>>>>>: {provider_id}')
    print(f'seeker_id: >>>>>>>: {seeker_id}')
    # Check if seeker_id is provided
    if seeker_id in [None, "None", ""]:
        print(f'Inside seeker_id None !!!!!!>>>>>>>')
        context = {
            'unique_id': unique_id,
            'email': email,
            'cp_id': cp_id,
            'provider_id': provider_id,
            
        }
        
        return render(request, 'user_no_data.html', context)

    try:
        # Fetch providers
        providers = UserProviderView.objects.filter(cp_id=cp_id, seeker_id=seeker_id)

        if not providers.exists():
            print(f'Inside not providers !!!!!!!>>>>>>>')
            context = {
            'unique_id': unique_id,
            'email': email,
            'cp_id': cp_id,
            'provider_id': provider_id,
            
            }
           
            return render(request, 'user_no_data.html', context)

        context = {
            'unique_id': unique_id,
            'email': email,
            'cp_id': cp_id,
            'provider_id': provider_id,
            'providers': providers,
        }
        
        return render(request, 'user3_seeking.html', context)

    except Exception as e:
        print(f'Inside Exception !!!!!!!>>>>>>>')
        context = {
            'unique_id': unique_id,
            'email': email,
            'cp_id': cp_id,
            'provider_id': provider_id,
            
        }

        return render(request, 'user_no_data.html', context)


def user4_mcq_questions(request):
    unique_id = request.GET.get('id')
    email = request.GET.get('email')
    cp_id = request.GET.get('cp_id')
    provider_id = request.GET.get('provider_id')
    seeker_id = request.GET.get('seeker_id')  # New parameter

    # Optional: Validate query parameters
    # if not unique_id or not email or not cp_id or not provider_id:
    #     return render(request, 'error_page.html', {'message': 'Missing or invalid parameters.'})

    mcq_questions = Question.objects.filter(cp_id=cp_id, question_type='MCQ')
    print(f"mcq_questions: {mcq_questions}")

    seeker_name = UserSeekerView.objects.filter(cp_id=cp_id, seeker_id=seeker_id).values_list('seeker_name', flat=True).first()
    seeker_email = UserSeekerView.objects.filter(cp_id=cp_id, seeker_id=seeker_id).values_list('seeker_email', flat=True).first()
    print(f"Seeker Name: {seeker_name}")
    print(f"Seeker Email: {seeker_email}")

    if request.method == 'POST':
        # Determine if this is a draft or final submission
        if 'save_as_draft' in request.POST:
            feedback_status = 'draft'
        elif 'continue' in request.POST:
            feedback_status = 'continue'
        else:
            feedback_status = None

       
        if feedback_status == 'draft':
            for question in mcq_questions:
                question_id = question.question_id
                feedback_value = request.POST.get(f'rating_{question_id}')
                print(f'Feedback Value for Question {question_id}: {feedback_value}')

                if feedback_value:
                    try:
                        # Get or create the Feedback entry
                        feedback, created = FeedbackUI.objects.get_or_create(
                            cp=cp_id,
                            provider_id=provider_id,
                            seeker_id=seeker_id,
                            question_id=question_id,
                            defaults={
                                'feedback_value': feedback_value,
                                'feedback_status': feedback_status,
                            }
                        )
                        if not created:
                            # Update the feedback entry if it exists
                            feedback.feedback_value = feedback_value
                            feedback.feedback_status = feedback_status
                            feedback.save()
                            print(f'Updated Feedback: {feedback}')
                    
                    except Exception as e:
                        print(f"Error saving feedback for question {question_id}: {str(e)}")

            # Set a success message and redirect
            if feedback_status == 'draft':
                messages.success(request, 'Your answers have been saved as a draft.')
            
            # Redirect with query parameters
            redirect_url = f"{reverse('user4_mcq_questions')}?id={unique_id}&email={email}&cp_id={cp_id}&provider_id={provider_id}&seeker_id={seeker_id}"
            return HttpResponseRedirect(redirect_url)
    
        if feedback_status == 'continue':
            for question in mcq_questions:
                question_id = question.question_id
                feedback_value = request.POST.get(f'rating_{question_id}')
                print(f'Feedback Value for Question {question_id}: {feedback_value}')

                if feedback_value:
                    try:
                        # Get or create the Feedback entry
                        feedback, created = FeedbackUI.objects.get_or_create(
                            cp=cp_id,
                            provider_id=provider_id,
                            seeker_id=seeker_id,
                            question_id=question_id,
                            defaults={
                                'feedback_value': feedback_value,
                                'feedback_status': feedback_status,
                            }
                        )
                        if not created:
                            # Update the feedback entry if it exists
                            feedback.feedback_value = feedback_value
                            feedback.feedback_status = feedback_status
                            feedback.save()
                            print(f'Updated Feedback: {feedback}')
                    
                    except Exception as e:
                        print(f"Error saving feedback for question {question_id}: {str(e)}")

            # Set a success message and redirect
            if feedback_status == 'continue':
                messages.success(request, 'Your answers have been saved successfully. Please fill the following answers.')
            # Redirect with query parameters
            redirect_url = f"{reverse('user5_written_questions')}?id={unique_id}&email={email}&cp_id={cp_id}&provider_id={provider_id}&seeker_id={seeker_id}"
            return HttpResponseRedirect(redirect_url)
    
    
    # Load draft answers for pre-filling
    draft_answers = {
        feedback.question_id: feedback.feedback_value 
        for feedback in FeedbackUI.objects.filter(cp=cp_id, provider_id=provider_id, seeker_id=seeker_id)
    }

    print(f"Draft_Answers: {draft_answers}")


    context = {
        'unique_id': unique_id,
        'email': email,
        'cp_id': cp_id,
        'provider_id': provider_id,
        'seeker_id': seeker_id,
        'questionss': mcq_questions,
        'rating_options': [1, 2, 3, 4, 5, 'N/A'],
        'draft_answers': draft_answers,
        'seeker_name': seeker_name,
        'seeker_email': seeker_email,
    }

    return render(request, 'user4_mcq_questions.html', context)

def user5_written_questions(request):
    unique_id = request.GET.get('id')
    email = request.GET.get('email')
    cp_id = request.GET.get('cp_id')
    provider_id = request.GET.get('provider_id')
    seeker_id = request.GET.get('seeker_id')  # New parameter

    # Optional: Validate query parameters
    # if not unique_id or not email or not cp_id or not provider_id:
    #     return render(request, 'error_page.html', {'message': 'Missing or invalid parameters.'})

    text_questions = Question.objects.filter(cp_id=cp_id, question_type='Open')
    print(text_questions)

    seeker_name = UserSeekerView.objects.filter(cp_id=cp_id, seeker_id=seeker_id).values_list('seeker_name', flat=True).first()
    seeker_email = UserSeekerView.objects.filter(cp_id=cp_id, seeker_id=seeker_id).values_list('seeker_email', flat=True).first()
    print(f"Seeker Name: {seeker_name}")
    print(f"Seeker Email: {seeker_email}")
    
    if request.method == 'POST':
        # Determine if this is a draft or final submission
        if 'save_as_draft' in request.POST:
            feedback_status = 'draft'
        elif 'submit' in request.POST:
            feedback_status = 'complete'
        else:
            feedback_status = None
        

        if feedback_status:
            for question in text_questions:
                question_id = question.question_id
                feedback_text = request.POST.get(f'answer_{question_id}', '').strip()
                print(f'Feedback Text for Question {question_id}: {feedback_text}')
                if feedback_text:
                    try:
                        # Get or create the Feedback entry
                        feedback, created = FeedbackUI.objects.get_or_create(
                            cp=cp_id,
                            provider_id=provider_id,
                            seeker_id=seeker_id,
                            question_id=question_id,
                            defaults={
                                'feedback_text': feedback_text,
                                'feedback_status': feedback_status,
                            }
                            
                        )
                        if not created:
                            # Update the feedback entry if it exists
                            feedback.feedback_text = feedback_text
                            feedback.feedback_status = feedback_status
                            feedback.save()
                            print(f'Updated Feedback: {feedback}')
                    except Exception as e:
                        print(f"Error saving feedback for question {question_id}: {e}")

            # Set success message and redirect
            if feedback_status == 'complete':
                messages.success(request, 'Your responses have been submitted successfully!')
                redirect_url = f"{reverse('user2_provider')}?id={unique_id}&email={email}&cp_id={cp_id}&provider_id={provider_id}"
                return HttpResponseRedirect(redirect_url)
            elif feedback_status == 'draft':
                messages.success(request, 'Your answers have been saved as a draft.')
                redirect_url = f"{reverse('user5_written_questions')}?id={unique_id}&email={email}&cp_id={cp_id}&provider_id={provider_id}&seeker_id={seeker_id}"
                return HttpResponseRedirect(redirect_url)
    
    
    # Load draft answers for pre-filling
    draft_answers = {
        feedback.question_id: feedback.feedback_text
        for feedback in FeedbackUI.objects.filter(cp=cp_id, provider_id=provider_id, seeker_id=seeker_id)
    }


    context = {
        'unique_id': unique_id,
        'email': email,
        'cp_id': cp_id,
        'provider_id': provider_id,
        #'provider': provider,
        'seeker_id': seeker_id,
        'questionss': text_questions,
        
        'draft_answers': draft_answers,

        'seeker_name': seeker_name,
        'seeker_email': seeker_email,
    }

    return render(request, 'user5_written_questions.html', context)