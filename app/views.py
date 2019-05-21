from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, HttpRequest
from django.urls import reverse
from .forms import CreateForm, LoginForm, SearchForm, EditInterestsForm, ChangePasswordForm, DeleteAccountForm, SimpleSearchForm
from .models import User, Interest
from decimal import Decimal
import django.contrib.auth.hashers as hashers
import requests
import json
import re

# Index page (home page for website, before a user logs in)
def index(request):
    if request.method == 'POST':
        # If Creating New User
        if "interest" in request.POST.keys():
            form = CreateForm(request.POST)
            if form.is_valid():
                # Checks if a user already has that username
                if User.objects.filter(username=form.cleaned_data['username']):
                    return render(request, 'app_templates/ErrorPage.html',
                                {
                                    'error_name': 'Username already taken',
                                    'index': reverse('app:index')
                                })
                # Makes new user
                else:
                    u = User(username=form.cleaned_data['username'],
                             password=hashers.make_password(form.cleaned_data['password']))
                    u.save()
                    initial_interest = Interest(name=form.cleaned_data['interest'].lower(),
                                                strength=form.cleaned_data['strength'],
                                                associated_user=u)
                    initial_interest.save()
                    request.session['user'] = u.id
                    return HttpResponseRedirect(reverse('app:search_page'))
        #Logging in an Existing User
        elif "username" in request.POST.keys():
            form = LoginForm(request.POST)
            if form.is_valid():
                #If username and password match
                if not User.objects.filter(username=form.cleaned_data['username']):
                    return render(request, 'app_templates/ErrorPage.html',
                                  {
                                      'error_name': 'Invalid username.',
                                      'index': reverse('app:index')
                                  })
                u = User.objects.get(username=form.cleaned_data['username'])
                #If password is correct log the user in
                if hashers.check_password(form.cleaned_data['password'], u.password):
                    request.session['user'] = u.id
                    return HttpResponseRedirect("/search_page")
                #If password is incorrect redirect to error page
                else:
                    return render(request, 'app_templates/ErrorPage.html',
                                  {
                                    'error_name': 'Incorrect password.',
                                    'index': reverse('app:index')
                                  })
        #Just Searching without logging in
        else:
            return HttpResponseRedirect("/simple_search")
    return render(request, 'app_templates/index.html',
                {
                    'search_action': reverse('app:simple_search'),
                    'search_form': SimpleSearchForm(),
                })

# Displays appropriate form by interpreting ajax request
def display_form(request):
    if request.GET.get("form") == "create_form":
        form = CreateForm()
    elif request.GET.get("form") == "login_form":
        form = LoginForm()
    elif request.GET.get("form") == "edit_interests_form":
        form = EditInterestsForm()
    elif request.GET.get("form") == "change_password_form":
        form = ChangePasswordForm()
    else:
        form = DeleteAccountForm()
    data = {
        'form': form.as_p()
    }
    request.session['data'] = data
    return JsonResponse(data)

#Renders the users home-search page
def search_page(request):
    user = User.objects.get(id=request.session["user"])
    return render(request, 'app_templates/SearchPage.html',
                {
                    'form': SearchForm(),
                    'username': user.username,
                })

#Titles returned by wiki search for word
def search_wiki_for(word):
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        'action':"query",
        'list':"search",
        'srsearch': word,
        'srlimit':10,
        'format':"json"
    }
    return requests.get(url=URL, params=PARAMS).json()

#Returns the content of a wiki page from its title
#Content does not include images, separate command for that available
def parse_page(title):
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        'action': "parse",
        'page': title,
        'format': "json"
    }
    return(requests.get(url=URL, params=PARAMS).json()["parse"])

#Gets a thumbnail image for a wikipedia page from the pages title and id
#Could use only title, but pageid is readily available so might as well pass it as a parameter
def get_image(title, page_id):
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        'action': "query",
        'prop': "pageimages",
        'titles': title,
        'format': "json",
        'piprop': "original"
    }
    req = requests.get(url=URL, params=PARAMS).json()
    #If an image is available
    if "original" in req["query"]["pages"][str(page_id)].keys():
        return req["query"]["pages"][str(page_id)]["original"]["source"]
    #Otherwise use a default image
    else:
        return "https://cdn.theatlantic.com/assets/media/img/mt/2016/07/AP_671014678252/lead_720_405.jpg?mod=1533691512"

#Gets a wikipedia page url from its page id
def get_url(page_id):
    URL = "https://en.wikipedia.org/w/api.php"
    PARAMS = {
        'action': "query",
        'prop': "info",
        'pageids': page_id,
        'inprop': "url",
        'format': "json",
    }
    req = requests.get(url=URL, params=PARAMS).json()
    return req["query"]["pages"][str(page_id)]["fullurl"]

#Performs a SimpleSearch
def simple_search(request):
    keyword = request.POST["value"]
    #Contains titles of the pages returned by the search
    search_json = search_wiki_for(keyword)
    data = []; entry = []
    for search_result in search_json["query"]["search"]:
        #Title
        entry.append(search_result["title"])
        #Snippet
        entry.append(re.sub('<[^<]+?>', '', search_result["snippet"]) + "...")
        #Image
        entry.append(get_image(search_result["title"], search_result["pageid"]))
        #Relevance
        entry.append(0)
        #Link to wiki page
        entry.append(get_url(search_result["pageid"]))
        data.append(entry)
        entry = []
    return render(request, 'app_templates/SearchResults.html',
                {
                    'disable_edit_account': 1,
                    'form_action':reverse("app:simple_search"),
                    'form': SimpleSearchForm(),
                    'data': data
                })

