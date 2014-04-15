# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from django.views import generic
from django.contrib import admin
from django.conf import settings

import sys, os

B_URL = ''
if settings.USE_NGINX and settings.BASEURL_ROOT.find('/') != -1:
    B_URL = '%s/' %settings.BASEURL_ROOT[1:]

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^%s403/$' % B_URL, generic.TemplateView.as_view(template_name="403.html"), name='403'),
    url(r'^%saccounts/login/$' % B_URL, 'django.contrib.auth.views.login', name="sys_login"),
    url(r'^%saccounts/logout/$' % B_URL, 'django.contrib.auth.views.logout_then_login', name="sys_logout"),
    
    # Examples:
    # url(r'^$', 'virttool.views.home', name='home'),
    url(r'^virt/', include('apps.virt.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

# Serve os arquivos estaticos quando esta rodando pelo runserver
if 'runserver' in sys.argv:
    urlpatterns += patterns('', url(r'^static/(.*)$', 'django.views.static.serve', kwargs={'document_root': '%s/static' %settings.ROOT_PATH}), )
    