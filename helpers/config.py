import os
import json
import platform

if platform.system() == "Windows":
    delimiter = "\\"
else:
    delimiter = "/"


def init_config():
    try:
        os.mkdir(os.getcwd()+delimiter+"consts")
    except:
        pass


def update_parameters(data):
    parameters = {}
    for d in data:
        if int(d[5]) > 1:
            bits = "{}-{}".format(d[6], int(d[6]) + int(d[5]))
        else:
            bits = d[6]
        flag = parameters.get(d[1])
        if not flag:
            parameters[d[1]] = {}
        parameters[d[1]][d[0]] = {"Bits": bits, "Rate": d[2], "Offset": int(d[3]), "Measure": d[4]}
    parameters_file = open(os.getcwd()+delimiter+"consts/parameters.txt", "w")
    parameters_file.write(str(parameters))
    parameters_file.close()


def get_parameters():
    try:
        with open(os.getcwd()+delimiter+"consts/parameters.txt") as json_file:
            return json.loads(json_file.read().replace("'", '"'))
    except Exception as e:
        print(e)
        return {}
