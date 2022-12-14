# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.db.models import Count
from apps.infraonemail.models import *


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}
    obj_count = Communication.objects.values('sentiment_type').annotate(count=Count('sentiment_type')).order_by()
    for row in obj_count:
        if row.get('sentiment_type', -3) == -1:
            context['negative'] = row.get('count', 0)
        elif row.get('sentiment_type', -3) == 0:
            context['neutral'] = row.get('count', 0)
        elif row.get('sentiment_type', -3) == 1:
            context['positive'] = row.get('count', 0)
    objs = Communication.objects.all().order_by('-creation_time')[:10]
    context["recent_mails"] = objs

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))
