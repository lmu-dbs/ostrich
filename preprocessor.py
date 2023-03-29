import datetime
import os

import utils

class RuleOcc:

    def __init__(self, a_s:tuple, a_e:tuple, c_s:tuple, c_e:tuple):
        # tuples of index and timestamps in ms
        self.ant_start = a_s
        self.ant_end = a_e
        self.cons_start = c_s
        self.cons_end = c_e

    def compute_duration(self):
        return self.cons_end[1] - self.ant_start[1]

    def compute_waiting_time(self):
        return self.cons_start[1] - self.ant_end[1]

    def __str__(self):
        return f"Antecedent start: {self.ant_start}\n" \
               f"Antecedent end: {self.ant_end}\n" \
               f"Consequent start: { self.cons_start},\n" \
               f"Consequent end: {self.cons_end},\n" \
               f"Waiting time: {self.compute_waiting_time()}\n" \
               f"Duration: {self.compute_duration()}"


class Rule: # one file per rule
    def __init__(self, antecedent, consequent, matching_cids, data, ts_data):
        self.antecedent = self.parse(antecedent)
        self.consequent = self.parse(consequent)
        self.matching_cids = matching_cids
        self.cases = []
        self.ts_cases = []
        self.map_sequences(data, ts_data)
        # self.rule_occ_per_case := {cid1: [RuleOcc1, RuleOcc2], cid2: [RuleOcc1], cid3: [RuleOcc1, RuleOcc2], ...}
        self.rule_occ_per_case = dict()

    def map_sequences(self, data, ts_data):
        s = []
        t = []
        for my_id in self.matching_cids:
            s.append(data[my_id])
            t.append(ts_data[my_id])
        self.cases = s
        self.ts_cases = t

    def parse(self, pattern):
        return [int(x) for x in pattern.split(",")]


