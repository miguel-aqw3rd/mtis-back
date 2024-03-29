import hashlib
import json
from datetime import datetime, timezone
import bcrypt
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import *


def save_password(password):
    return bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt()).decode('utf8')


def check_password(user, password):
    encrypted = user.encrypted_password
    return bcrypt.checkpw(password.encode('utf-8'), encrypted.encode('utf-8'))


@csrf_exempt
def login(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        username = data.get('username', None)
        password = data.get('password', None)

        if not username or not password:
            return JsonResponse({"Error": "Username or password missing"}, status=400)
        if not User.objects.filter(username=username).exists():
            return JsonResponse({"Error": "User does not exist"}, status=404)

        user = User.objects.get(username=username)
        if not check_password(user, password):
            return JsonResponse({"Error": "Incorrect password"}, status=401)

        token = new_token(username)
        user.token = token
        user.save()
        return JsonResponse({"Message": "Login Successful", "token": token}, status=201)
    else:
        return JsonResponse({"Error": "Only put"}, status=405)


@csrf_exempt
def signup(request):
    if request.method == "POST":
        data = json.loads(request.body)
        username = data.get('username', None)
        email = data.get('email', None)
        password = data.get('password', None)

        if not username or not password:
            return JsonResponse({"Error": "Username or password missing"}, status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({"Error": "Username already in use"}, status=409)

        password = save_password(password)
        user = User(username=username, encrypted_password=password)
        token = new_token(username)
        user.token = token
        if email:
            user.email = email
        user.save()
        return JsonResponse({"Message": "User created", "token": token}, status=201)
    else:
        return JsonResponse({"Error": "Only post"}, status=405)


@csrf_exempt
def logout(request):
    if request.method == "PUT":
        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)

        user.token = new_token(user.username + "a pink mockingbird")
        user.save()
        return JsonResponse({"Message": "Logout Successful"}, status=200)
    else:
        return JsonResponse({"Error": "Only put"}, status=405)


def new_token(username):
    now = str(datetime.datetime.now())
    hash = hashlib.sha256()
    hash.update((now + username).encode('utf-8'))
    return hash.hexdigest()[0:30]


@csrf_exempt
def change_name(request):
    if request.method == "PUT":
        data = json.loads(request.body)
        name = data.get('name', None)
        if not name:
            return JsonResponse({"Error": "Name missing"}, status=400)

        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)

        user.name = name
        user.save()
        return JsonResponse({"Message": "Name updated successfully"}, status=200)
    else:
        return JsonResponse({"Error": "Only put"}, status=405)


# Returns the user of the token given in the header of the request
def get_user(request):  # Throw errors as needed
    auth_token = request.headers.get('auth-token', None)
    if not auth_token:
        return -1
    try:
        user = User.objects.get(token=auth_token)
    except User.DoesNotExist:
        return -1

    return user


""" The following functions parse recursively a json to save the uploaded story to the database
The json is expected in this format:

{
"title": ,
"character": ,
"story":{
	"text": ,
	"a": ,
	"b": ,
	"nextQa":{
			"text": ,
			"a": ,
			"b": ,
			"nextQa": ,
			"nextQb": ,
			},
	"nextQb":{
			"text": ,
			"a": ,
			"b": ,
			"nextQa": ,
			"nextQb": ,
			},

}

}

The fields nextQa and nextQb are optional
"""


@csrf_exempt
def save_question(json):
    text = json.get("text", None)
    a = json.get("a", None)
    b = json.get("b", None)
    nextQa = json.get("nextQa", None)
    nextQb = json.get("nextQb", None)
    if not text or not a or not b:
        return -1

    question = Question(text=text, a=a, b=b)
    if nextQa:
        id = save_question(nextQa)
        if id != -1:
            question.nextQa = id
    if nextQb:
        id = save_question(nextQb)
        if id != -1:
            question.nextQb = id
    question.save()
    return question.id


@csrf_exempt
def new_story(request):
    json_body = json.loads(request.body)
    title = json_body.get("title", None)
    character = json_body.get("character", None)
    story_json = json_body.get("story", None)
    if not title or not character or not story_json:
        return JsonResponse({"Error": "Invalid json body"}, status=400)

    # Starts recursively saving questions, starting with the first
    chapter0_id = save_question(story_json)
    chapter0 = Question.objects.get(id=chapter0_id)

    story = Story(title=title, character=character, chapter0=chapter0)
    story.save()
    return JsonResponse({"Message": "Story saved successfully"}, status=200)


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
        X = request.GET.get("answer", None)
        if not X:
            return JsonResponse({"Error": "Invalid answer"}, status=400)
        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return JsonResponse({"Error": "Story chapter does not exist"}, status=404)

        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)
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
        return JsonResponse({"Message": "Answer saved"}, status=200)
    else:
        return JsonResponse({"Error": "Only post"}, status=405)


