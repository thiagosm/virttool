# -*- coding: utf-8 -*- 
from django.utils.translation import ugettext as _
from django import forms 
from django.conf import settings
from apps.virt import models, constants
from lib.djangoutils.formfields import StrippedCharField
from lib.djangoutils.modelfields import MACAddressFormField
from lib.virtutils import xmltool
import helpforms

class NodeForm(forms.ModelForm):
    hostname = StrippedCharField(label=_(u'Hostname'),max_length=255, help_text=helpforms.NODE_HOSTNAME)
    node_type = forms.IntegerField(label=_(u'Node Type'), initial=0,
                                                          widget=forms.widgets.Select(choices=constants.VIRT_INTERFACE_NAME), 
                                                          help_text=helpforms.NODE_TYPE)

    defaultbridge = forms.CharField(label=_(u'Bridge Default'), max_length=50, 
                                                                required=False,
                                                                help_text=helpforms.NODE_DEFAULTBRIDGE)

    import_domain = forms.BooleanField(label=_(u'Import Domain?'),  
                                       help_text=helpforms.NODE_IMPORTDOMAINS,
                                       required=False)

    class Meta:
        model = models.Node
        fields = ('hostname', 'name','description', 'node_type','defaultbridge','uri','active','import_domain',)

    class Media:
        js = ('%sjs/jquery-validate/jquery.validate.js' % settings.STATIC_URL,)

        css = {'all': ('%sapp/virt/css/node_form.css' % settings.STATIC_URL,
                       '%scss/box.css' % settings.STATIC_URL,)}

    
class DomainForm(forms.ModelForm):
    
    """ Basic resources """
    memory = forms.IntegerField(label=_(u'Memory'))
    currentMemory = forms.IntegerField(label=_(u'Current Memory'), required=False)
    vcpu = forms.IntegerField(label=_(u'Vcpu'),initial=1)

    """ Host bootloader """
    bootloader = forms.CharField(label=_(u'Boot Loader'),max_length=100, required=False)
    bootloader_args = forms.CharField(label=_(u'Boot Loader args'), max_length=200, required=False)


    """ OS configuration details """
    os_type = forms.ChoiceField(label=_(u'OS Type'), choices=constants.OS_TYPES)
    os_loader = forms.CharField(label=_(u'Loader'), max_length=100, required=False, help_text=helpforms.DOMAIN_OS_LOADER)
    os_arch = forms.CharField(label=_(u'Arch'), max_length=10, required=False, help_text=helpforms.DOMAIN_OS_ARCH)
    os_machine = forms.CharField(label=_(u'Machine'), max_length=10, required=False, help_text=helpforms.DOMAIN_OS_MACHINE)
    os_kernel = forms.CharField(label=_(u'Kernel'), max_length=200, required=False, help_text=helpforms.DOMAIN_OS_KERNEL)
    os_initrd = forms.CharField(label=_(u'Initrd'), max_length=200, required=False, help_text=helpforms.DOMAIN_OS_INITRD)
    os_cmdline = forms.CharField(label=_(u'Boot cmdline'), max_length=200, required=False, help_text=helpforms.DOMAIN_OS_CMDLINE)
    os_boot = forms.ChoiceField(choices=constants.BOOT_TYPES, required=False)

    """ Time keeping """
    clock= forms.ChoiceField(label=_(u'Clock'), required=False, choices=constants.CLOCK_TYPES)
    
    """ Hypervisor features """
    pae = forms.BooleanField(required=False)
    acpi = forms.BooleanField(required=False)
    apic = forms.BooleanField(required=False)
    
    """ Lifecycle control """
    on_poweroff = forms.ChoiceField(label=_(u'Poweroff'), choices=constants.LIFECYCLE_TYPES)
    on_reboot = forms.ChoiceField(label=_(u'Reboot'), choices=constants.LIFECYCLE_TYPES)
    on_crash = forms.ChoiceField(label=_(u'Crash'), choices=constants.LIFECYCLE_TYPES)

    class Meta:
        model = models.Domain             
        exclude = ('state','xml',)


    class Media:
        css = {'all': ('%sapp/virt/css/domain_form.css' %
                       settings.STATIC_URL,)}

    
    

#
# DEVICES
#
class DiskForm(forms.ModelForm):

    disk_type = forms.ChoiceField(label=_(u'Type'), choices=constants.DISK_TYPES)
    device = forms.ChoiceField(label=_(u'Device'), choices=constants.DISKDEV_TYPES)
    source = StrippedCharField(label=_(u'Source'), max_length=128, help_text=helpforms.DEVICE_DISK_SOURCE)
    target = StrippedCharField(label=_(u'Target'), max_length=128, help_text=helpforms.DEVICE_DISK_TARGET)
    target_bus = StrippedCharField(label=_(u'Target Bus'), max_length=10, required=False, help_text=helpforms.DEVICE_DISK_TARGET_BUS)
    driver = StrippedCharField(label=_(u'Driver'), max_length=10, required=False, help_text=helpforms.DEVICE_DISK_DRIVER)
    driver_type = StrippedCharField(label=_(u'Driver Type'), max_length=20, required=False)
    driver_cache = StrippedCharField(label=_(u'Driver Cache'), max_length=20, required=False)
    readonly = forms.BooleanField(label=_(u'Read only ?'), required=False, initial=False)
    shareable = forms.BooleanField(label=_(u'Shareable ?'), required=False, initial=False, help_text=helpforms.DEVICE_DISK_SHAREABLE)
    args = forms.CharField(label=_(u'Args'), widget=forms.Textarea, required=False)

    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)


