from django.forms.widgets import Textarea

class TextareaWithCounter(Textarea):

    def render(self, name, value, attrs=None, renderer=None):
        attrs.update({'class': 'textareacounter'})
        ret_html = super(TextareaWithCounter, self).render(name, value, attrs, renderer=None)
        return ('{}<div class="counter"><span class="input-counter">'
                '{}</span> chars</div>').format(ret_html, len(value))