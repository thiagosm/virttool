# -*- coding: utf-8 -*- 

from django.http import HttpResponseRedirect, HttpResponse, HttpResponseForbidden
from django.template import RequestContext
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy as reverse
from django.views.generic import FormView, ListView, DetailView, CreateView, DeleteView, UpdateView, TemplateView, View, RedirectView
from django.views import generic
from django.shortcuts import redirect, render, get_object_or_404, render_to_response
from django.contrib import messages
from django.db.models import F,Q, Count, Sum
from django.conf import settings
from django.utils.decorators import method_decorator
from lib.djangoutils import customviews
from apps.virt import models, forms, constants
from django.core.cache import cache

URL403 = settings.URL403