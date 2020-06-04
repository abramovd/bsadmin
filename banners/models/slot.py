from django.db import models

from banners.models.page import Page
from helpers.models import BaseModel


class Slot(BaseModel):
    name = models.CharField(unique=True, max_length=256)
    description = models.TextField()
    page = models.ForeignKey(Page, on_delete=models.PROTECT)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'page': self.page.to_dict(),
        }

    class Meta:
        ordering = ('-create_time', )