#Generates a relevance score for a given page and user
def get_relevance_score(page_title, user, additional_interest="", additional_interest_strength=0):
    if additional_interest != "":
        temp_interest = Interest(name=additional_interest, strength=additional_interest_strength, associated_user=user)
        temp_interest.save()
    page_data_string = re.sub('<[^<]+?>', '', json.dumps(parse_page(page_title))).lower()
    relevance = 0
    for interest in Interest.objects.filter(associated_user=user):
        relevance += page_data_string.count(interest.name) * interest.strength
    if additional_interest != "":
        temp_interest.delete()
    return relevance

#Performs a DuckSearch
def search(request):
    #Variables
    keyword = request.POST["value"]
    user = User.objects.get(id=request.session["user"])
    additional_interest = request.POST["additional_interest"]
    additional_interest_strength = request.POST["additional_interest_strength"]
    #Contains titles of the pages returned by the search
    search_json = search_wiki_for(keyword)
    data = []; entry = []
    for search_result in search_json["query"]["search"]:
        #Title
        entry.append(search_result["title"])
        #Snippet
        entry.append(re.sub('<[^<]+?>', '', search_result["snippet"]) + "...")
        #Image
        entry.append(get_image(search_result["title"], search_result["pageid"]))
        #Relevance
        entry.append(get_relevance_score(search_result["title"], user, additional_interest, additional_interest_strength))
        #Link to wiki page
        entry.append(get_url(search_result["pageid"]))
        data.append(entry)
        entry = []
    #Sort the search results
    data.sort(key = lambda val: val[3], reverse = True)
    return render(request, 'app_templates/SearchResults.html',
                {
                    'disable_edit_account': 0,
                    'form_action':reverse("app:search"),
                    'form': SearchForm(),
                    'data': data
                })

# View for user page
def edit_account(request):
    # Checks if user has user id cookie (if not, they're not logged in)
    if request.session.get('user'):
        u = User.objects.get(id=request.session.get('user'))
        queryset_of_interests = Interest.objects.filter(associated_user=u)
        interests = []
        # Displays users interests and their strength value
        for interest in queryset_of_interests:
            interests.append(interest.name + ":      " + str(interest.strength))
        # If User is submitting something
        if request.method == 'POST':
            #Editting Interests
            if "interest" in request.POST.keys():
                form = EditInterestsForm(request.POST)
                if form.is_valid():
                    interest_name = form.cleaned_data['interest'].lower()
                    #Boolean value that specifies whether the user has this interest
                    interest_exists = len(Interest.objects.filter(associated_user=u, name=interest_name)) != 0
                    #If they do then delete it
                    if interest_exists:
                        interest_to_delete = Interest.objects.filter(associated_user=u, name=interest_name)[0]
                        interest_to_delete.delete()
                    #If they don't then create it
                    else:
                        try:
                            new_interest = Interest(name=interest_name,
                                                    strength=form.cleaned_data['strength'],
                                                    associated_user=u)
                            new_interest.save()
                        except:
                            return render(request, 'app_templates/ErrorPage.html',
                                        {
                                            'error_name': 'Please specify the strength of your interest',
                                            'go_back_to': reverse('app:edit_account'),
                                        })
                    return HttpResponseRedirect('/edit_account')
            # If changing password
            elif "new_password" in request.POST.keys():
                    form = ChangePasswordForm(request.POST)
                    if form.is_valid():
                        # If their new passwords don't match
                        if form.cleaned_data['new_password'] != form.cleaned_data['new_password_repeat']:
                            return render(request, 'app_templates/ErrorPage.html',
                                        {
                                            'error_name': 'Your new passwords did not match',
                                            'go_back_to': reverse('app:edit_account'),
                                        })
                        # If password change is successfull
                        else:
                            u.password = hashers.make_password(form.cleaned_data['new_password'])
                            u.save()
                    return HttpResponseRedirect('/')
                # If deleting account
            else:
                form = DeleteAccountForm(request.POST)
                if form.is_valid():
                    # If they do not type in their account name
                    if form.cleaned_data['confirmation'] != u.username:
                        return render(request, 'app_templates/ErrorPage.html',
                                    {
                                        'error_name': 'Account Deletion Aborted',
                                        'go_back_to': reverse('app:edit_account'),
                                    })
                    # If they do type in their account name
                    else:
                        u.delete()
                    return HttpResponseRedirect('/')
        # If GET or other request
        else:
            return render(request, 'app_templates/EditAccount.html',
                        {
                            'form_action': reverse('app:edit_account'),
                            'username': u.username,
                            'interests': interests
                        })
    # User not logged in
    else:
        return render(request, 'app_templates/ErrorPage.html',
                    {
                        'error_name': 'User not logged in!',
                        'go_back_to': reverse('app:edit_account'),
                    })
