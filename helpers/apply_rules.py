import requests
from helpers.auth import get_creds
import json

class ApplyRules:
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
    
    def __init__(self, mail_ids, actions):
        self.actions(mail_ids, actions)

    def modify_mail(self, ids, addLabel, removeLabel):
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
        return resp.status_code

    def actions(self, mail_ids, actions):
        #make labels based on actions
        add_labels = []
        remove_labels = []
        ids = []
        for action in actions:
            if (action["action"] == "move"):
                add_labels.append(self.mapping_labels[action["value"]])
            elif (action["action"] == "mark as"):
                if (action["value"] == "read"):
                    remove_labels.append(self.mapping_labels[action["value"]])
                else:
                    add_labels.append(self.mapping_labels[action["value"]])    
        while True:
            ids.append(mail_ids.pop())
            if (len(ids) == 1000):
                self.modify_mail(ids, add_labels, remove_labels)
                ids = []
            if (len(mail_ids) == 0):
                self.modify_mail(ids, add_labels, remove_labels)
                break
        return True



