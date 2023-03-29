import os
import subprocess
import time

PATH = "ca.pfv.spmf.algorithms.sequential_rules.rulegrowth"


class Main:
    def __init__(self):
        print("Importing log.")
        # print(f"Importing log: {constants.LOG_PATH}")
        # self.log = importer.apply(os.path.join("..",constants.LOG_PATH))

    def run(self, miner):
        if miner == "ERMiner":
            support = .2  # electronics: sup=0,0005, conf=0,1 .sf: 0,
            confidence = .3  # steam: sup=0,005 conf=0,6.
            input_data = os.path.join("../../../..", "data", "traces.txt")
            title = "result_" + str(support) + "_" + str(confidence)
            self.call_spmf_mod(title, support, confidence, input_data)


    def get_current_dir(self):
        returned_output = subprocess.check_output("cd", shell=True, stderr=subprocess.STDOUT)
        print("Currently here: ", returned_output.decode("utf-8"))

    def call_spmf_mod(self, title, min_sup, min_conf, data):
        start_time = time.time()

        out_label = title + "_rules.txt"
        out_file = out_label
        self.get_current_dir()
        print("input data: ", data)
        os.chdir('spmf_mod/out/production/spmf')
        self.call("AlgoERMiner", min_sup, min_conf, data, out_label,
                  consequent=20)  # cons: maximale #of items in coms => number of items-1
        os.chdir('../../../..')
        self.get_current_dir()
        if os.path.isfile(out_file):  # if file exists: -> remove it
            os.remove(out_file)
        os.rename("spmf_mod/out/production/spmf/" + out_label, out_file)
        print("Computation took {} seconds".format(time.time() - start_time))

    def call(self, algo, sup, conf, data, out, consequent):
        results = []
        command = "java " + PATH + "." + algo + f" {sup} {conf} {data} {out} {consequent}"
        try:
            returned_output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                "command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        out_string = returned_output.decode("utf-8")
        print("######### FINISHED")
        print(out_string)
        mem = None
        nr_rules = None
        time = None
        print(len(out_string))
        for line in out_string.split("\n"):
            line = line.strip()
            if line.startswith("Sequential rules count:"):
                nr_rules = line.split(" ")[-1]
            if line.startswith("Total time:"):
                time = line.split(" ")[-2]
            if line.startswith("Max memory:"):
                mem = line.split(" ")[-1]
        results.append(
            {"algorithm": algo, "support": sup, "confidence": conf, "number of rules": nr_rules, "time": time,
             "memory": mem})
        with open("stats_" + out, "w") as text_file:
            text_file.write(returned_output.decode("utf-8"))


if __name__ == "__main__":
    """Finds the rules included in the input_format/events file in numerical spmf format, named in the run methode.
    The resulting file of rules is saved in the folder FPClu. And has to be moved manually into the corresponding input_format folder.
    This is then used as input for preprocessor to get the projections of cases for every rule."""
    main = Main()
    main.run("ERMiner")
