def read_rules(path_rules):
    with open(path_rules, mode="r") as f:
        rule_lines = f.readlines()
    return rule_lines

def read_db(path_db):
    data = []
    with open(path_db) as f:
        lines = f.readlines()  # lines = Liste von Strings der Form "Regel+Sup+Conf+CaseIDs"
        for sequence in lines:
            temp = []
            for x in sequence.strip().split(" "):  # Pro Case alle Act_Nummern in temporäre Liste temp
                if x != "-1" and x != "-2":
                    temp.append(int(x))
            data.append(temp)  # temp an data übergeben
    return data  # Liste von Listen aller Case_Act_numbers


def read_timestamps(path_ts):
    ts_data = []
    with open(path_ts) as f:
        lines = f.readlines()
        for sequence in lines:  # sequence = ts1 -1 ts2 -1 ts3 ... -1 -2
            temp = []
            for x in sequence.strip().split(" "):
                if x != "-1" and x != "-2":
                    temp.append(float(x))
            ts_data.append(temp)
    return ts_data