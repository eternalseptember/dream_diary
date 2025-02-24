from django.db import models
from django.utils.timezone import now
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify



class Symbol(models.Model):
    # name = models.CharField(max_length=255, unique=True, verbose_name="symbols")
    name = models.CharField(max_length=255, unique=True, verbose_name="symbols", db_collation="case_insensitive")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Dream(models.Model):
    title = models.CharField(max_length=255)
    created_on = models.DateTimeField(default=now)
    last_modified = models.DateTimeField(auto_now=True)
    recollection = MarkdownxField()
    preoccupation = models.TextField(blank=True)  # real-life preocccupations
    interpretation = MarkdownxField(blank=True)
    symbols = models.ManyToManyField("Symbol", blank=True, through="Symbolism", related_name="dreams")

    # Create properties that returns the markdown.
    @property
    def formatted_recollection(self):
        return markdownify(self.recollection)
    
    @property
    def formatted_preoccupation(self):
        return markdownify(self.preoccupation)

    @property
    def formatted_interpretation(self):
        return markdownify(self.interpretation)

    def __str__(self):
        return self.title


class Symbolism(models.Model):
    symbol = models.ForeignKey("Symbol", verbose_name="symbol", on_delete=models.CASCADE)
    dream = models.ForeignKey("Dream", verbose_name="dream", on_delete=models.CASCADE)
    comment = models.TextField(blank=True)

