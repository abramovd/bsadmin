import uuid

from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)

    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