def entries(request):
    if request.method == "GET":
        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)

        entries = Entry.objects.filter(user=user).order_by("datetime")
        entries_data = [entry.to_json() for entry in entries]
        return JsonResponse({"entries": entries_data}, status=200)
    else:
        return JsonResponse({"Error": "Only get"}, status=405)


@csrf_exempt
def get_entry(request, entry_id):  # also delete
    try:
        entry = Entry.objects.get(id=entry_id)
    except Entry.DoesNotExist:
        return JsonResponse({"Error": "Entry does not exist"}, status=404)

    user = get_user(request)
    if user == -1:
        return JsonResponse({"Error": "Invalid or missing token"}, status=401)
    if user != entry.user:
        return JsonResponse({"Error": "You don't have permission to read other users' entries"}, status=401)

    if request.method == "GET":
        data = entry.to_json()
        return JsonResponse(data, status=200)
    elif request.method == "DELETE":
        entry.delete()
        return JsonResponse({"Message": "Entry deleted successfully"}, status=200)
    else:
        return JsonResponse({"Error": "Only get or delete"}, status=405)


@csrf_exempt
def get_entrygroup(request, entrygroup_id):
    try:
        entrygroup = EntryGroup.objects.get(id=entrygroup_id)
    except EntryGroup.DoesNotExist:
        return JsonResponse({"Error": "Entry Group does not exist"}, status=404)

    user = get_user(request)
    if user == -1:
        return JsonResponse({"Error": "Invalid or missing token"}, status=401)
    if user != entrygroup.user:
        return JsonResponse({"Error": "You don't have permission to read other users' entries"}, status=401)

    if request.method == "GET":
        entries = [group.entry for group in Groups.objects.filter(group=entrygroup)]
        entries_array = [entry.to_json() for entry in entries if entry != entrygroup.main]

        return JsonResponse({
            "id": entrygroup.id,
            "root": entrygroup.root.to_json(),
            "main": entrygroup.main.to_json(),
            "level": entrygroup.level,
            "favorite": entrygroup.favorite,
            "entries": entries_array
        }, status=200)
    elif request.method == "DELETE":
        entrygroup.delete()
        return JsonResponse({"Message": "Entry Group deleted successfully"})
    else:
        return JsonResponse({"Error": "Only get"}, status=405)


@csrf_exempt
def new_entry(request):
    if request.method == "POST":
        # Optional: associated entry group
        entrygroup_id = request.GET.get("entrygroup", None)

        json_body = json.loads(request.body)
        text = json_body.get("text", None)
        type = json_body.get("type", None)
        level = json_body.get("level", None)
        if text is None or type is None or level is None:
            return JsonResponse({"Error": "Invalid json body"}, status=400)

        try:
            type = int(type)
            level = int(level)
        except ValueError:
            return JsonResponse({"Error": "Invalid json body. Type and Level must be numbers"}, status=400)
        if type < 0 or level < 0:
            return JsonResponse({"Error": "Invalid json body. Type and Level must be non-negative numbers"}, status=400)

        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)
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
        entry.datetime = datetime.datetime.now()
        if entrygroup_id:
            entry.level = entrygroup.level  # The level of entry is default 0, or the same as the level of its entrygroup
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
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)
        if user != entry.user:
            return JsonResponse({"Error": "You don't have permission to read other users' entries"}, status=401)

        if entry.entrygroup_child is not None:
            return JsonResponse({"Error": "There is already an entry group associated with this entry"}, status=409)

        entrygroup = EntryGroup(root=entry, main=entry, user=user)
        entrygroup.level = entry.level + 1  # The Entry Group is a level higher than the root entry
        entrygroup.save()
        group = Groups(entry=entry, group=entrygroup)  # Save root entry as member of the entry group
        group.save()
        entry.entrygroup_child = entrygroup  # Save the entrygroup as the child of this entry
        entry.save()

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
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)
        if user != entrygroup.user or user != entry.user:
            return JsonResponse({"Error": "You don't have permission to modify other users' entry groups"}, status=401)

        entrygroup.main = entry
        entrygroup.save()
        return JsonResponse({"Message": "Entry Group updated"}, status=200)
    else:
        return JsonResponse({"Error": "Only put"}, status=405)


