from log.forms import RegistrationForm
from django.contrib.auth.models import User
import random
import hashlib
from django.utils import timezone
from django.template import Context
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from .models import UserProfile
from datetime import datetime
from django.contrib import messages


# Create your views here.
def register_user(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        context = {'form': form}
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'])
            user.is_active = False
            user.save()
            salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
            activation_key = hashlib.sha1(salt + user.username).hexdigest()
            now = datetime.today()
            key_expires = datetime(now.year, now.month, now.day + 2)
            profile = UserProfile(user=user, activation_key=activation_key,
                                  key_expires=key_expires)
            profile.save()
            email_subject = 'Your new <bancaldo> fantalega account confirmation'
            # go to https://www.google.com/settings/security/lesssecureapps
            # click on active
            location = reverse("activate", args=(activation_key,))
            activation_link = request.build_absolute_uri(location)
            template = get_template('registration/confirm_email.html')
            context = Context({'user': user.username,
                               'activation_link': activation_link})
            email_body = template.render(context)
            print email_body  # debug
            email = EmailMultiAlternatives(email_subject, email_body,
                                           'no-reply@gmail.com>', [user.email])
            email.attach_alternative(email_body, 'text/html')
            print email_body
            # email.send()  # decomment to send email
            messages.info(request,
                          "A confirmation mail has been sent to you.\n"
                          "You have 2 days before the link expires")
            return redirect('index')
    else:
        form = RegistrationForm()
        context = {'form': form}
    return render(request, 'registration/registration_form.html', context)


def activate(request, activation_key):
    user_profile = get_object_or_404(UserProfile, activation_key=activation_key)
    if user_profile.user.is_active:
        return render(request, 'registration/active.html',
                      {'user': request.user.username})
    if user_profile.key_expires < timezone.now():
        return render(request, 'registration/expired.html',
                      {'user': request.user.username})
    user_profile.user.is_active = True
    user_profile.user.save()
    messages.success(request, "You have confirmed with success!")
    return redirect('reg_success')


def register_success(request):
    return render(request, 'registration/success.html')


def activation_link_expired(request):
    return render(request, 'registration/expired.html')