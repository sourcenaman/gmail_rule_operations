from helpers.database import *
from dateutil import parser
import base64, pytz
from datetime import datetime, timedelta


class InsertEmails():
    def __init__(self, mails):
        self.session = Session(bind=engine)
        self.mails = mails
        self._parse_mails()

    def _extract_body(self, parts):
        for part in parts:
            mimeType = part["mimeType"]
            if (mimeType in ["text/plain", "text/html"] and "data" in part["body"].keys()):
                return part["body"]["data"]
            elif ("parts" in part.keys()):
                return self._extract_body(part["parts"])
        return False
    
    def _parse_headers(self, mail):
        headers = {}
        headers["id"] = mail["id"]
        for header in mail["payload"]["headers"]:
            if header["name"].lower() == "from":
                sender = header["value"]
                #sender email example: Amazon.in <shipment-tracking@amazon.in>
                headers["sender"] = sender[sender.find("<")+1:sender.find(">")]
            elif header["name"].lower() == "date":
                #date comes in different timezones and formats
                date_arr = header["value"].split(" ")
                datetime_obj = parser.parse(" ".join(date_arr[1:5]))
                headers["received_date"] = datetime_obj.astimezone(pytz.timezone('Asia/Kolkata'))
            elif header["name"].lower() == "subject":
                headers["subject"] = header["value"]
        return headers

    def _parse_body(self, mail):
        #body is base64 encoded
        body = None
        if ("parts" in mail["payload"].keys()):
            body_encoded = self._extract_body(mail["payload"]["parts"])
            if body_encoded:
                body = base64.urlsafe_b64decode(body_encoded)
        elif (mail["payload"]["mimeType"] in ["text/plain", "text/html"] and "data" in mail["payload"]["body"].keys()):
            body = base64.urlsafe_b64decode(mail["payload"]["body"]["data"])
        return {"body": body}
    
    def _parse_mails(self):
        parsed_mails = []
        for mail in self.mails:
            headers = self._parse_headers(mail)
            body = self._parse_body(mail)
            parsed_mails.append(headers | body)
        self._insert_mails(parsed_mails)
            
    def _insert_mails(self, parsed_mails):
        session = Session(bind=engine)
        try:
            session.bulk_insert_mappings(
                Emails,
                [
                    mail for mail in parsed_mails
                ],
            )
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

class FetchEmails():
    mapping_predicate = {
        "contains": "ilike",
        "does not contain": "notlike",
        "equals": "==",
        "not equals": "!=",
        "less than": ">",
        "greater than": "<"
    }
    
    def __init__(self):
        self.session = Session(bind=engine)

    #returns list of filters in sqlAlchemy's filter format
    def get_filters(self, conditions):
        filters = []
        for condition in conditions:
            if (condition["predicate"] in ["contains", "does not contain"]):
                filters.append(f'Emails.{condition["field"]}.{self.mapping_predicate[condition["predicate"]]}("%{condition["value"]}%")')
            elif (condition["field"] == "received_date"):
                current_time = datetime.now()
                delta = timedelta(days=condition["value"]) if condition["type"] == "day" else timedelta(days=30*condition["value"])
                future_date = current_time - delta
                filters.append(f'Emails.{condition["field"]}{self.mapping_predicate[condition["predicate"]]}"{future_date}"')
            else:
                filters.append(f'Emails.{condition["field"]}{self.mapping_predicate[condition["predicate"]]}"{condition["value"]}"')
        return filters

    #creates and condition for filters    
    def fetch_all(self, conditions):
        filters = self.get_filters(conditions)
        result = self.session.query(Emails.id)
        for filter in filters:
            result = result.filter(eval(filter))
        mail_ids = [id[0] for id in result.all()]
        return mail_ids

    #creates or condition for filters
    def fetch_any(self, conditions):
        filters = self.get_filters(conditions)
        result = self.session.query(Emails.id)
        temp = result.filter(eval(filters[0]))
        for filter in filters:
            result1 = result.filter(eval(filter))
            temp = temp.union(result1)
        mail_ids = [id[0] for id in temp.all()]
        return mail_ids

