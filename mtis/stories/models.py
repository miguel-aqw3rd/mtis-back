from django.db import models
from users.models import User

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
    weights = models.ForeignKey(Weights, null=True, on_delete=models.CASCADE)

    def to_json(self):
        return {
            "id": self.id,
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
    title = models.CharField(max_length=100, default="F*ck Mondays")
    character = models.CharField(max_length=50, default="Garfield")
    author = models.CharField(max_length=50, default="Homer")
    category = models.CharField(max_length=50, default="Normal")
    chapter0 = models.ForeignKey(Question, on_delete=models.CASCADE)
    image = models.ImageField()

    def to_json(self):
        return {
            "id": self.id,
            "title": self.title,
            "character": self.character,
            "author": self.author,
            "chapter0": self.chapter0,
        }


