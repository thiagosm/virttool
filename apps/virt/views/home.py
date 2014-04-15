# -*- coding: utf-8 -*- 
from django.utils.translation import ugettext as _
from apps.virt.views.base import * 
from lib.virtutils import xmltool

class HomeView(View):
  template_name = 'virt/home.html'
  def get(self,request,*args,**kwargs):
    return render(request,self.template_name,{})