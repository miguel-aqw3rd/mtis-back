import hashlib
import json
from datetime import datetime, timezone
import bcrypt
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from .models import *


# Returns the user of the token given in the header of the request
def get_user(request):  # Throw errors as needed
    return User.objects.get(id=1)  # Function is a dummy for now


@csrf_exempt
def new_story(request):
    pass


def question(request, question_id):
    if request.method == "GET":
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({"Error": "Story chapter does not exist"}, status=404)

        data = question.to_json()
        return JsonResponse(data, status=200)


@csrf_exempt
def answer(request, question_id):
    if request.method == "POST":
        X = request.POST.get("answer", None)
        if not X:
            return JsonResponse({"Error": "Invalid answer"}, status=400)
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({"Error": "Story chapter does not exist"}, status=404)

        user = get_user(request)
        try:
            answer = Answer.objects.get(user=user, question=question)
        except Answer.DoesNotExist:
            answer = Answer()
            answer.question = question
            answer.user = user

        if X == "A" or X == "a":
            answer.count += 1
            answer.netAB += 1
        elif X == "B" or X == "b":
            answer.count += 1
            answer.netAB -= 1
        else:
            return JsonResponse({"Error": "Invalid answer"}, status=400)

        answer.save()
        return JsonResponse({"Message": "Instance created"}, status=200)
    else:
        return JsonResponse({"Error": "Only post"}, status=405)


def get_entry(request, entry_id):  # also delete
    if request.method == "GET":
        try:
            entry = Entry.objects.get(id=entry_id)
        except Entry.DoesNotExist:
            return JsonResponse({"Error": "Entry does not exist"}, status=404)

        user = get_user(request)
        if user != entry.user:
            return JsonResponse({"Error": "You don't have permission to read other users' entries"}, status=401)

        data = entry.to_json()
        return JsonResponse(data, status=200)
    elif request.method == "DELETE":
        try:
            entry = Entry.objects.get(id=entry_id)
        except Entry.DoesNotExist:
            return JsonResponse({"Error": "Entry does not exist"}, status=404)

        user = get_user(request)
        if user != entry.user:
            return JsonResponse({"Error": "You don't have permission to delete other users' entries"}, status=401)

        entry.delete()
        return JsonResponse({"Message": "Entry deleted successfully"}, status=200)
    else:
        return JsonResponse({"Error": "Only get or delete"}, status=405)



def get_entrygroup(request, entrygroup_id):
    if request.method == "GET":
        try:
            entrygroup = EntryGroup.objects.get(id=entrygroup_id)
        except EntryGroup.DoesNotExist:
            return JsonResponse({"Error": "Entry Group does not exist"}, status=404)

        user = get_user(request)
        if user != entrygroup.user:
            return JsonResponse({"Error": "You don't have permission to read other users' entries"}, status=401)

        entries = [group.entry for group in Groups.objects.filter(group=entrygroup)]
        entries_array = [entry.to_json() for entry in entries]

        return JsonResponse({
            "id": entrygroup.id,
            "root": entrygroup.root.to_json(),  # Esto a lo mejor falla
            "main": entrygroup.main.to_json(),  # Esto a lo mejor falla
            "level": entrygroup.level,
            "entries": entries_array
        }, status=200)
    else:
        return JsonResponse({"Error": "Only get"}, status=405)


@csrf_exempt
def new_entry(request):
    if request.method == "POST":
        # Optional: associated entry group
        entrygroup_id = request.POST.get("entrygroup", None)

        json_body = json.loads(request.body)
        text = json_body.get("text", None)
        type = json_body.get("type", None)
        level = json_body.get("level", None)
        if not text or not type or not level:
            return JsonResponse({"Error": "Invalid json body"}, status=400)

        try:
            type = int(type)
            level = int(level)
        except ValueError:
            return JsonResponse({"Error": "Invalid json body. Type and Level must be numbers"}, status=400)
        if type < 0 or level < 0:
            return JsonResponse({"Error": "Invalid json body. Type and Level must be non-negative numbers"}, status=400)

        user = get_user(request)
        #############################
        if entrygroup_id:
            try:
                entrygroup = EntryGroup.objects.get(id=entrygroup_id)
            except EntryGroup.DoesNotExist:
                return JsonResponse({"Error": "Entry Group does not exist"}, status=404)
            if user != entrygroup.user:
                return JsonResponse({"Error": "You don't have permission to touch other users' entries"}, status=401)
        #################################
        entry = Entry(text=text, type=type, level=level, user=user)
        entry.save()
        if entrygroup_id:  # If a valid EntryGroup id is sent as a query parameter, new entry is associated with that Entry Group
            group = Groups(entry=entry, group=entrygroup)
            group.save()

        return JsonResponse({"Message": "Entry saved"}, status=200)

    else:
        return JsonResponse({"Error": "Only post"}, status=405)


