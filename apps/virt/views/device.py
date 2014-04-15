# -*- coding: utf-8 -*- 
from django.utils.translation import ugettext as _
from apps.virt.views.base import * 
from apps.virt import forms_style
from lib.virtutils import xmltool, virtclient
import copy

class DeviceCreateView(customviews.RestrictedCreateView):
    """
      Create Device 
    """
    model = models.Device 
    template_name = 'virt/device_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.domain = get_object_or_404(models.Domain, pk=self.kwargs.get('pk'))
        return super(DeviceCreateView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DeviceCreateView, self).get_context_data(**kwargs)
        context['domain'] = self.domain
        context['device_type'] = self.kwargs.get('type')
        return context

    def get_form_class(self):
        return forms_style.getFormDevice(self.kwargs.get('type'))

    def form_valid(self, form):
        obj = form.save(commit=False)
        postdata = copy.copy(form.cleaned_data)
        postdata['device_type'] = self.kwargs.get('type')
        xml_desc = xmltool.build_device_xml(postdata)
        print xml_desc, postdata, 
        if len(xml_desc) > 5:
            obj.xml = xml_desc
            obj.domain = self.domain
            obj.device_type = self.kwargs.get('type')
            obj.save()
            print obj 
            self.msg_form_success = _(u'Device registered successfully')
            self.success_url = reverse('domain_edit', kwargs={'pk':obj.domain.id})
        else:
            messages.error(self.request,_(u'Error Device'))
        return super(DeviceCreateView, self).form_valid(form)


class DeviceUpdateView(customviews.RestrictedPostUpdateView):
    """
      Update Device 
    """
    model = models.Device
    template_name = 'virt/device_form.html'

    def get_form_class(self):
        obj = self.get_object()
        return forms_style.getFormDevice(obj.device_type)


    def get_context_data(self, **kwargs):
        context = super(DeviceUpdateView, self).get_context_data(**kwargs)
        obj = self.get_object()
        context['domain'] = obj.domain
        context['device_type'] = obj.device_type
        return context

    def get_initial(self):
        obj = self.get_object()
        devdict = obj.getdict()
        self.initial = {}
        for f in obj._meta.fields:
            devdict[f.name] = obj.__dict__.get(f.name)
        devdict['domain'] = obj.domain
        devdict['device_type'] = obj.device_type
        return devdict

    def form_valid(self, form):
        self.object = form.save(commit=False)
        oldxml = self.object.xml 

        postdata = copy.copy(form.cleaned_data)
        postdata['device_type'] = self.object.device_type
        xml_desc = xmltool.build_device_xml(postdata)

        if len(xml_desc) > 5:
            self.object.xml = xml_desc
            self.object.save() 
            self.msg_form_success = _(u'Device successfully changed')
        else:
            self.object.xml = oldxml 
            messages.error(self.request,_(u'Error, device unchanged'))
        self.success_url = reverse('domain_edit', kwargs={'pk':self.object.domain.id})
        return super(DeviceUpdateView, self).form_valid(form)


class DeviceDeleteView(customviews.RestrictedDeleteView):
    """
       Delete Device
    """
    model = models.Device
    msg_success = _(u'Device successfully removed')
    

    def get(self,request,*args,**kwargs):
        return self.delete(request,*args,**kwargs)

    def delete(self,request,*args,**kwargs):
        self.object = self.get_object()
        self.url_name = reverse('domain_edit',kwargs={'pk':self.object.domain.id})
        self.object.delete()
        messages.success(request,self.msg_success)
        return HttpResponseRedirect(self.get_success_url())


class DeviceAttachView(customviews.RestrictedView):
    model = models.Device 
    perm_name = 'attach'

    def get(self,request,*args,**kwargs):
        device = get_object_or_404(self.model, pk=kwargs.get('pk'))
        message = virtclient.attachdevice(device)
        messages.info(request,message)
        return redirect(reverse('device_edit',kwargs={'pk': device.id}))


class DeviceDetachView(customviews.RestrictedView):
    model = models.Device 
    perm_name = 'detach'

    def get(self,request,*args,**kwargs):
        device = get_object_or_404(self.model, pk=kwargs.get('pk'))
        message = virtclient.detachdevice(device)
        messages.info(request,message)
        return redirect(reverse('device_edit',kwargs={'pk': device.id}))

