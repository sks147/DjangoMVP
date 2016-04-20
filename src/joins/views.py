from django.conf import settings

from . import models

from django.shortcuts import render, HttpResponseRedirect, Http404
from joins.models import Join


# Create your views here.

from .forms import EmailForm, JoinForm

# def leaderboard(request):
#     list = Join.objects.all()
#     print list
#     context = {
#         "list" : Join.objects.all()
#     }
#     template = "home.html"
#     return render(request, template, context)

# Create your views here.
def get_ip(request):
    try:
        x_forward = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forward:
            ip = x_forward.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
    except:
        ip = ""
    return ip

import uuid
def get_ref_id():
    ref_id = str(uuid.uuid4())[:11].replace('-', '').lower()
    try:
        id_exists = Join.objects.get(ref_id = ref_id)
        get_ref_id()
    except:
        return ref_id


def share(request, ref_id):
    try:
        join_obj = Join.objects.get(ref_id = ref_id)
        friends_referred = Join.objects.filter(friend = join_obj)
        count = join_obj.referral.all().count()
        ref_url = settings.SHARE_URL + str(join_obj.ref_id)

        context = {
            "ref_id": join_obj.ref_id,
            "count": count,
            "ref_url": ref_url
        }
        template = "share.html"
        return render(request, template, context)
    except:
        raise Http404

def home(request):
    try:
        join_id = request.session['join_id_ref']
        obj = Join.objects.get(id = join_id)

    except:
        obj = None

    form = JoinForm(request.POST or None)
    if form.is_valid():
        new_join = form.save(commit = False)
        email = form.cleaned_data['email']
        new_join_old, created = Join.objects.get_or_create(email = email)

        if created:
            new_join_old.ref_id = get_ref_id()
            #add our friend who referred us to our join model
            if not obj == None:
                new_join_old.friend = obj

            new_join_old.ip_address = get_ip(request)
            new_join_old.save()
            #redirect to the unique id share page 
        return HttpResponseRedirect(new_join_old.ref_id)

    number = Join.objects.count()
    #number is the total count of members

    counter = [] #to store the number of friends
    for obj in Join.objects.all():
        counter.append(obj.referral.all().count())

    # print counter
    queryset = Join.objects.all()
    #print array[0]
    context = {
        "form": form,
        "number": number,
        "queryset" : queryset,
        "counter" : counter
    }
    template = "home.html"
    return render(request, template, context)


