# -*- coding: utf-8 -*- 

from django import http
from django.template.loader import get_template
from django.template import Context
import ho.pisa  as pisa

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

def create_pdf(html):
    """
    Create PDF from html
    """
    buffer = StringIO()
    pdf = pisa.pisaDocument(StringIO(html), buffer)
    pdf_file = buffer.getvalue()
    buffer.close()
    return pdf_file

def render_to_pdf(template_src, context_dict, filename):
    """
     Render html to PDF 
    """
    template = get_template(template_src)
    context = Context(context_dict)
    html  = template.render(context)
    
    response = http.HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'filename=%s' %filename
    pdf = create_pdf(html.encode("UTF-8"))
    
    response.write(pdf)    
    return response
