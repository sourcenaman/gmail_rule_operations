if __name__ == "__main__":
    import json
    from helpers.apply_rules import ApplyRules
    from helpers.db_operations import FetchEmails

    #read rules json file
    print("Fetching rules from rules.json")
    with open("rules.json", 'r') as rules:
        rules = json.load(rules)

    fetch = FetchEmails()

    #apply rules and perform action on all the eligible emails with condition "all"
    for rule in rules["all"]:
        print(f'Fetching eligible ids for rule: {rule["name"]}')
        ids = fetch.fetch_all(rule["conditions"])
        print(f'Fetched {len(ids)} for rule: {rule["name"]}')
        if ids:
            print(f'Performing actions on fetched ids')
            ApplyRules(ids, rule["actions"])
            print(f'Operation successful for rule: {rule["name"]}')

    #apply rules and perform action on all the eligible emails with condition "any"
    for rule in rules["any"]:
        print(f'Fetching eligible ids for rule: {rule["name"]}')
        ids = fetch.fetch_any(rule["conditions"])
        print(f'Fetched {len(ids)} for rule: {rule["name"]}')
        if ids:
            print(f'Performing actions on fetched ids')
            ApplyRules(ids, rule["actions"])
            print(f'Operation successful for rule: {rule["name"]}')

    print("Done")
