from django.contrib.gis.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class School(models.Model):
    tag = models.CharField(max_length=255, blank=False)
    slug = models.SlugField(null=True)
    name = models.CharField(max_length=255, blank=False)
    university = models.CharField(max_length=255, blank=False)
    geometry = models.PointField()
    
    @property
    def tooltip(self):
        return f"{self.tag}"

    @property
    def popup(self):
        return '{} - {} - {}'.format(
            self.name,
            self.university,
            self.id,
        )

    def __str__(self):
        return f"{self.tag}"

    class Meta:
        # order of drop-down list items
        ordering = ('tag',)


class Discipline(models.Model):
    name = models.CharField(max_length=255, blank=False)
    slug = models.SlugField(null=True)
    label = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return f"{self.label}"

    class Meta:
        ordering = ('name',)


class Diploma(models.Model):
    name = models.CharField(max_length=255, blank=False)
    slug = models.SlugField(null=True)
    label = models.CharField(max_length=255, blank=False)
    discipline = models.ForeignKey(
        'Discipline',
        on_delete=models.CASCADE,
        related_name='diploma',
    )

    def __str__(self):
        return f"{self.label}"

    class Meta:
        ordering = ('name',)


class Room(models.Model):
    school = models.ForeignKey(
        'School',
        on_delete=models.CASCADE,
        related_name='room',
    )
    diploma = models.ForeignKey(
        'Diploma',
        on_delete=models.CASCADE,
        related_name='diploma',
    )
    room_id = models.CharField(max_length=255, blank=True)
    room_alias = models.CharField(max_length=255, blank=True)
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id} | {self.diploma} | {self.school}"


    class Meta:
        ordering = ('school__tag', 'diploma__label',)
        unique_together = ['school', 'diploma']

     
    def create_room(self, school: School, diploma: Diploma):
        if Room.objects.filter(
            school=school,
            diploma=diploma,
            room_id__isnull=False,
            room_alias__isnull=False
        ).exists:
            room = Room.objects.get(
                school=school,
                diploma=diploma
            )
            return {"room_id": room.room_id, "room_alias": room.room_alias}


class ParticipantType(models.Model):
    name = models.CharField(max_length=255, blank=False)
    slug = models.SlugField(null=True)
    label = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return f"{self.name}"


class Participant(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("Django user"),
        verbose_name=_("User")
    )
    type = models.ForeignKey(
        'ParticipantType',
        on_delete=models.CASCADE,
        null=True,
    )
    room = models.ManyToManyField(
        'Room',
        through='ParticipantRoom'
    )

    def __str__(self):
        return f"{self.user}"


class ParticipantRoom(models.Model):
    participant = models.ForeignKey(
        'Participant',
        on_delete=models.CASCADE,
    )
    room = models.ForeignKey(
        'Room',
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(
        default=True,
        help_text=(
            "Is this Room actively used by the Participant?"
        )
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.participant} {self.room} {self.active}"
    
    class Meta:
        unique_together = ['participant', 'room']


class Text(models.Model):
    name = models.CharField(
        max_length=254,
        unique=True,
    )
    label = models.CharField(
        max_length=254,
    )
    description = models.TextField(
        null=True,
        blank=True
    )
    content = models.TextField(
        blank=True,
        null=True,
        help_text = "context: diploma_slug , diploma_label, school_slug, " \
        "school_tag"
    )

    def __str__(self):
        return f"Text = {self.name}"