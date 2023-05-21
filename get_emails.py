from auth import get_creds
from googleapiclient.discovery import build
import json
import pytz
import base64
from sqlalchemy import *
from database import *
from dateutil import parser

creds = get_creds()

def get_mails():
    with open('ids.json', 'r') as ids:
        ids = json.load(ids)
    with build('gmail', 'v1', credentials=creds) as service:
        mails = []
        length = len(ids)
        # length = 102
        counter = 1
        batch = service.new_batch_http_request()
        for id in ids:
            batch.add(service.users().messages().get(userId='me', id=id["id"]))
            if (counter%100==0):
                batch.execute()
                for response in batch._responses:
                    mail = json.loads(batch._responses[response][1].decode('utf-8'))
                    mails.append(mail)
                print(len(mails))
                batch = service.new_batch_http_request()
            if (counter==len(ids)):
                batch.execute()
                for response in batch._responses:
                    mail = json.loads(batch._responses[response][1].decode('utf-8'))
                    mails.append(mail)
                print(len(mails))
            counter+=1
    with open('mails.json', 'w') as ids:
        ids.write(json.dumps(mails))


def get_ids():
    creds = get_creds()
    with build('gmail', 'v1', credentials=creds) as service:
        next_page = None
        message_ids = []
        while True:
            messages = service.users().messages().list(userId='me', pageToken=next_page, maxResults=500).execute()
            message_ids.extend(messages["messages"])
            if "nextPageToken" in messages.keys():
                next_page = messages["nextPageToken"]
            else:
                print(next_page)
                break

        with open('ids.json', 'w') as ids:
            ids.write(json.dumps(message_ids))


def extract_body(parts):
    for part in parts:
        mimeType = part["mimeType"]
        if (mimeType in ["text/plain", "text/html"] and "data" in part["body"].keys()):
            return part["body"]["data"]
        elif ("parts" in part.keys()):
            return extract_body(part["parts"])
    return False
        


def insert_mails(mails):
    mail_arr = []
    for mail in mails:
        try:
            mail_data = {}
            mail_data["thread_id"] = mail["threadId"]
            mail_data["id"] = mail["id"]
            for header in mail["payload"]["headers"]:
                if header["name"].lower() == "from":
                    sender = header["value"]
                    mail_data["sender"] = sender[sender.find("<")+1:sender.find(">")]
                elif header["name"].lower() == "date":
                    date_arr = header["value"].split(" ")
                    datetime_obj = parser.parse(" ".join(date_arr[1:5]))
                    mail_data["received_date"] = datetime_obj.astimezone(pytz.timezone('Asia/Kolkata'))
                elif header["name"].lower() == "subject":
                    mail_data["subject"] = header["value"]
            if ("parts" in mail["payload"].keys()):
                body = extract_body(mail["payload"]["parts"])
                if body:
                    mail_data["body"] = base64.urlsafe_b64decode(body)
            elif (mail["payload"]["mimeType"] in ["text/plain", "text/html"] and "data" in mail["payload"]["body"].keys()):
                mail_data["body"] = base64.urlsafe_b64decode(mail["payload"]["body"]["data"])
            else:
                mail_data["body"] = None
            mail_arr.append(mail_data)
        except Exception as e:
            pass
    session = Session(bind=engine)
    try:
        session.bulk_insert_mappings(
            Emails,
            [
                mail for mail in mail_arr
            ],
        )
        session.commit()
    except Exception:
        session.rollback()
    finally:
        session.close()

with open("mails.json", "r") as mails:
    mails = json.load(mails)

insert_mails(mails)



