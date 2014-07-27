from __future__ import print_function
from django import forms
import json
from django.conf import settings
from IPython.core import display
from IPython.html import widgets
from IPython.utils.traitlets import Unicode 

def init_django_forms():
    """ Initializes the django environment if necessary and renders the javascript and css code."""
    try:
        settings.configure()
    except RuntimeError:
        pass
    display.display_html(widget_css, raw=True)
    display.display_html(widget_javascript, raw=True)

widget_css = """
<style>
    .nb-django-form th, .nb-django-form td {
        padding: 11px;
        vertical-align: middle;
    }
    .nb-django-form input, .nb-django-form label, .nb-django-form select {
        margin-bottom: 0px;
    }
    .nb-django-form input[type="checkbox"] {
        margin: 0px;
    }
</style>
"""
widget_javascript = """
<script type="text/javascript">
$.fn.serializeObject = function()
{
    var o = {};
    var a = this.serializeArray();
    $.each(a, function() {
        if (o[this.name] !== undefined) {
            if (!o[this.name].push) {
                o[this.name] = [o[this.name]];
            }
            o[this.name].push(this.value || '');
        } else {
            o[this.name] = this.value || '';
        }
    });
    return o;
};
console.log("hello world");
require(["widgets/js/widget"], function(WidgetManager){
    var DjangoFormView = IPython.WidgetView.extend({
        render: function(){
            // Get rendered form data
            var html = this.model.get("form_html");
            var $form = $("<div>"+html+"</div>");
            this.$form = $form;
            this.updateFormHtml();
            this.model.on('change:form_html', this.updateFormHtml, this);
            this.setElement($form);
        },
        updateFormHtml: function(){
                this.$form.html(this.model.get("form_html"));
                this.$form.find(".nb-django-submit").click($.proxy(this.submitHandler, this));
        },
        submitHandler: function(evt) {
                var json = JSON.stringify(this.$form.find("form").serializeObject());
                this.send(json);
                this.touch();
            },
        events: {
        }
    });
    WidgetManager.register_widget_view('DjangoFormView', DjangoFormView);
});
</script>
"""

class DjangoFormWidget(widgets.DOMWidget):
    """ Turns a Django form class into an interactive widget.
    """
    _view_name = Unicode('DjangoFormView', sync=True)
    value = Unicode(sync=True)
    form_html = Unicode(sync=True)
    def __init__(self, form_class, **kwargs):
        widgets.DOMWidget.__init__(self, **kwargs)
        self.form_class = form_class
        self.errors = widgets.CallbackDispatcher(accepted_nargs=[0, 1])
        self.on_msg(self._handle_custom_msg)
        form = self.form_class()
        self.update_form_html(form)
        self.valid_submit = widgets.CallbackDispatcher(accepted_nargs=[0, 1])
        self.invalid_submit = widgets.CallbackDispatcher(accepted_nargs=[0, 1])
        
    def update_form_html(self, form):
        self.form_html = """<div class='nb-django-form'>
        
        <form><table>
        %s
        </table>
        </form></div>
        <div>
            <button class="nb-django-submit">Ok</button>
        </div>
        """ % (form.as_table(), )
        self.send_state()
    def _handle_custom_msg(self, content):
        data = json.loads(content)
        form = self.form_class(data)
        self.update_form_html(form)
        if form.is_valid():
            self.valid_submit(form)
        else:
            self.invalid_submit(form)

class interactive_form(object):
    def __init__(self, form_class):
        self.form_class = form_class
    def __call__(self, f):
        def wrapped_f(*args):
            f(*args)
        self.f = f
        self.widget = DjangoFormWidget(self.form_class)
        self.widget.valid_submit.register_callback(self.valid)
        self.widget.invalid_submit.register_callback(self.invalid)
        display.display(self.widget)
        
    def valid(self, form):
        self.f(True, form)
    def invalid(self, form):
        self.f(False, form)   
