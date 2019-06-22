from django.utils import six
from django.db import models
from modelcluster.fields import ParentalKey
from wagtail.core.models import Page, Orderable, PageBase
from wagtail.core.fields import RichTextField
from wagtail.admin.edit_handlers import FieldPanel, InlinePanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.search import index
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.contrib.auth import get_user_model
from wagtailmetadata.models import MetadataPageMixin
from modelcluster.fields import ParentalKey, ParentalManyToManyField
from django import forms
from ajax_select import fields


class BlogIndexPage(Page):
    intro = RichTextField(blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('intro', classname="full")    
    ]
    
    def get_context(self, request):
        # Update context to include only published posts, ordered by reverse-chron
        context = super().get_context(request)
        blogpages = self.get_children().live().order_by('-first_published_at')
        context['blogpages'] = blogpages
        return context


def get_anonymous_user():
    return get_user_model().objects.get_or_create(username='anonymous')[0]

class BlogPage(six.with_metaclass(PageBase, MetadataPageMixin, Page)):
    promote_panels = Page.promote_panels + MetadataPageMixin.panels
    date = models.DateField(_("Post date"))
    intro = RichTextField(max_length=500)
    body = RichTextField(blank=True)
    authors = ParentalManyToManyField(
        settings.AUTH_USER_MODEL,
        default=get_anonymous_user
    )

    def main_image(self):
        gallery_item = self.gallery_images.first()
        if gallery_item:
            return gallery_item.image
        else:
            return None

    search_fields = Page.search_fields + [
        index.SearchField('intro'),
        index.SearchField('body'),
    ]

    content_panels = Page.content_panels + [
        #FieldPanel('authors', widget=forms.CheckboxSelectMultiple),
        FieldPanel('authors', widget=fields.AutoCompleteSelectMultipleWidget('authors')),
        #FieldPanel('authors', widget=Select2MultipleWidget),
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('body', classname="full"),
        InlinePanel('gallery_images', label=_("Gallery images")),
    ]


class BlogPageGalleryImage(Orderable):
    page = ParentalKey(BlogPage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]
