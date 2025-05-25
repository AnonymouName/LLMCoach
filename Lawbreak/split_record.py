import os
import shutil

def copy_to(Apollo_path, target_path, port):
    Apollo_record = os.listdir(Apollo_path)
    for file_name in Apollo_record:
        if "S_" in file_name or "S" in file_name and "SM" not in file_name:
            source_file = os.path.join(Apollo_path, file_name)
            if "S" in file_name and "S_" not in file_name:
                target_path_s = target_path + "/S/"+ file_name.split(".")[0].replace("_s","").replace("S","S_").replace("CH_", "")
            else:
                target_path_s = target_path + "/S/"+ file_name.split(".")[0].replace("_s","").replace("CH_", "")
            if not os.path.exists(target_path_s):
                os.makedirs(target_path_s)
            target_path_s_a = target_path_s + port
            if not os.path.exists(target_path_s_a):
                os.makedirs(target_path_s_a)
            shutil.copyfile(source_file, target_path_s_a+"/"+file_name)
        elif "SM" in file_name:
            source_file = os.path.join(Apollo_path, file_name)
            target_path_s = target_path + "/SM/"+ file_name.split(".")[0].replace("_s","").replace("CH_", "")
            if not os.path.exists(target_path_s):
                os.makedirs(target_path_s)
            target_path_s_a = target_path_s + port
            if not os.path.exists(target_path_s_a):
                os.makedirs(target_path_s_a)
            shutil.copyfile(source_file, target_path_s_a+"/"+file_name)
        elif "A_" in file_name:
            source_file = os.path.join(Apollo_path, file_name)
            target_path_s = target_path + "/A/"+ file_name.split(".")[0].replace("_s","").replace("CH_", "")
            if not os.path.exists(target_path_s):
                os.makedirs(target_path_s)
            target_path_s_a = target_path_s + port
            if not os.path.exists(target_path_s_a):
                os.makedirs(target_path_s_a)
            shutil.copyfile(source_file, target_path_s_a+"/"+file_name)
        else:
            print(file_name)

if __name__ == "__main__":
    Apollo_path = "record/Apollo"
    CH_S_path = "record/CH_S"
    CH_SM_path = "record/CH__SM"
    CH_A_path= "record/CH_A"

    target_path = "/home/sunsun/Desktop/UDriver/Lawbreak/LLM_record"
    # copy_to(Apollo_path, target_path, "/Apollo")
    # copy_to(CH_S_path, target_path, "/CH")
    # copy_to(CH_SM_path, target_path, "/CH")
    copy_to(CH_A_path, target_path, "/CH")