from django.db import models
import datetime
from users.models import User
from stories.models import Weights

class Entry(models.Model):
    text = models.TextField()
    type = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=datetime.datetime(2020, 10, 14))
    entrygroup_child = models.ForeignKey("EntryGroup", null=True, on_delete=models.DO_NOTHING)
    entry_challenger = models.ForeignKey("Entry", null=True, on_delete=models.DO_NOTHING)

    def to_json(self):
        json = {
            "id": self.id,
            "text": self.text,
            "type": self.type,
            "level": self.level
        }
        if self.entrygroup_child is not None:
            json.update({"child_entrygroup_id": self.entrygroup_child.id})
        if self.entry_challenger is not None:
            json.update({"entry_challenger_id": self.entry_challenger.id})
        return json


class EntryGroup(models.Model):
    root = models.ForeignKey(Entry, related_name="root_entrygroup", on_delete=models.DO_NOTHING)
    main = models.ForeignKey(Entry, related_name="main_entrygroup", on_delete=models.DO_NOTHING)
    level = models.IntegerField(default=1)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    favorite = models.BooleanField(default=False)

    def to_json(self):
        return {
            "id": self.id,
            "root_id": self.root.id,
            "main": self.main.to_json(),
            "level": self.level,
            "favorite": self.favorite
        }


class Groups(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    group = models.ForeignKey(EntryGroup, on_delete=models.CASCADE)


class Goal(models.Model):
    description = models.TextField()
    frequency = models.CharField(max_length=2,
                                 default="D")  # Coded sthing like.. "W" (weekly), "D" (daily), "3D" (3 times a day)
    active = models.BooleanField(default=True)
    favorite = models.BooleanField(default=False)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    entry = models.ForeignKey(Entry, null=True, on_delete=models.CASCADE)

    def to_json(self):
        json = {
            "id": self.id,
            "description": self.description,
            "frequency": self.frequency,
            "active": self.active,
            "favorite": self.favorite
        }
        if self.entry is not None:
            json.update({"entry_id": self.entry.id})
        return json


class Banner(models.Model):
    text = models.TextField()
    weights = models.ForeignKey(Weights, on_delete=models.CASCADE)