@csrf_exempt
def new_entrygroup(request, entry_id):
    if request.method == "POST":
        # Check the existence of the given entry and the credentials
        try:
            entry = Entry.objects.get(id=entry_id)
        except Entry.DoesNotExist:
            return JsonResponse({"Error": "Entry does not exist"}, status=404)

        user = get_user(request)
        if user != entry.user:
            return JsonResponse({"Error": "You don't have permission to read other users' entries"}, status=401)

        entrygroup = EntryGroup(root=entry, main=entry, user=user)
        entrygroup.level = entry.level + 1  # The Entry Group is a level higher than the root entry
        entrygroup.save()
        return JsonResponse({"Message": "EntryGroup created"}, status=200)

    else:
        return JsonResponse({"Error": "Only post"}, status=405)


@csrf_exempt
def change_mainentry_of_entrygroup(request, entrygroup_id, entry_id):
    if request.method == "PUT":
        try:
            entrygroup = EntryGroup.objects.get(id=entrygroup_id)
        except EntryGroup.DoesNotExist:
            return JsonResponse({"Error": "Entry Group does not exist"}, status=404)
        try:
            entry = Entry.objects.get(id=entry_id)
        except Entry.DoesNotExist:
            return JsonResponse({"Error": "Entry does not exist"}, status=404)

        user = get_user(request)
        if user != entrygroup.user or user != entry.user:
            return JsonResponse({"Error": "You don't have permission to modify other users' entry groups"}, status=401)

        entrygroup.main = entry
        entrygroup.save()
        return JsonResponse({"Message": "Entry Group updated"}, status=200)
    else:
        return JsonResponse({"Error": "Only put"}, status=405)


def entrygroups(request):
    if request.method == "GET":
        level = request.GET.get("level", None)  # Optional filters per entry group level
        user = get_user(request)

        if level:
            try:
                level=int(level)
            except ValueError:
                return JsonResponse({"Error": "Level must be an integer number"}, status=400)

            entrygroups = EntryGroup.objects.filter(user=user, level=level)
        else:
            entrygroups = EntryGroup.objects.filter(user=user)

        entrygroups_array = [group.to_json() for group in entrygroups]
        return JsonResponse({"entrygroups": entrygroups_array}, status=200)
    else:
        return JsonResponse({"Error": "Only get"}, status=405)


@csrf_exempt
def new_challenge(request, entry_id):
    if request.method == "POST":
        # Check the existence of the given entry and the credentials
        allowed = True
        entries_ids = request.POST.get("to", None)
        if not entries_ids:
            return JsonResponse({"Error": "Missing query parameter: entries to challenge"}, status=400)
        try:
            # Entry ids come separated by plus signs in the query
            entries_ids = [int(id) for id in entries_ids.split("+")]
        except ValueError:
            return JsonResponse({"Error": "Formating error in query parameter"}, status=400)
        try:
            # Check if all the corresponding entries exist
            entry = Entry.objects.get(id=entry_id)
            entries = [Entry.objects.get(id=entry_id) for entry_id in entries_ids]
        except Entry.DoesNotExist:
            return JsonResponse({"Error": "Entry does not exist"}, status=404)

        # Check permission
        user = get_user(request)
        if user != entry.user:
            allowed = False
        for entry in entries:
            if user != entry.user:
                allowed = False
        if not allowed:
            return JsonResponse({"Error": "You don't have permission to read other users' entries or update their challenges"}, status=401)

        # Save
        for e in entries:
            challenge = Challenge(challenger=entry, in_question=e)
            challenge.save()
        return JsonResponse({"Message": "Challenges updated successfully"}, status=200)
    else:
        return JsonResponse({"Error": "Only post"}, status=405)


