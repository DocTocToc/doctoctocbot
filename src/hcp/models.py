from django.db import models

class Taxonomy(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True
    )
    grouping = models.CharField(
        max_length=255,
        unique=False
    )
    classification = models.CharField(
        max_length=255,
        unique=False
    )
    specialization = models.CharField(
        max_length=255,
        unique=False
    )
    definition = models.TextField(
        unique=False
    )
    
    def __str__(self):
        return f"{self.classification} : {self.specialization}"
    
    class Meta:
        ordering = ('grouping', 'classification', 'specialization',)
        verbose_name_plural = "Taxonomy"
        

class HealthCareProvider(models.Model):
    human = models.ForeignKey(
       'moderation.Human',
       on_delete=models.CASCADE,
       unique=True,
    )
    taxonomy = models.ManyToManyField(
        Taxonomy,
        through='HealthCareProviderTaxonomy',
        through_fields=(
            'healthcareprovider',
            'taxonomy'
        ),
        blank=True,
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.human} : {self.taxonomy.all()}"


class HealthCareProviderTaxonomy(models.Model):
    """ HealthCareProvider - Taxonomy through class"""
    healthcareprovider = models.ForeignKey(
        'HealthCareProvider',
        on_delete=models.CASCADE,
    )
    taxonomy = models.ForeignKey(
        'Taxonomy',
        on_delete=models.CASCADE,
    )
    creator = models.ForeignKey(
        'moderation.Human',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    created =  models.DateTimeField(auto_now_add=True)
    updated =  models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"hcp: {self.healthcareprovider} ,"
            f"taxonomy: {self.taxonomy} ,"
            f"creator: {self.creator} ,"
            f"create: {self.created} ,"
            f"update: {self.updated}."
        )


class TaxonomyCategory(models.Model):
    code = models.CharField(
        max_length=10,
        unique=True,
        blank=True,
        null=True,
    )
    grouping = models.CharField(
        max_length=255,
        unique=False,
        blank=True,
    )
    classification = models.CharField(
        max_length=255,
        unique=False,
        blank=True,
    )
    specialization = models.CharField(
        max_length=255,
        unique=False,
        blank=True,
    )
    category = models.ForeignKey(
        'moderation.Category',
        on_delete=models.PROTECT,
    )
    community = models.ForeignKey(
        'community.Community',
        on_delete=models.PROTECT,
    )

    def __str__(self):
        return f"{self.code} {self.grouping} {self.classification} " \
               f"{self.specialization} | {self.category}"