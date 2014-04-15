# -*- coding: utf-8 -*- 
from django.db import models
from django.db.models import F,Q
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext as _d
from django.conf import settings

from lib.virtutils import xmltool
from lib.utils import snmp
import sys

import libvirt
import signal
import helpforms
import constants

class TimeoutException(Exception): 
    pass

class Node(models.Model):    
    
    name = models.CharField(_('Name'), max_length=100, unique=True)
    hostname = models.CharField(_('Hostname'), max_length=255)
    uri = models.CharField(_('URI'), max_length=255, null=True, blank=True, default=None)
    description = models.CharField(_('Description'), blank=False, max_length=255)
    node_type = models.IntegerField(_('Node Type'), db_column='type', 
                                                default=0, 
                                                choices=constants.VIRT_INTERFACE_NAME)
    state = models.IntegerField(default=0, choices=constants.NODE_STATE)
    capabilities = models.TextField(null=True,blank=True)
    defaultbridge = models.CharField(_('Bridge Default'), max_length=50, 
                                                          null=True, blank=True,
                                                          default=None)

    active = models.BooleanField(_('Active'), default=True)
    date_created = models.DateTimeField(db_column='datecreated', auto_now_add=True)
    date_modified = models.DateTimeField(db_column='datemodified', auto_now=True)
    
    def __unicode__(self):
        return self.name


    def getlibvirt(self):
        """
          Return instance libvirt.virConnect and 
          dict(libvirt.libvirtError[code,message])
        """

        def timeout_handler(signum, frame):
            raise TimeoutException()

        #if 'runserver' in sys.argv:
        #    # Agora comeceu a gambiarra (pedido do evandro) 
        #    signal.signal(signal.SIGALRM, timeout_handler) 
        #    signal.alarm(10) # triger alarm in 10 seconds


        VIRT_INTERFACE_ = constants.VIRT_INTERFACE_URI[self.node_type] %self.hostname
        URI = self.uri or VIRT_INTERFACE_
   
        try:    
            try:
                return libvirt.open(URI), None                       
            except libvirt.libvirtError, le:
                return None, dict(code=le.get_error_code(), msg=le.get_error_message())
        except TimeoutException:
            return None, dict(code=le.VIR_ERR_OPERATION_TIMEOUT, msg="timeout connection powered by evandro")   
        
    
    @property
    def libvirtDomains(self):
        domains = []
        libvirtnode, libvirterror_ = self.getlibvirt()
        for d in self.domain_set.all():
            domains.append({'domain': d, 'libvirtdomain': d.getlibvirt(libvirtnode) if libvirtnode else None})
        return domains

    def updateCapabilities(self,autosave=True,libvirtnode=None):
        """
          Update name, capabilities, state from libvirt 
        """
        if libvirtnode:
            libvirtnode_, error_ = libvirtnode,None
        else:
            libvirtnode_, error_ = self.getlibvirt()
        if libvirtnode_:
            self.capabilities = libvirtnode_.getCapabilities()
            self.state = 1
        else:
            self.state = 2            
        if autosave == True:
            self.save()

            
    def getNetworkInterfaces(self,version=1,community="public"):
        """
          Get network interfaces via SNMP 
        """
        snmp_ = snmp.Snmp()
        devlist = []
        NOTLISTED=['vif','lo']
        
        for dev in snmp_.snmpwalk(self.hostname,"1.3.6.1.2.1.2.2.1.2",version,community):
            invalidfound = False
            for nl in NOTLISTED:
                if dev.split('STRING:')[1].strip().startswith(nl):
                    invalidfound=True
            if invalidfound == False:
                devlist.append(dev.split('STRING:')[1].strip())
        return devlist
                    

    def importDomains(self,libvirtnode=None):
        """
          Import all domains from Node 
        """        
        if libvirtnode:
            libvirtnode_, erro_ = libvirtnode, None
        else:
            libvirtnode_, error_ = self.getlibvirt()
            
        if libvirtnode_:
            libvirtdomains = [ libvirtnode_.lookupByID(ID) for ID in libvirtnode_.listDomainsID()[1:] ]
            for libvirtdomain in libvirtdomains:
                
                # import domains
                if Domain.objects.filter(name=libvirtdomain.name()).count() == 0:
                    new_domain = Domain()
                    new_domain.name=libvirtdomain.name()
                    new_domain.description='Virtual Machine %s' %libvirtdomain.name()
                    new_domain.node=self
                    new_domain.state=libvirtdomain.info()[0]
                    
                    if self.defaultbridge:
                        options = dict(defaultbridge=self.defaultbridge)
                    else:
                        options = None
                        
                    xmlf = xmltool.getxml(libvirtdomain.XMLDesc(0), options)
                    new_domain.domain_type = xmlf.get('type')
                    new_domain.xml= xmlf.get('domain')
                    new_domain.save()
                    
                    # import devices
                    for d in xmlf.get('devices'):
                        new_device = Device()
                        new_device.domain = new_domain
                        new_device.device_type = d.get('type')
                        new_device.xml = d.get('xml')
                        new_device.save()
    

    def getdict(self):
        """
           Return Capabilities dictionary python 
        """
        return xmltool.get_capabilities_dict(self.capabilities)
        
                        
    class Meta:
        ordering = 'name',
        verbose_name = _('Node')
        verbose_name_plural = (_('Nodes'))
        