@csrf_exempt
def favorite_entrygroup(request, entrygroup_id):
    if request.method == "PUT":
        try:
            entrygroup = EntryGroup.objects.get(id=entrygroup_id)
        except EntryGroup.DoesNotExist:
            return JsonResponse({"Error": "Entry Group does not exist"}, status=404)

        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)
        if user != entrygroup.user:
            return JsonResponse({"Error": "You don't have permission to modify other users' entry groups"}, status=401)

        entrygroup.favorite = not entrygroup.favorite  # Switches the "Favorite" boolean
        entrygroup.save()
        return JsonResponse({"Message": "Entry Group updated"}, status=200)
    else:
        return JsonResponse({"Error": "Only put"}, status=405)


def entrygroups(request):
    if request.method == "GET":
        level = request.GET.get("level", None)  # Optional filters per entry group level
        favorites = request.GET.get("favorites", None)
        parent_entrygroup_id = request.GET.get("entrygroup", None)

        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)

        if favorites is not None:
            if favorites == "True" or favorites == "true":
                favorites = True
            elif favorites == "False" or favorites == "false":
                favorites = False
            else:
                return JsonResponse({"Error": "Favorites query parameter must be boolean"}, status=400)

        entrygroups = EntryGroup.objects.filter(user=user).order_by("-favorite")
        if level:
            try:
                level = int(level)
            except ValueError:
                return JsonResponse({"Error": "Level must be an integer number"}, status=400)

            entrygroups = entrygroups.filter(level=level)
        if favorites is not None:
            entrygroups = entrygroups.filter(favorite=favorites)
        if parent_entrygroup_id:
            try:
                parent_entrygroup_id = int(parent_entrygroup_id)
            except ValueError:
                return JsonResponse({"Error": "Level must be an integer number"}, status=400)
            try:
                parent_entrygroup = EntryGroup.objects.get(id=parent_entrygroup_id)
            except EntryGroup.DoesNotExist:
                return JsonResponse({"Error": "EntryGroup does not exist"}, status=404)
            entries = [group.entry for group in Groups.objects.filter(group=parent_entrygroup)]  # List of ALL entries of the entrygroup
            child_entrygroups = [entry.entrygroup_child for entry in entries if entry != parent_entrygroup.root]
            # Intersection: of the filtered entrygroups, which are children of the entries of the entrygroup (not counting root entry)?
            # Flexible but not very efficient... To be improved
            entrygroups = set(entrygroups).intersection(set(child_entrygroups))

        entrygroups_array = [group.to_json() for group in entrygroups]
        return JsonResponse({"entrygroups": entrygroups_array}, status=200)
    else:
        return JsonResponse({"Error": "Only get"}, status=405)


@csrf_exempt
def new_challenge(request, entry_id):
    if request.method == "POST":
        # Check the existence of the given entry and the credentials
        allowed = True
        entries_ids = request.GET.get("to", None)
        if not entries_ids:
            return JsonResponse({"Error": "Missing query parameter: entries to challenge"}, status=400)
        try:
            # Entry ids come separated by plus signs in the query
            entries_ids = [int(id) for id in entries_ids.split(" ")]
        except ValueError:
            return JsonResponse({"Error": "Formating error in query parameter"}, status=400)
        try:
            # Check if all the corresponding entries exist
            entry_challenge = Entry.objects.get(id=entry_id)
            entries = [Entry.objects.get(id=entry_id) for entry_id in entries_ids]
        except Entry.DoesNotExist:
            return JsonResponse({"Error": "Entry does not exist"}, status=404)

        # Check permission
        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)
        if user != entry_challenge.user:
            allowed = False
        for entry in entries:
            if user != entry.user:
                allowed = False
        if not allowed:
            return JsonResponse(
                {"Error": "You don't have permission to read other users' entries or update their challenges"},
                status=401)

        # Save
        for e in entries:
            e.entry_challenger = entry_challenge
            e.save()
        return JsonResponse({"Message": "Challenges updated successfully"}, status=200)
    else:
        return JsonResponse({"Error": "Only post"}, status=405)