class Preprocessor:
    def __init__(self, path_rules, path_db, path_ts):
        self.path_ts = path_ts
        self.path_db = path_db
        self.path_rules = path_rules
        self.rule_lines = dict()
        self.ts_data = []
        self.rules = []
        self.data = []

    def parse_rules(self):
        for line in self.rule_lines:
            line = line.strip()
            line = line.split(" #SUP")
            rule = line[0].split(" ==> ")  # rule[0] = antecedent, rule[1] = consequent
            cids = line[1].split("[")
            cids = cids[1][:-1]
            cids = cids.split(", ")  # -> Liste von caseIDs dieser Regel
            matching_cids = [int(el) for el in cids]  # Diejenigen CaseIDs, die diese Regel enthalten, als int in Liste
            # each rules does not consist of all cases, they are filtered based on matching cids
            new_rule = Rule(rule[0], rule[1], matching_cids, self.data, self.ts_data)  # Erstellt 1 File pro Regel

            self.rules.append(new_rule)


    def project(self):
        print(f"Got {len(self.rules)} rules")
        num_matching = 0
        for j, rule in enumerate(self.rules):  # Wir gehen alle gefundenen Regeln+Sup+Conf+CaseIDs durch
            num_matching += len(rule.matching_cids)
            # rule.cases only consists of cases where the rule matches as a whole
            for i, case in enumerate(rule.cases):
                ts_case = rule.ts_cases[i]
                occurences_ant = dict()
                occurences_cons = dict()
                for a in rule.antecedent:
                    occurences_ant[a] = []  # {a: [], b: []}
                for c in rule.consequent:
                    occurences_cons[c] = []  # {c: [], d: []}

                # Pro Case (=Liste von Act_num): checke ob El des Consequent/Antecedent.
                # Wenn ja, speichere in occurences_ant/_cons die Position im Case ab
                for k, el in enumerate(case):
                    if el in occurences_ant.keys():
                        occurences_ant[el].append(k)  # {a: [0], b: [1,4,6]}
                    if el in occurences_cons.keys():
                        occurences_cons[el].append(k)  # {c: [3, 7], d: [8]}
                # for each case we call match rules with the occurences of antecedent and consequent of that rule
                self.match_rules(occurences_ant, occurences_cons, rule, case, ts_case, rule.matching_cids[i])


    def match_rules(self, occurences_ant, occurences_cons, rule, case, ts_case, cid):
        """
        * Wird pro Regel und dabei pro Case aufgerufen.
        * occurences_ant/cons sind dictionary{Act_num: Position des Vorkommens in diesem Case}.
        """
        # break condition
        if any(len(v) == 0 for k, v in occurences_cons.items()):
            return
        res_ant = dict()
        res_cons = dict()
        for k, v in occurences_cons.items():
            res_cons[k] = min(v)

        # Save indices of antecedent item iff the index is smaller than the first index of any consequent item
        for ant_item, ant_occ_list in occurences_ant.items():
            #for cons_item, cons_occ in res_cons.items():
            for index in ant_occ_list:
                if all(index < x for x in list(res_cons.values())):
                    res_ant[ant_item] = index
        ant = list(res_ant.values())  # ant: Indizes vom Antecedent
        ant.sort()
        cons = list(res_cons.values())
        cons.sort()

        # Jeder Antecedent kommt mind. einmal vor Start des Consequent vor
        if all(k in res_ant for k in occurences_ant.keys()):
            # Minimum aller Vorkommen im Consequent nachdem Ant vollständig
            c_s = cons[0]
            c_e = cons[-1]
            # Maximum aller Vorkommen im Antecedent, die kleiner sind als Min des Cons.
            a_s = ant[0]
            a_e = ant[-1]

            occ = RuleOcc((a_s, ts_case[a_s]), (a_e,  ts_case[a_e]), (c_s,ts_case[c_s]), (c_e, ts_case[c_e]))
            rule.rule_occ_per_case[cid] = [occ]
            return

        else:
            min_vals = list()
            for k, v in occurences_cons.items():
                min_vals.append((k, min(v)))
            t = min(min_vals, key=lambda x: x[1])
            occurences_cons[t[0]].remove(t[1])

        # Fkt. ruft sich selber wieder auf, für den Fall, dass Index(cons) < Index(ant) ist
        self.match_rules(occurences_ant, occurences_cons, rule, case, ts_case, cid)

    def write_cases(self):
        """ Writes the timestamps for every affected case in FPClus/results/timestamp_of_exp/projections.txt.
        The timestamps are as follows, with a=antecedent, c=consequent, s=start and e=end:
         (a_s, a_e, c_s, c_e, c_s-a_e, c_e-a_s)"""
        ts_dir = os.path.join(os.getcwd(), "results", datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        os.makedirs(ts_dir)
        with open(os.path.join(ts_dir, "projections.txt"), "w") as f:
            for i, rule in enumerate(self.rules):
                f.write("#Rule: " + str(rule.antecedent) + " ==> " + str(rule.consequent) + "\n")
                for cid, occ_list in rule.rule_occ_per_case.items():
                    for occ in occ_list:
                        write_string = "" + str(cid) + ": "
                        write_string += str(int(occ.ant_start[1])) + "," + \
                            str(int(occ.ant_end[1])) + "," + \
                            str(int(occ.cons_start[1])) + "," + \
                            str(int(occ.cons_end[1])) + "," + \
                            str(int(occ.cons_start[1])-int(occ.ant_end[1])) + "," + \
                            str(int(occ.cons_end[1]) - int(occ.ant_start[1]))  # Waitingtime, Duration between Ant and Cons
                        write_string = write_string + "\n"
                        f.write(write_string)


if __name__ == "__main__":
    path_prefix = "data"
    path_rules = os.path.join(path_prefix, "result_0.2_0.3_rules.txt")
    path_db = os.path.join(path_prefix, "traces.txt")
    path_ts = os.path.join(path_prefix, "timestamps.txt")
    preprocessor = Preprocessor(path_rules, path_db, path_ts)
    preprocessor.data = utils.read_db(path_db)  # hier wird num_cases eingelesen: Jeder Case im SPMF-Format mit Zahlen statt Activities

    preprocessor.rule_lines = utils.read_rules(path_rules)
    preprocessor.ts_data = utils.read_timestamps(path_ts)  # hier wird ts_cases eingelesen: Jeder Case als Timestamps im SPMF-Format

    preprocessor.parse_rules()
    preprocessor.project()
    preprocessor.write_cases()


