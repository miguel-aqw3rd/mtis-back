from django.db import models
import datetime


class User(models.Model):
    username = models.CharField(max_length=50, unique=True)
    email = models.CharField(max_length=150, null=True)
    encrypted_password = models.CharField(max_length=256, default="1234")
    token = models.CharField(max_length=30, default="1234")
    name = models.CharField(max_length=75, default="Beautiful Person")


class Weights(models.Model):
    Xfactor = models.FloatField(default=0.0)
    Yfactor = models.FloatField(default=0.0)
    Zfactor = models.FloatField(default=0.0)


class Question(models.Model):
    text = models.TextField()
    a = models.TextField()
    b = models.TextField()
    nextQa = models.IntegerField(null=True)  # Represents the id of the chapter/question that follows the choice of A
    nextQb = models.IntegerField(null=True)  # Represents the id of the chapter/question that follows the choice of B
    weights = models.ForeignKey(Weights, on_delete=models.CASCADE)

    def to_json(self):
        return {
            "text": self.text,
            "a": self.a,
            "b": self.b,
            "nextQa": self.nextQa,
            "nextQb": self.nextQb
        }


class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    netAB = models.IntegerField(default=0)


class Story(models.Model):
    title = models.CharField(max_length=100, default="Peaky Blinders")
    character = models.CharField(max_length=50, default="Tommy")
    chapter0 = models.ForeignKey(Question, on_delete=models.CASCADE)


class Entry(models.Model):
    text = models.TextField()
    type = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=datetime.datetime.now())

    def to_json(self):
        return {
            "id": self.id,
            "text": self.text,
            "type": self.type,
            "level": self.level
        }


class Challenge(models.Model):
    challenger = models.ForeignKey(Entry, related_name="challenger_challenge", on_delete=models.CASCADE)
    in_question = models.ForeignKey(Entry, related_name="in_question_challenge", on_delete=models.CASCADE)


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
            "level": self.level
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
        return {
            "id": self.id,
            "description": self.description,
            "frequency": self.frequency,
            "active": self.active,
            "favorite": self.favorite,
            "entry_id": self.entry.id
        }


class Banner(models.Model):
    text = models.TextField()
    weights = models.ForeignKey(Weights, on_delete=models.CASCADE)
