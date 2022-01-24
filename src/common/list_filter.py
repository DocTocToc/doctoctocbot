from django.contrib import admin

from moderation.models import Category
# with default filter labels (`not Null`, `is Null`)
# list_filter = (by_null_filter('processed', 'Processed'), )

# Processed header with labels based on field name (`processed`, `not processed`)
# list_filter = (by_null_filter('processed', 'Processed', bool_dt=True), )

# Paid header filter with labels based on bool(end_time) (`yes`, `no`)
# list_filter = (by_null_filter('end_time', 'Paid', bool_value=True), )


def by_null_filter(attr, name, null_label='is Null', non_null_label='not Null', bool_dt=False, bool_value=False):

    class ByNullFilter(admin.SimpleListFilter):
        """List display filter to show null/not null values"""
        parameter_name = attr
        title = name

        def lookups(self, request, model_admin):
            if bool_dt:
                label_null = 'not %s' % attr
                label_non_null = attr
            elif bool_value:
                label_null = 'no'
                label_non_null = 'yes'
            else:
                label_null = null_label
                label_non_null = non_null_label

            return (
                ('not_null', label_non_null),
                ('null', label_null)
            )

        def queryset(self, request, queryset):
            filter_string = attr + '__isnull'
            if self.value() == 'not_null':
                is_null_false = {
                    filter_string: False
                }
                return queryset.filter(**is_null_false)

            if self.value() == 'null':
                is_null_true = {
                    filter_string: True
                }
                return queryset.filter(**is_null_true)

    return ByNullFilter


def by_socialuser_category_filter(
        attr,
        name,
    ):

    class BySocialUserCategoryFilter(admin.SimpleListFilter):
        """List display filter to show entries according to Category of
        SocialUser. Model must have a 'socialuser' field."""
        parameter_name = attr
        title = name

        def lookups(self, request, model_admin):
            return list(Category.objects.values_list('pk', 'name'))

        def queryset(self, request, queryset):
            if not self.value():
                return queryset
            return queryset.filter(socialuser__category=int(self.value()))

    return BySocialUserCategoryFilter