class Domain(models.Model):

    node = models.ForeignKey(Node, verbose_name=_('Node'))
    name = models.CharField(_('Name'), max_length=100)
    uuid = models.CharField(_('UUID'), max_length=36,blank=True)
    hostname = models.CharField(_('Host'), max_length=200, blank=True, null=True, default=None)
    description = models.CharField(_('Description'), blank=False, max_length=200)
    domain_type = models.CharField(_('Type'), db_column='type', max_length=20, choices=constants.DOM_TYPES)
    xml = models.TextField(_('XML'))
    autostart = models.BooleanField(_('Auto start'), default=True)
    priority = models.IntegerField(_('Priority'), default=10)    
    state = models.IntegerField(default=0, choices=constants.DOMAIN_STATE)
    date_created = models.DateTimeField(db_column='datecreated', auto_now_add=True)
    date_modified = models.DateTimeField(db_column='datemodified', auto_now=True)
    
    
    def getlibvirt(self,libvirtnode=None):
        """
          Return Domain libvirt
        """     
          
        if libvirtnode:
            libvirtnode_, error_ = libvirtnode, None
        else:
            libvirtnode_, error_ = self.node.getlibvirt()
        try:    
            return libvirtnode_.lookupByName(self.name), error_
        except:
            return None, error_
            
    
    def updateState(self,libvirtnode=None):
        """
           Update state Domain 
        """
        
        # 96 = Powered Off by user, 97 = Wait Migrate, 98 = Powered Off, 99 = Disabled
        if self.state not in [96,97,99]:   
            change=False         
            state = self.state
            libvirtdomain, error_ = self.getlibvirt(libvirtnode)
            if libvirtdomain:
                state_ = libvirtdomain.info()[0]
                if state_ != state:
                    change=True
                    self.state = state_
            else:
                self.state = 98
                change=True
                
            if change == True:
                self.save()
    
    
    #
    #  GETs Devices 
    #
    
    def getEmulator(self):
        return self.device_set.filter(device_type='emulator')
    def getDisk(self):
        return self.device_set.filter(device_type='disk')                            
    def getInterface(self):
        return self.device_set.filter(device_type='interface')        
    def getGraphics(self):
        return self.device_set.filter(device_type='graphics')
    def getInput(self):
        return self.device_set.filter(device_type='input')
    def getConsole(self):
        return self.device_set.filter(device_type='console')
    def getSerial(self):
        return self.device_set.filter(device_type='serial')
    def getParallel(self):
        return self.device_set.filter(device_type='parallel')
    def getChannel(self):
        return self.device_set.filter(device_type='channel')    
    def getSound(self):
        return self.device_set.filter(device_type='sound')
    def getVideo(self):
        return self.device_set.filter(device_type='video')
    def getHostdev(self):
        return self.device_set.filter(device_type='hostdev')
    def getController(self):
        return self.device_set.filter(device_type='controller')
            
    
    
    def getdict(self):
        """
           Return Domain dictionary python 
        """
        return xmltool.get_domain_dict(self.xml)
                    
    
    def getXML(self):
        """
           Return Domain XML Format 
        """
        
        xmldomain = str()
        xmldomain = self.xml

        xmldomain = xmldomain.replace('</domain>','')
        xmldomain+="<devices>\n"
        for devicetype in ['emulator',
                           'disk',
                           'controller',
                           'interface',
                           'graphics',
                           'input',
                           'parallel',
                           'serial',
                           'console',
                           'channel',
                           'sound',
                           'video',
                           'hostdev']:
            for dxml in self.device_set.filter(device_type=devicetype):
                xmldomain+="%s\n" %dxml.xml
        xmldomain+="</devices>\n</domain>"

        return xmldomain
            
    
    def __unicode__(self):
        return self.name 
        
        
    class Meta:
        ordering = 'name',
        verbose_name = _('Domain')
        verbose_name_plural = (_('Domains'))

        permissions = (
            ("create_domain" , _d(u"Can create Domain")),
            ("destroy_domain" , _d(u"Can destroy Domain")),
            ("shutdown_domain" , _d(u"Can shutdown Domain")),
            ("reboot_domain" , _d(u"Can reboot Domain")),
            ("resume_domain" , _d(u"Can resume Domain")),
            ("suspend_domain" , _d(u"Can suspend Domain")),
            ("migrate_domain" , _d(u"Can migrate Domain")),

        )

        
