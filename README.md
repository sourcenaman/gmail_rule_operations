
# Gmail rule based operations

This project works in two parts.
1. Import emails from gmail and insert them in a local database
2. Perform operations on emails which follow certain rules mentioned in a json file.


## Pre-requisite

1. In google cloud, enable Gmail api.
2. Generate credentials.json file by creating an oAuth account.
## Installation

Clone the repository.

```bash
  cd project
  pip install -r requirements.txt
```
    
## How to make rules.json

*"The json should be made according to the rules given below. Failing to do that will result in error while execution."*

1. The following structure must be followed.
```
{
  "any": [
    {
      "name": "Rule1",
      "conditions": [
        {
            "field": "sender",
            "predicate": "equals",
            "value": "nbp343@gmail.com"
        },
        {
            "field": "sender",
            "predicate": "contains",
            "value": "amazon.in"
        },
      ],
      "actions": [
        {
            "action": "move",
            "value": "Important"
        },
        {
            "action": "mark as",
            "value": "read"
        }
      ]
    }
  ],
  "all": [
    {
      "name": "Rule2",
      "conditions": [
        {
          "field": "sender",
          "predicate": "contains",
          "value": "amazon.in"
        },
        {
          "field": "subject",
          "predicate": "contains",
          "value": "407-3265286-0419553"
        },
        {
          "field": "received_date",
          "predicate": "less than",
          "value": "2",
          "type": "days"
        }
      ],
      "actions": [
        {
          "action": "mark as",
          "value": "read"
        }
      ]
    }
  ]
}

```

2. "field" can only be `sender/subject/body/received_date`
3. "predicate" in case of "field" `sender/subject/body` can only be `equals/not equals/contains/does not contain`
4. "predicate" in case of "field" `received_date` can only be `less than/greater than`
5. "type" in case of "field" `received_date` can only be `day/month`
6. "action" can only be `move/mark as`
7. "value" in "actions" in case of "action" `mark as` can only be `read/unread`
8. "value" in "actions" in case of "action" `move` can only be `important/inbox/spam/trash/starred/personal/social/promotions/updates/forums`
9. json is case-sensitive
## How to run

```
cd project
python fetch_mails.py
python apply_rules.py
```



## Future Scope

1. rule json validation
2. Validation for rate-limiting and quota limit exceed