if __name__ == "__main__":
    import json
    from helpers.apply_rules import ApplyRules
    from helpers.db_operations import FetchEmails

    #read rules json file
    with open("rules.json", 'r') as rules:
        rules = json.load(rules)

    fetch = FetchEmails()

    #apply rules and perform action on all the eligible emails with condition "all"
    for rule in rules["all"]:
        ids = fetch.fetch_all(rule["conditions"])
        if ids:
            ApplyRules(ids, rule["actions"])

    #apply rules and perform action on all the eligible emails with condition "any"
    for rule in rules["any"]:
        ids = fetch.fetch_any(rule["conditions"])
        if ids:
            ApplyRules(ids, rule["actions"])

    print("Done")
