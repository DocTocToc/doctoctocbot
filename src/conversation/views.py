import logging
from django.shortcuts import render
from dry_rest_permissions.generics import DRYPermissions, DRYPermissionFiltersBase
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets
from .serializers import HashtagSerializer
from .models import Hashtag
from django.views.generic import ListView
from django.contrib.postgres.search import (
    SearchQuery,
    SearchHeadline,
    SearchRank,
)
from django.contrib.sites.shortcuts import get_current_site
from common.twitter import status_url_from_id
from django.db.models import F, Q, Func
from django.db.models.functions import Coalesce
from .models import Treedj, Tweetdj
from common.mixins import AdminStaffRequiredMixin

logger = logging.getLogger(__name__)

def show_conversations(request):
    return render(request, "conversation/status.html", {'treedj': Treedj.objects.all()})


class HashtagFilterBackend(DRYPermissionFiltersBase):
    action_routing = True


class HashtagViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows hashtag objects to be viewed.
    """
    permission_classes = (IsAuthenticated, DRYPermissions,)
    #permission_classes = (AllowAny, DRYPermissions,)
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer


class SearchResultsList(AdminStaffRequiredMixin, ListView):
    model = Tweetdj
    context_object_name = "statuses"
    template_name = "conversation/search.html"
    paginate_by = 20

    @staticmethod
    def search_query(query, config, search_type):
        return SearchQuery(
            query,
            config=config,
            search_type=search_type,
        )

    @staticmethod
    def is_websearch(query):
        def starts_with_dash(query):
            for w in query.split():
                if w[0] == "-":
                    return True

        _is_websearch = (
            ' OR ' in query or '"' in query or starts_with_dash(query)
        )
        logger.debug(f'{_is_websearch=}')
        return _is_websearch

    def get_queryset(self):
        query = self.request.GET.get("q")
        if not query:
            return []
        lang = self.request.GET.get("lang")
        lang_dct = {
            "fr": "french_unaccent",
            "en": "english",
            "null": None  
        }
        search_type="websearch"
        try:
            config = lang_dct[lang]
        except:
            config = "french_unaccent"
        q_filter = Q(
            status_text=SearchResultsList.search_query(
                query, config, search_type
            )
        )
        """
        q_split : list = query.split()
        if q_split and not SearchResultsList.is_websearch(query):
            query_or = " OR ".join(q_split)
            q_filter = (
                q_filter
                |
                Q(
                    status_text=SearchResultsList.search_query(
                        query_or,
                        config,
                        search_type
                    )
                )
            )
        """
        vector = F('status_text')
        search_query = SearchResultsList.search_query(query, config, search_type)
        qs = (
            Tweetdj.objects
            .exclude(retweetedstatus=True)
            .filter(q_filter)
            .annotate(rank=SearchRank(vector,search_query))
            .order_by('-rank', '-statusid')
        )
        if not lang == "null":
            qs = qs.filter(
                Q(json__lang=lang) | Q(socialuser__language__tag=lang)
            )
        logger.debug(f'{qs.count()=}')
        return qs.annotate(
            highlight=SearchHeadline(
                Coalesce("json__full_text", "json__text"),
                query,
                highlight_all=True,
                start_sel='<mark>',
                stop_sel='</mark>',
            )
        )

    def get_context_data(self, **kwargs):
        context = super(SearchResultsList, self).get_context_data(**kwargs)
        query = self.request.GET.get('q')
        request_lang = self.request.GET.get('lang')
        context['query'] = query
        try:
            tag = self.request.user.socialuser.language.tag
        except:
            site = get_current_site(self.request)
            tag = site.community.language
        context['lang'] = request_lang or tag
        return context