from django.db import models

class User(models.Model):
    username = models.CharField(max_length=50)

class Weights(models.Model):
    Xfactor = models.FloatField(default=0.0)
    Yfactor = models.FloatField(default=0.0)
    Zfactor = models.FloatField(default=0.0)

class Question(models.Model):
    text = models.TextField()
    a = models.TextField()
    b = models.TextField()
    nextQa = models.IntegerField(null=True) #Represents the id of the chapter/question that follows the choice of A
    nextQb = models.IntegerField(null=True) #Represents the id of the chapter/question that follows the choice of B
    weights = models.ForeignKey(Weights, on_delete=models.CASCADE)

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    count = models.IntegerField(default=0)
    netAB = models.IntegerField(default=0)

class Story(models.Model):
    chapter0 = models.ForeignKey(Question, on_delete=models.CASCADE)



class Entry(models.Model):
    text = models.TextField()
    type = models.IntegerField(default=0)
    level = models.IntegerField(default=0)

class Challenge(models.Model):
    challenger = models.ForeignKey(Entry, related_name="challenger_challenge", on_delete=models.CASCADE)
    in_question = models.ForeignKey(Entry, related_name="in_question_challenge", on_delete=models.CASCADE)

class EntryGroup(models.Model):
    root = models.ForeignKey(Entry, related_name="root_entrygroup", on_delete=models.DO_NOTHING)
    main = models.ForeignKey(Entry, related_name="main_entrygroup", on_delete=models.DO_NOTHING)
    level = models.IntegerField(default=1)

class Groups(models.Model):
    entry = models.ForeignKey(Entry, on_delete=models.CASCADE)
    group = models.ForeignKey(EntryGroup, on_delete=models.CASCADE)

