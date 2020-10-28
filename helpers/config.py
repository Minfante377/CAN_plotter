from consts.OS import SEPARATOR
import os
import json

delimiter = SEPARATOR


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
        parameters[d[1]][d[0]] = {"Bits": bits, "Rate": d[2], "Offset": int(d[3]),
                                 "Measure": d[4], "Draw": d[7]}
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


def get_unit(label):
    parameters = get_parameters()
    for pgn in parameters.keys():
        parameter = parameters[pgn].get(label)
        if parameter:
            return parameter['Measure']

def get_excluded_from_plotting():
    excluded = []
    parameters = get_parameters()
    for pgn in parameters.keys():
        for parameter in parameters[pgn].keys():
            if not parameters[pgn][parameter]['Draw'] == 'true':
                excluded.append(parameter)
    return excluded
