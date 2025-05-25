import os, json, shutil, re

path = "scenarios/scenario_sets"
scenario_sets = os.listdir(path)
target_path = "/home/sunsun/Desktop/UDriver/Lawbreak/LLM_record"

for scenario_set in scenario_sets:
    for scenatio in os.listdir(path + "/" + scenario_set + "/scenarios"):
        with open(path + "/" + scenario_set + "/scenarios/" + scenatio, 'r') as f:
            data = json.load(f)
            descrption = "".join(data["descriptionEnTokens"])
            if "S_" in descrption:
                target_path_s = target_path + "/S"
                pattern = r'S__?\d+'
                match = re.findall(pattern, descrption)[0]
                if not os.path.exists(target_path_s + "/" + match):
                    print(scenario_set, scenatio)
                else:
                    source_file = os.path.join(path + "/" + scenario_set + "/scenarios", scenatio)
                    target_file = target_path_s + "/" + match +"/" + match + ".json"
                    shutil.copyfile(source_file, target_file)
            elif "SM" in descrption:
                target_path_s = target_path + "/SM"
                pattern = r'SM_?\d+'
                match = re.findall(pattern, descrption)[0]
                if not os.path.exists(target_path_s + "/" + match):
                    print(scenario_set, scenatio)
                else:
                    source_file = os.path.join(path + "/" + scenario_set + "/scenarios", scenatio)
                    target_file = target_path_s + "/" + match +"/" + match + ".json"
                    shutil.copyfile(source_file, target_file)
            elif "A_" in descrption:
                target_path_s = target_path + "/A"
                pattern = r'A__?\d+'
                match = re.findall(pattern, descrption)[0]
                if not os.path.exists(target_path_s + "/" + match):
                    print(scenario_set, scenatio)
                else:
                    source_file = os.path.join(path + "/" + scenario_set + "/scenarios", scenatio)
                    target_file = target_path_s + "/" + match +"/" + match + ".json"
                    shutil.copyfile(source_file, target_file)



