# -*- coding: utf-8 -*-

import os, sys


from reportlab.lib.pagesizes import A4,letter, landscape, portrait
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, LongTable, TableStyle
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet
from django.utils.translation import ugettext as _

from cStringIO import StringIO


class ReportCanvas:

    def __init__(self,pagesize=landscape(A4)):
        self.buffer = StringIO()
        self.pdfc = canvas.Canvas(self.buffer,pagesize=pagesize)
        self.width, self.height = pagesize
        self.npage = 1
        
    def splitDataList(self,data_list,size):
        return [data_list[i:i+size] for i in range(0, len(data_list), size)]
        
            
    def setFilter(self,formdata,x,y):
        filtro_display = []  
        for f,d in formdata:
            if d:
                filtro_display.append([f,d])
        
        if len(filtro_display) > 0:
            self.pdfc.drawString(x, y, _(u'Filters:'))
            self.pdfc.drawString(x, y-2, _(u'_________________________________'))
            y -= 10
            for f,d in filtro_display:
                y -= 11
                try:
                    self.pdfc.drawString(x, y, _(u'%s: %s' %(f.capitalize(),str(d))))
                except:
                    self.pdfc.drawString(x, y, _(u'%s: %s' %(f.capitalize(),d.__unicode__())))

    def setTitle(self,title,x,y):
        self.pdfc.drawString(x, y, title)
    

    def setPageNumber(self,x,y):
        self.pdfc.drawString(x,y, _(u'Page %s' %self.npage))
        self.npage += 1
    
                
    def setTable(self,data_list,colWidths=None,style=None):
        table = Table(data_list,colWidths=colWidths,style=style)
        w,h = table.wrapOn(self.pdfc,self.width,self.height)
        return table, w,h

 