@csrf_exempt
def new_goal(request):
    if request.method == "POST":
        # Optional: associated entry to the goal
        entry_id = request.POST.get("entry", None)

        json_body = json.loads(request.body)
        description = json_body.get("description", None)
        frequency = json_body.get("frequency", "D")
        active = json_body.get("active", True)
        if not description:
            return JsonResponse({"Error": "Invalid json body"}, status=400)
        if active:
            try:
                active = bool(active)
            except ValueError:
                return JsonResponse({"Error": "Invalid json body"}, status=400)

        user = get_user(request)
        if entry_id:
            try:
                entry = Entry.objects.get(id=entry_id)
            except Entry.DoesNotExist:
                return JsonResponse({"Error": "Entry does not exist"}, status=404)
            if user != entry.user:
                return JsonResponse({"Error": "You don't have permission to read other users' entries"}, status=401)

        # Save the goal and its associations
        goal = Goal(description=description, frequency=frequency, active=active)
        goal.save()
        rel = RelEGU(goal=goal, user=user)
        if entry_id:
            rel.entry = entry
        rel.save()
        return JsonResponse({"Message": "Goal saved"}, status=200)
    else:
        return JsonResponse({"Error": "Only post or put"}, status=405)


@csrf_exempt
def goal(request, goal_id):
    try:
        goal = Goal.objects.get(id=goal_id)
    except Goal.DoesNotExist:
        return JsonResponse({"Error": "Goal does not exist"}, status=404)
    user = get_user(request)
    rel = RelEGU.objects.get(goal=goal)
    if user != rel.user:
        return JsonResponse({"Error": "You don't have permission to read or modify other users' goals"}, status=401)

    if request.method == "GET":
        return JsonResponse(goal.to_json(), status=200)
    elif request.method == "PUT":
        json_body = json.loads(request.body)
        description = json_body.get("description", None)
        frequency = json_body.get("frequency", None)
        active = json_body.get("active", None)
        if active:
            try:
                active = bool(active)
            except ValueError:
                return JsonResponse({"Error": "Invalid json body"}, status=400)

        # Update the goal
        if description:
            goal.description = description
        if frequency:
            goal.frequency = frequency
        if active is not None:
            goal.active = active

        goal.save()
    elif request.method == "DELETE":
        goal.delete()
        return JsonResponse({"Message": "Goal deleted"}, status=200)
    else:
        return JsonResponse({"Error": "Only get, put or delete"}, status=405)


def goals(request):
    if request.method == "GET":
        user = get_user(request)
        rels = RelEGU.objects.filter(user=user)
        goals = [rel.goal for rel in rels]
        goals_data = [goal.to_json() for goal in goals]
        return JsonResponse({"goals": goals_data}, status=200)
    else:
        return JsonResponse({"Error": "Only get"}, status=405)


def active_goals(request):
    if request.method == "GET":
        user = get_user(request)
        rels = RelEGU.objects.filter(user=user)
        goals = [rel.goal for rel in rels if rel.goal.active]
        goals_data = [goal.to_json() for goal in goals]
        return JsonResponse({"goals": goals_data}, status=200)
    else:
        return JsonResponse({"Error": "Only get"}, status=405)


def entry_goals(request, entry_id):
    if request.method == "GET":
        try:
            entry = Entry.objects.get(id=entry_id)
        except Entry.DoesNotExist:
            return JsonResponse({"Error": "Entry does not exist"}, status=404)
        user = get_user(request)
        if user != entry.user:
            return JsonResponse({"Error": "You don't have permission to read or modify other users' entries"}, status=401)

        rels = RelEGU.objects.filter(user=user, entry=entry)
        goals = [rel.goal for rel in rels]
        goals_data = [goal.to_json() for goal in goals]
        return JsonResponse({"goals": goals_data}, status=200)
    else:
        return JsonResponse({"Error": "Only get"}, status=405)