@csrf_exempt
def new_goal(request):
    if request.method == "POST":
        # Optional: associated entry to the goal
        entry_id = request.GET.get("entry", None)

        json_body = json.loads(request.body)
        description = json_body.get("description", None)
        frequency = json_body.get("frequency", "D")
        active = json_body.get("active", True)
        favorite = json_body.get("favorite", False)
        if not description:
            return JsonResponse({"Error": "Invalid json body"}, status=400)
        if not isinstance(active, bool):
            return JsonResponse({"Error": "Invalid json body. Field 'active' must be boolean"}, status=400)
        if not isinstance(favorite, bool):
            return JsonResponse({"Error": "Invalid json body. Field 'favorite' must be boolean"}, status=400)

        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)
        if entry_id:
            try:
                entry = Entry.objects.get(id=entry_id)
            except Entry.DoesNotExist:
                return JsonResponse({"Error": "Entry does not exist"}, status=404)
            if user != entry.user:
                return JsonResponse({"Error": "You don't have permission to read other users' entries"}, status=401)

        # Save the goal and its associations
        goal = Goal(description=description, frequency=frequency, active=active, user=user)
        if favorite:
            goal.favorite = favorite
        if entry_id:
            goal.entry = entry
        goal.save()
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
    if user == -1:
        return JsonResponse({"Error": "Invalid or missing token"}, status=401)
    if user != goal.user:
        return JsonResponse({"Error": "You don't have permission to read or modify other users' goals"}, status=401)

    if request.method == "GET":
        return JsonResponse(goal.to_json(), status=200)
    elif request.method == "PUT":
        json_body = json.loads(request.body)
        description = json_body.get("description", None)
        frequency = json_body.get("frequency", None)
        active = json_body.get("active", None)
        favorite = json_body.get("favorite", None)
        if active is not None:
            if not isinstance(active, bool):
                return JsonResponse({"Error": "Invalid json body. Field 'active' must be boolean"}, status=400)
        if favorite is not None:
            if not isinstance(favorite, bool):
                return JsonResponse({"Error": "Invalid json body. Field 'favorite' must be boolean"}, status=400)

        # Update the goal
        if description:
            goal.description = description
        if frequency:
            goal.frequency = frequency
        if active is not None:
            goal.active = active
        if favorite is not None:
            goal.favorite = favorite

        goal.save()
        return JsonResponse({"Message": "Goal updated"}, status=200)
    elif request.method == "DELETE":
        goal.delete()
        return JsonResponse({"Message": "Goal deleted"}, status=200)
    else:
        return JsonResponse({"Error": "Only get, put or delete"}, status=405)


def goals(request):
    if request.method == "GET":
        active = request.GET.get("active", None)
        entry_id = request.GET.get("entry", None)
        favorite = request.GET.get("favorite", None)
        if active is not None:
            if active == "True" or active == "true":
                active = True
            elif active == "False" or active == "false":
                active = False
            else:
                return JsonResponse({"Error": "Invalid query parameter. Active must be boolean"}, status=400)
        if favorite is not None:
            if favorite == "True" or favorite == "true":
                favorite = True
            elif favorite == "False" or favorite == "false":
                favorite = False
            else:
                return JsonResponse({"Error": "Invalid query parameter. Favorite must be boolean"}, status=400)

        user = get_user(request)
        if user == -1:
            return JsonResponse({"Error": "Invalid or missing token"}, status=401)

        if entry_id:
            try:
                entry_id = int(entry_id)
            except ValueError:
                return JsonResponse({"Error": "Invalid query parameter. Entry must be a number"}, status=400)
            try:
                entry = Entry.objects.get(id=entry_id)
            except Entry.DoesNotExist:
                return JsonResponse({"Error": "Entry does not exist"}, status=404)
            if user != entry.user:
                return JsonResponse({"Error": "You don't have permission to read or modify other users' entries"},
                                    status=401)

        if entry_id:
            goals = Goal.objects.filter(user=user, entry=entry)
        else:
            goals = Goal.objects.filter(user=user)
        if active is not None:
            goals = goals.filter(active=active)
        if favorite is not None:
            goals = goals.filter(favorite=favorite)

        goals = [goal for goal in goals]
        goals_data = [goal.to_json() for goal in goals]
        return JsonResponse({"goals": goals_data}, status=200)
    else:
        return JsonResponse({"Error": "Only get"}, status=405)
