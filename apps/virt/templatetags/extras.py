from django.template.defaultfilters import stringfilter, register
from xml.etree import ElementTree

@register.filter(name='memorysizeformat')
@stringfilter
def memorysize(value,typev):      
    size = 0
    try:
        if typev:
            if typev == 'k':
                size = int(long(value) / 1024)
                value = size
            if typev == 'b':
                size = int((long(value) / 1024) / 1024)
                value = size 
        return value
    except:
        return value


@register.filter(name='ndomain')
@stringfilter
def numdomains(value):
    return "%s" %(int(value) -1)

@register.filter(name='libvirtstate')
@stringfilter
def libvirtstate(value):
    try:
        if int(value) == 0:
            return "No State"
        elif int(value) == 1 or int(value) == 2:
            return "Running"
        elif int(value) == 3:
            return "Paused by user"
        elif int(value) == 4:
            return "Being shut down"     
        elif int(value) == 5:
            return "Shut off"      
        elif int(value) == 6:
            return "Crashed"
        else:
            return "?"
    except:
        return "?"

@register.filter(name='libvirtstatelabel')
@stringfilter
def libvirtstatelabel(value):
    try:
        if int(value) == 0:
            return "label-default"
        elif int(value) == 1 or int(value) == 2:
            return "label-primary"
        elif int(value) == 3:
            return "label-warning"
        elif int(value) == 4:
            return "label-info"     
        elif int(value) == 5:
            return "label-default"      
        elif int(value) == 6:
            return "label-danger"
        else:
            return "label-default"
    except:
        return "label-default"