#
#  Transport Domain
#
class Transport(models.Model):
    node = models.ForeignKey(Node, verbose_name=_('Node'))
    domain = models.ForeignKey(Domain, verbose_name=_('Domain'))

    def __unicode__(self):
        return "%s %s" %(self.node, self.domain)

    class Meta:
        ordering = 'node',
        verbose_name = _('Transport')
        verbose_name_plural = (_('Transport List'))

#
# Devices
#
class Device(models.Model):
    
    domain = models.ForeignKey(Domain, verbose_name=_('Domain'))
    description = models.CharField(_('Description'), max_length=255, null=True, blank=True, default=None)
    device_type = models.CharField(_('Device Type'), db_column='type', max_length=50, choices=constants.DEVICE_TYPES)  
    xml = models.TextField(_('XML'))
    
    def __unicode__(self):
        return "%s - %s : %s" %(self.domain,self.device_type,self.description)
    
    
    
    def isConnected(self,libvirtdomain=None):
        """
           Return Boolean
           Check if device is connected
        """
        try:
            if libvirtdomain:
                libvirtdomain_, error_ = libvirtdomain, None
            else:
                libvirtdomain_, error_ = self.domain.getlibvirt()
            if libvirtdomain_:
                # current domain xml - libvirt 
                domxml = xmltool.getxml(libvirtdomain_.XMLDesc(0))         
                # list devices 
                for devicexml in domxml.get('devices'):         
                    # check type 
                    devicedict = xmltool.get_device_dict(devicexml.get('xml'))                
                    # if device is valid 
                    if devicedict:
                        # check type 
                        if devicedict.get('type') == self.device_type:
                            # check device == device from (XMLDesc)
                            if self.getdict() == devicedict:
                                return True
        except Exception, e:
            print e
            pass
            
        return False
        

    
    def getdict(self):
        """
           Return Device dictionary python
        """
        return xmltool.get_device_dict(self.xml)
    
                
    class Meta:
        ordering = 'device_type',
        verbose_name = _('Device')
        verbose_name_plural = (_('Devices'))

        permissions = (
            ("attach_device" , _d(u"Can attach Device")),
            ("detach_device" , _d(u"Can detach Device")),
        )


