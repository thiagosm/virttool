# -*- coding: utf-8 -*- 
from django.utils.translation import ugettext as _
from apps.virt.views.base import * 
from lib.virtutils import xmltool, virtclient

class DomainListView(ListView):

    """
      List Domain
    """
    model = models.Domain
    template_name = 'virt/domain_list.html'

    def get_queryset(self):
        f = self.request.GET.get('q')
        if f:
            return self.model.objects.filter(Q(name__icontains=f)|
                                             Q(hostname__icontains=f)|
                                             Q(description__icontains=f)).order_by('node')
        return self.model.objects.all().order_by('node')


class DomainLibvirtView(DetailView):
    """
      Libvirt Domain Info
    """
    model = models.Domain
    template_name = 'virt/domain_libvirt.html'

    def get_context_data(self,**kwargs):
        context = super(DomainLibvirtView, self).get_context_data(**kwargs)
        node_libvirt = None
        cache_libvirt = cache.get('node_%s_libvirt' %self.object.node.id)
        print 'teste', cache_libvirt
        if cache_libvirt:
            print 'CACHE'
            node_libvirt = cache_libvirt
        else:
            print "NO CACHE"
            node_libvirt,e = self.object.node.getlibvirt()
            if node_libvirt:
                cache.add('node_%s_libvirt' %self.object.node.id,node_libvirt)

        context['object_libvirt'] = self.object.getlibvirt(node_libvirt) if self.object.node.active == True else None
        context['output_format'] = self.request.GET.get('format')
        return context



class DomainCreateView(customviews.RestrictedCreateView):
    """
      Create Domain 
    """
    model = models.Domain
    form_class = forms.DomainForm
    template_name = 'virt/domain_form.html'
    url_name = 'home'
    msg_form_success = _(u'Domain registered successfully')

    def form_valid(self, form):
        self.object = form.save()
        self.object.xml = xmltool.build_domain_xml(form.cleaned_data)
        self.object.save()
        self.success_url = reverse('domain_edit', kwargs={'pk':self.object.id})
        return super(DomainCreateView, self).form_valid(form)


class DomainUpdateView(customviews.RestrictedPostUpdateView):
    """
      Update Domain 
    """
    model = models.Domain
    form_class = forms.DomainForm
    template_name = 'virt/domain_form.html'
    msg_form_success = _(u'Domain successfully changed')


    def get_initial(self):
        obj = get_object_or_404(models.Domain, pk=self.kwargs.get('pk'))
        domdict = obj.getdict()
        self.initial = domdict
        for f in obj._meta.fields:
            self.initial[f.name] = obj.__dict__.get(f.name)
        self.initial['node'] = obj.node
        return self.initial.copy()


    def form_valid(self, form):
        self.object = form.save()
        self.object.xml = xmltool.build_domain_xml(form.cleaned_data)
        self.object.save()
        self.success_url = reverse('domain_edit', kwargs={'pk':self.object.id})
        return super(DomainUpdateView, self).form_valid(form)


class DomainDeleteView(customviews.RestrictedDeleteView):
    """
       Delete Domain
    """
    model = models.Domain
    msg_success = _(u'Domain successfully removed')
    url_name = 'home'

    def get(self,request,*args,**kwargs):
        return self.delete(request,*args,**kwargs)

    def delete(self,request,*args,**kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request,self.msg_success)
        return HttpResponseRedirect(self.get_success_url())


#
# Libvirt actions 
#

class LibvirtCreateView(customviews.RestrictedView):
    model = models.Domain
    perm_name = 'create'

    def get(self,request,*args,**kwargs):
        domain = get_object_or_404(models.Domain, pk=kwargs.get('pk'))
        message = virtclient.create(domain)
        messages.info(request,message)
        return redirect(reverse('domain_edit',kwargs={'pk': domain.id}))


class LibvirtRebootView(customviews.RestrictedView):
    model = models.Domain
    perm_name = 'reboot'

    def get(self,request,*args,**kwargs):
        domain = get_object_or_404(models.Domain, pk=kwargs.get('pk'))
        message = virtclient.reboot(domain)
        messages.info(request,message)
        return redirect(reverse('domain_edit',kwargs={'pk': domain.id}))


class LibvirtShutdownView(customviews.RestrictedView):
    model = models.Domain
    perm_name = 'shutdown'

    def get(self,request,*args,**kwargs):
        domain = get_object_or_404(models.Domain, pk=kwargs.get('pk'))
        message = virtclient.shutdown(domain)
        messages.info(request,message)
        return redirect(reverse('domain_edit',kwargs={'pk': domain.id}))


class LibvirtDestroyView(customviews.RestrictedView):
    model = models.Domain
    perm_name = 'destroy'

    def get(self,request,*args,**kwargs):
        domain = get_object_or_404(models.Domain, pk=kwargs.get('pk'))
        message = virtclient.destroy(domain)
        messages.info(request,message)
        return redirect(reverse('domain_edit',kwargs={'pk': domain.id}))


class LibvirtMigrateView(customviews.RestrictedView):
    model = models.Domain
    perm_name = 'migrate'

    def get(self,request,*args,**kwargs):
        domain = get_object_or_404(models.Domain, pk=kwargs.get('pk'))
        node = get_object_or_404(models.Node, pk=kwargs.get('node_pk'))
        message = virtclient.migrate(domain,node)
        messages.info(request,message)
        return redirect(reverse('domain_edit',kwargs={'pk': domain.id}))


class LibvirtResumeView(customviews.RestrictedView):
    model = models.Domain
    perm_name = 'resume'

    def get(self,request,*args,**kwargs):
        domain = get_object_or_404(models.Domain, pk=kwargs.get('pk'))
        message = virtclient.resume(domain)
        messages.info(request,message)
        return redirect(reverse('domain_edit',kwargs={'pk': domain.id}))


class LibvirtSuspendView(customviews.RestrictedView):
    model = models.Domain
    perm_name = 'suspend'

    def get(self,request,*args,**kwargs):
        domain = get_object_or_404(models.Domain, pk=kwargs.get('pk'))
        message = virtclient.suspend(domain)
        messages.info(request,message)
        return redirect(reverse('domain_edit',kwargs={'pk': domain.id}))

    
