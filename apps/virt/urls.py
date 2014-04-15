# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url
from apps.virt.views import node, domain,device,cluster,home

urlpatterns = patterns('',

    # Home 
    url(r'^$', home.HomeView.as_view(), name='home'),

    # Cluster 
    url(r'^cluster/status/$', cluster.ClusterStatusView.as_view(), name='cluster_status'),

    # Node
    url(r'^node/list/$', node.NodeListView.as_view(), name='node_list'),
    url(r'^node/add/$', node.NodeCreateView.as_view(), name='node_add'),
    url(r'^node/(?P<pk>\d+)/libvirt/$', node.NodeLibvirtView.as_view(), name='node_libvirt'),
    url(r'^node/(?P<pk>\d+)/libvirt/update/$', node.UpdateCapabilitiesView.as_view(), name='node_libvirt_update'),
    url(r'^node/(?P<pk>\d+)/libvirt/update/domains/$', node.UpdateDomainsView.as_view(), name='node_libvirt_updatedomains'),
    url(r'^node/(?P<pk>\d+)/libvirt/create/domains/$', node.CreateALLDomainsView.as_view(), name='node_libvirt_createdomains'),
    url(r'^node/(?P<pk>\d+)/edit/$', node.NodeUpdateView.as_view(), name='node_edit'),
    url(r'^node/(?P<pk>\d+)/delete/$', node.NodeDeleteView.as_view(), name='node_delete'),


    # Domain
    url(r'^domain/list/$', domain.DomainListView.as_view(), name='domain_list'),
    url(r'^domain/add/$', domain.DomainCreateView.as_view(), name='domain_add'),
    url(r'^domain/(?P<pk>\d+)/libvirt/$', domain.DomainLibvirtView.as_view(), name='domain_libvirt'),
    url(r'^domain/(?P<pk>\d+)/edit/$', domain.DomainUpdateView.as_view(), name='domain_edit'),
    url(r'^domain/(?P<pk>\d+)/delete/$', domain.DomainDeleteView.as_view(), name='domain_delete'),
    
    url(r'^domain/(?P<pk>\d+)/libvirt/create/$', domain.LibvirtCreateView.as_view(), name='domain_libvirt_create'),
    url(r'^domain/(?P<pk>\d+)/libvirt/reboot/$', domain.LibvirtRebootView.as_view(), name='domain_libvirt_reboot'),
    url(r'^domain/(?P<pk>\d+)/libvirt/shutdown/$', domain.LibvirtShutdownView.as_view(), name='domain_libvirt_shutdown'),
    url(r'^domain/(?P<pk>\d+)/libvirt/destroy/$', domain.LibvirtDestroyView.as_view(), name='domain_libvirt_destroy'),

    url(r'^domain/(?P<pk>\d+)/libvirt/migrate/(?P<node_pk>\d+)/$', domain.LibvirtMigrateView.as_view(), name='domain_libvirt_migrate'),
    url(r'^domain/(?P<pk>\d+)/libvirt/resume/$', domain.LibvirtResumeView.as_view(), name='domain_libvirt_resume'),
    url(r'^domain/(?P<pk>\d+)/libvirt/suspend/$', domain.LibvirtSuspendView.as_view(), name='domain_libvirt_suspend'),


    # Device
    url(r'^domain/(?P<pk>\d+)/device/(?P<type>\w+)/add/$', device.DeviceCreateView.as_view(), name="device_add"),
    url(r'^device/(?P<pk>\d+)/$', device.DeviceUpdateView.as_view(), name="device_edit"),
    url(r'^device/(?P<pk>\d+)/attach/$', device.DeviceAttachView.as_view(), name="device_attach"),
    url(r'^device/(?P<pk>\d+)/detach/$', device.DeviceDetachView.as_view(), name="device_detach"),
    url(r'^device/(?P<pk>\d+)/delete/$', device.DeviceDeleteView.as_view(), name="device_delete")


)