class InterfaceForm(forms.ModelForm):


    interface_type = forms.ChoiceField(label=_(u'Type'), choices=constants.INTERFACE_TYPES)
    source = StrippedCharField(label=_(u'Source'), max_length=128, required=False, help_text=helpforms.INTERFACE_SOURCE)
    target = StrippedCharField(label=_(u'Target'), max_length=128, required=False, help_text=helpforms.INTERFACE_TARGET)
    mac = MACAddressFormField(label=_(u'MAC Address'), required=False)
    script = StrippedCharField(label=_(u'Script Path'), required=False)
    model = forms.ChoiceField(label=_(u'Model'), required=False, choices=constants.INTERFACE_MODELS)
    args = forms.CharField(label=_(u'Args'), widget=forms.Textarea, required=False)


    # Set Class - jquery Mask
    mac.widget.attrs['class'] = 'mac_field mac'

    def __init__(self, *args, **kwargs):
        super(InterfaceForm, self).__init__(*args, **kwargs)

        if not self.instance.id:
            self.fields['mac'].initial=xmltool.libvirttemplate.macgen(50,self.instance.device_type)[0]

    def clean_source(self):
        interface_type = self.cleaned_data.get('interface_type')
        source = self.cleaned_data.get('source')
        if not source and interface_type == 'bridge':
            raise forms.ValidationError(_(u"Source required for bridge interface"))
        return source

    def clean_mac(self):
        interface_type = self.cleaned_data.get('interface_type')
        mac = self.cleaned_data.get('mac')
        if not mac and interface_type == 'bridge':
            raise forms.ValidationError(_(u"MAC Address required for bridge interface"))
        return mac

    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)

    class Media:
        js = ('%sjs/fieldmask.js' % settings.STATIC_URL,
              '%sjs/jquery.meiomask.js' % settings.STATIC_URL,)

    
class GraphicsForm(forms.ModelForm):


    graphics_type = forms.ChoiceField(choices=constants.GRAPHICTYPES)
    sdl_display = forms.CharField(label=_(u'SDL Display'), max_length=25, required=False)
    sdl_xauth = forms.CharField(label=_(u'SDL Xauth'), max_length=25, required=False)
    sdl_fullscreen = forms.BooleanField(label=_(u'SDL FullScreen ?'), required=False)
    autoport = forms.BooleanField(label=_(u'Auto Port'), required=False, initial=True)
    vnc_port = forms.IntegerField(label=_(u'VNC Port'), required=False)
    vnc_listen = forms.IPAddressField(label=_(u'VNC Listen'), initial='0.0.0.0')
    vnc_passwd = forms.CharField(label=_(u'VNC Password'), required=False)
    
    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)

    
class InputForm(forms.ModelForm):


    input_type = forms.ChoiceField(label=_(u'Type'), choices=constants.INPUT_TYPES)
    bus = forms.ChoiceField(label=_(u'Bus'), choices=constants.INPUT_BUS)

    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)


class EmulatorForm(forms.ModelForm):


    emulator = StrippedCharField(label=_(u'Emulator'), help_text=helpforms.EMULATOR)
   
    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)

    
class SerialForm(forms.ModelForm):


    serial_type = forms.ChoiceField(label=_(u'Type'),choices=constants.SERIAL_TYPES)
    source = StrippedCharField(label=_(u'Source Path'), max_length=128, required=False)
    target = forms.IntegerField(label=_(u'Target Port'), initial=0)   

    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)


class ConsoleForm(forms.ModelForm):


    console_type =  forms.ChoiceField(label=_(u'Type'), choices=constants.CONSOLE_TYPES)  
    source = StrippedCharField(label=_(u'Source Path'), max_length=128, required=False)
    target = forms.IntegerField(label=_(u'Target Port'), initial=0)    

    class Meta:
        model = models.Device
        exclude = ('xml','domain','type','xml',)


class ParallelForm(forms.ModelForm):


    parallel_type = forms.ChoiceField(label=_(u'Type'), choices=constants.PARALLEL_TYPES)
    source = StrippedCharField(label=_(u'Source Path'), max_length=128)
    target = forms.IntegerField(label=_(u'Target Port'), initial=0)    

    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)


# kvm and virtualbox
class HostdevUSBForm(forms.ModelForm):


    hostdev_type =  forms.CharField(label=_(u'Type'),initial='usb')       
    vendor = StrippedCharField(label=_(u'Vendor'), max_length=30)
    product = StrippedCharField(label=_(u'Product'), max_length=30) 

    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)


# kvm and virtualbox
class HostdevPCIForm(forms.ModelForm):


    hostdev_type =  forms.CharField(label=_(u'Type'),initial='pci')    
    bus = StrippedCharField(label=_(u'Bus'), max_length=50)
    slot = StrippedCharField(label=_(u'Slot'), max_length=50)
    function = StrippedCharField(label=_(u'Function'), max_length=50)
 
    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)


class ControllerForm(forms.ModelForm):


    controller_type = StrippedCharField(label=_(u'Type'), max_length=50, initial='scsi')
    index = forms.IntegerField(label=_(u'Index'), initial=0)
    model = forms.CharField(label=_(u'Model'),max_length=10, \
                                widget=forms.Select(choices=constants.VMWARE_SCSI_CONTROLLER),\
                                required=False) 

    class Meta:
        model = models.Device
        exclude = ('xml','domain','device_type',)


class GenericDeviceForm(forms.ModelForm):


    xml = forms.CharField(label=_(u'XML'), widget=forms.Textarea, required=False)

    class Meta:
        model = models.Device
        exclude = ('domain',)
