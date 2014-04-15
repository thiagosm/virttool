# -*- coding: utf-8 -*-

from django.forms.widgets import Select
from django.utils.html import escape, conditional_escape, format_html_join
from django import forms
from django.utils.safestring import mark_safe
from django.utils.encoding import force_unicode, force_text
from django.core.urlresolvers import reverse
from django.forms.util import  ValidationError
from django.forms.widgets import RadioFieldRenderer


class StrippedCharField(forms.CharField):
    def __init__(self, max_length=None, min_length=None, strip=True, lower=False, *args, **kwargs):
        super(StrippedCharField, self).__init__(max_length, min_length, *args, **kwargs)
        self.strip = strip
        self.lower = lower

    def clean(self, value):
        if self.strip and value:
            value = value.strip()
            if self.lower:
                value = value.lower()
        return super(StrippedCharField, self).clean(value)


class RadioFieldWithoutULRenderer(RadioFieldRenderer):

    def render(self):
        return format_html_join(
            '\n',
            '{0}',
            [(force_text(w), ) for w in self],
        )

class SelectWithDisabled(Select):
    """
    Subclass of Django's select widget that allows disabling options.
    To disable an option, pass a dict instead of a string for its label,
    of the form: {'label': 'option label', 'disabled': True}
    """
    def render_option(self, selected_choices, option_value, option_label):
        option_value = force_unicode(option_value)
        if (option_value in selected_choices):
            selected_html = u' selected="selected"'
        else:
            selected_html = ''
        disabled_html = ''
        if isinstance(option_label, dict):
            if dict.get(option_label, 'disabled'):
                disabled_html = u' disabled="disabled"'
            option_label = option_label['label']
        return u'<option value="%s"%s%s>%s</option>' % (
            escape(option_value), selected_html, disabled_html,
            conditional_escape(force_unicode(option_label)))


class ReadOnlyFieldsMixin(object):
    readonly_fields = ()
    all_fields = False

    def __init__(self, *args, **kwargs):
        super(ReadOnlyFieldsMixin, self).__init__(*args, **kwargs)
        for field in (field for name, field in self.fields.iteritems() 
                                    if name in self.readonly_fields 
                                    or self.all_fields == True):
            field.widget.attrs['disabled'] = 'true'
            field.required = False

    def clean(self):
        cleaned_data = super(ReadOnlyFieldsMixin,self).clean()
        for field in self.readonly_fields:
           cleaned_data[field] = getattr(self.instance, field)
        return cleaned_data
