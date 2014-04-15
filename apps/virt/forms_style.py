# -*- coding: utf-8 -*- 
from apps.virt import forms, constants

def getFormDevice(typedev):

    tdev = typedev
    
    if tdev in constants.DEVICE_TYPE_LIST:
        if tdev == 'disk':
            return forms.DiskForm
        elif tdev == 'controller':
            return forms.ControllerForm
        elif tdev == 'interface':
            return forms.InterfaceForm
        elif tdev == 'graphics':
            return forms.GraphicsForm
        elif tdev == 'input':
            return forms.InputForm
        elif tdev == 'console':
            return forms.ConsoleForm
        elif tdev == 'serial':
            return forms.SerialForm
        elif tdev == 'parallel':
            return forms.ParallelForm
        elif tdev == 'emulator':
            return forms.EmulatorForm
        else:
            return forms.GenericDeviceForm
    else:
        return forms.GenericDeviceForm



