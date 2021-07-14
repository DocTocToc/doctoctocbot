from ..models import FilterSocial
from moderation.models import (
    SocialUser,
    Category,
    SocialMedia,
    Follower,
    Friend,
)
from django.conf import settings
import factory

User = settings.AUTH_USER_MODEL


class SocialMediaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialMedia
        django_get_or_create = ('name',)

    name = "twitter"


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category
        
    name = factory.Sequence(lambda n: "category_name_%d" % n)
    label = factory.Sequence(lambda n: "category_label_%d" % n)


class SocialUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SocialUser

    user_id = factory.Sequence(lambda n: n)
    social_media = factory.SubFactory(SocialMediaFactory)


    @factory.post_generation
    def category(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for category in extracted:
                self.category.add(category)

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user_%d" % n)
    email = "my_name@example.com"
    password = "my_password"
    socialuser = factory.SubFactory(SocialUserFactory)


class FriendFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Friend
        
    user = factory.SubFactory(SocialUserFactory)
    id_list = factory.List([])


class FollowerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Follower
        
    user = factory.SubFactory(SocialUserFactory)
    id_list = factory.List([])


class FilterSocialFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = FilterSocial
        
    social_media = SocialMediaFactory()
    friend_lower = 0
    follower_lower = 0

    @factory.post_generation
    def friend_category(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for category in extracted:
                self.friend_category.add(category)

    @factory.post_generation
    def follower_category(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for category in extracted:
                self.follower_category.add(category)