# -*- coding: utf-8 -*-

import os
from subprocess import Popen, PIPE
from django.utils.translation import ugettext as _
from django.conf import settings

class Shell:
    def run(self,command, type_=None):
        """
         Execute command shells
        """    
      
        try:
            # if user != root 
            if os.getuid() != 0:
                command = "sudo %s" %command
            if type_:
                p = Popen(command, stdout=PIPE, shell=True)
                if type_ == 'readlines':                            
                    result = []
                    result = [ l for l in p.stdout ]
                    p.communicate()
                    return result
                if type_ == 'read':
                    return p.communicate()
                return None           
            else:
                p = Popen(command,shell=True)
                p.wait()
        except:
            print _(u" Unable to run commands, see Developer ")
            
    
