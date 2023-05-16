from database.database import db
from peewee import *
from datetime import datetime
from pytz import timezone


class BaseModel(Model):
    _time = datetime.now(timezone('Asia/Kolkata')).strftime("%d-%m-%Y, %H:%M:%S")
    created_at = DateTimeField(default=_time)
    modified_at = DateTimeField()

    def save(self, *args, **kwargs):
        self.modified_at = self._time
        return super().save(*args, **kwargs)

    class Meta:
        database = db
