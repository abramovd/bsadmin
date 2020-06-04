from django.db import models

from helpers.models import BaseModel


class Page(BaseModel):
    name = models.CharField(unique=True, max_length=256)
    description = models.TextField()

    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name,
            'description': self.description
        }

    class Meta:
        ordering = ('-create_time', )
