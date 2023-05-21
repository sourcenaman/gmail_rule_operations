from .auth import get_creds
from googleapiclient.discovery import build
import json


class MailService():
    def __init__(self):
        self.creds = get_creds()

    #return all ids of all the emails
    def get_ids(self):
        with build('gmail', 'v1', credentials=self.creds) as service:
            next_page = None
            mail_ids = []
            while True:
                messages = service.users().messages().list(userId='me', pageToken=next_page, maxResults=500).execute()
                mail_ids.extend(messages["messages"])
                if "nextPageToken" in messages.keys():
                    next_page = messages["nextPageToken"]
                else:
                    break
        return mail_ids

    #return raw email data of given ids
    def get_mails(self, ids):
        with build('gmail', 'v1', credentials=self.creds) as service:
            mails = []
            counter = 0
            batch = service.new_batch_http_request()

            #batch is used to club requests to limit api calls; batch can take max 100 requests at once
            while True:
                counter+=1
                batch.add(service.users().messages().get(userId='me', id=ids.pop()["id"]))
                if counter%100 == 0:
                    batch.execute()
                    mails.extend([json.loads(batch._responses[response][1].decode('utf-8')) for response in batch._responses])
                    batch = service.new_batch_http_request()
                if len(ids) == 0:
                    batch.execute()
                    mails.extend([json.loads(batch._responses[response][1].decode('utf-8')) for response in batch._responses])
                    break
        
        return mails

