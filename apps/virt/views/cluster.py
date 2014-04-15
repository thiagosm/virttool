# -*- coding: utf-8 -*- 
from django.utils.translation import ugettext as _
from apps.virt.views.base import * 
from lib.utils import shell


class ClusterStatusView(View):
    template_name = 'virt/cluster_status.html'

    def get(self,request,*args,**kwargs):
        result = ''
        sr = shell.Shell()
        result,error = sr.run("""ssh root@10.1.1.3 "echo 'cman_tool status: '; cman_tool status; echo; echo 'cman_tool nodes: '; cman_tool nodes;echo; echo 'dlm_tool: '; dlm_tool ls -n" ""","read")
        return render(request,self.template_name,{'info': result })