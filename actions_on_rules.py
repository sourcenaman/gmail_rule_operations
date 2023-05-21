import requests
from auth import get_creds
from sqlalchemy import *
from database import *
import json
from datetime import datetime, timedelta

with open("rules.json", 'r') as rules:
    rules = json.load(rules)

session = Session(bind=engine)

mapping_predicate = {
    "contains": "ilike",
    "does not contain": "notlike",
    "equals": "==",
    "not equals": "!=",
    "less than": ">",
    "greater than": "<"
}

mapping_labels = {
    "important": "IMPORTANT",
    "inbox": "INBOX",
    "spam": "SPAM",
    "trash": "TRASH",
    "unread": "UNREAD",
    "read": "UNREAD",
    "starred": "STARRED",
    "personal": "CATEGORY_PERSONAL",
    "social": "CATEGORY_SOCIAL",
    "promotions": "CATEGORY_PROMOTIONS",
    "updates": "CATEGORY_UPDATES",
    "forums": "CATEGORY_FORUMS"
}


def modify_mail(ids, addLabel, removeLabel):
    print(len(ids))
    creds = json.loads(get_creds().to_json())
    headers = {
        "Authorization": f'Bearer {creds["token"]}'
    }
    url = f'https://gmail.googleapis.com/gmail/v1/users/me/messages/batchModify'
    data = {
        "ids": ids,
        "addLabelIds": addLabel,
        "removeLabelIds": removeLabel
    }

    resp = requests.post(url=url, data=data, headers=headers)
    print(resp.status_code)

def actions(mail_ids, actions):
    add_labels = []
    remove_labels = []
    ids = []
    for action in actions:
        if (action["action"] == "move"):
            add_labels.append(mapping_labels[action["value"]])
        elif (action["action"] == "mark as"):
            if (action["value"] == "read"):
                remove_labels.append(mapping_labels[action["value"]])
            else:
                add_labels.append(mapping_labels[action["value"]])    
    while True:
        ids.append(mail_ids.pop())
        if (len(ids) == 1000):
            modify_mail(ids, add_labels, remove_labels)
            ids = []
        if (len(mail_ids) == 0):
            modify_mail(ids, add_labels, remove_labels)
            break

def get_filters(rule):
    filters = []
    conditions = rule["conditions"]
    for condition in conditions:
        if (condition["predicate"] in ["contains", "does not contain"]):
            filters.append(f'Emails.{condition["field"]}.{mapping_predicate[condition["predicate"]]}("%{condition["value"]}%")')
        elif (condition["field"] == "received_date"):
            current_time = datetime.now()
            delta = timedelta(days=condition["value"]) if condition["type"] == "day" else timedelta(days=30*condition["value"])
            future_date = current_time - delta
            filters.append(f'Emails.{condition["field"]}{mapping_predicate[condition["predicate"]]}"{future_date}"')
        else:
            filters.append(f'Emails.{condition["field"]}{mapping_predicate[condition["predicate"]]}"{condition["value"]}"')
    return filters

def any(rules):
    for rule in rules:
        filters = get_filters(rule)
        result = session.query(Emails.id)
        temp = result.filter(eval(filters[0]))
        for filter in filters:
            result1 = result.filter(eval(filter))
            temp = temp.union(result1)
        mail_ids = [id[0] for id in temp.all()]
        actions(mail_ids, rule["actions"])

def all(rules):
    for rule in rules:
        filters = get_filters(rule)
        result = session.query(Emails.id)
        for filter in filters:
            result = result.filter(eval(filter))
        mail_ids = [id[0] for id in result.all()]
        print(len(mail_ids))
        actions(mail_ids, rule["actions"])

# any(rules["any"])
all(rules["all"])


