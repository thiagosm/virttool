# -*- coding: utf-8 -*- 
from django.utils.translation import ugettext as _
from apps.virt.views.base import * 


class NodeListView(ListView):
    """
      List Node
    """
    model = models.Node
    template_name = 'virt/node_list.html'

    def get_queryset(self):
        f = self.request.GET.get('q')
        if f:
            return self.model.objects.filter(Q(name__icontains=f)|Q(hostname__icontains=f))
        return self.model.objects.all()


class NodeLibvirtView(DetailView):
    """
      Libvirt Node Info
    """
    model = models.Node
    template_name = 'virt/node_libvirt.html'

    def get_context_data(self,**kwargs):
        context = super(NodeLibvirtView, self).get_context_data(**kwargs)
        if self.request.GET.get('format') != 'node_libvirt_table':
            context['object_libvirt'] = self.object.getlibvirt() if self.object.active == True else None
        context['output_format'] = self.request.GET.get('format')
        return context


class NodeCreateView(customviews.RestrictedCreateView):
    """
      Create Node 
    """
    model = models.Node
    form_class = forms.NodeForm
    template_name = 'virt/node_form.html'
    url_name = 'home'

    def form_valid(self, form):
        self.object = form.save()

        # getting libvirt virConnect instance to optimize register
        libvirtnode, libvirterror_ = self.object.getlibvirt()

        # update capabilities, name, state from libvirt 
        self.object.updateCapabilities(libvirtnode=libvirtnode)

        if form.cleaned_data.get('import_domain'):
            self.object.importDomains(libvirtnode=libvirtnode)
            self.msg_form_success=_(u'Node registered successfully')

        self.success_url = reverse('node_edit', kwargs={'pk':self.object.id})
        return super(NodeCreateView, self).form_valid(form)


    def get_context_data(self,**kwargs):
        context = super(NodeCreateView, self).get_context_data(**kwargs)
        context['URIHELP'] = constants.DRIVERS_DESCRIPTION
        return context


class NodeUpdateView(customviews.RestrictedPostUpdateView):
    """
      Update Node
    """
    model = models.Node
    form_class = forms.NodeForm
    template_name = 'virt/node_form.html'

    msg_form_success = _(u'Node successfully changed')
    msg_form_unchanged = _(u'Node unchanged')

    def get_success_url(self):
        return reverse('node_edit',kwargs={'pk': self.object.id})

    def get_context_data(self,**kwargs):
        context = super(NodeUpdateView, self).get_context_data(**kwargs)
        context['URIHELP'] = constants.DRIVERS_DESCRIPTION
        return context


class NodeDeleteView(customviews.RestrictedDeleteView):
    """
       Delete Node
    """
    model = models.Node
    msg_success = _(u'Node successfully removed')
    url_name = 'home'

    def get(self,request,*args,**kwargs):
        return self.delete(request,*args,**kwargs)

class UpdateDomainsView(View):
    """
      Import Domains from Libvirt 
    """
    def get(self,request,*args,**kwargs):
        node_object = get_object_or_404(models.Node, pk=kwargs.get('pk'))
        node_object.importDomains()
        messages.success(request,_(u"Domains imported Node %s" %node_object.name))
        return redirect(reverse('node_edit',kwargs={'pk': node_object.id}))

class UpdateCapabilitiesView(View):
    """
       Update capabilities from Libvirt
    """
    def get(self,request,*args,**kwargs):
        node_object = get_object_or_404(models.Node, pk=kwargs.get('pk'))
        node_object.updateCapabilities()
        messages.success(request,_(u"Updated Capabilities"))
        return redirect(reverse('node_edit',kwargs={'pk': node_object.id}))

class CreateALLDomainsView(View):
    """
       Update capabilities from Libvirt
    """
    def get(self,request,*args,**kwargs):
        node_object = get_object_or_404(models.Node, pk=kwargs.get('pk'))
        from lib.virtutils import virtclient
        for domain in node_object.domain_set.filter(active=True):
            message = virtclient.create(domain)
            messages.success(request,message)
        return redirect(reverse('node_edit',kwargs={'pk': node_object.id}))



