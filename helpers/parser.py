import re
from helpers import config

_RE_COMBINE_WHITESPACE = re.compile(r"\s+")
HEADER = ";"
OFFSET = 8


class Parser():

    def __init__(self, filename):
        tcr_file = open(filename, "r")
        self.lines = tcr_file.readlines()
        self.erase_header(HEADER)
        self.params = config.get_parameters()

    def erase_header(self, HEADER):
        i = 0
        while self.lines[i][0] == HEADER:
            i = i+1
        self.lines = self.lines[i:]

    def parse_file(self):
        parsed_output = []
        self.params = config.get_parameters()
        for line in self.lines:
            line = line.strip("\n")
            line = _RE_COMBINE_WHITESPACE.sub(" ", line).strip()
            line = line.split(" ")
            data_id = line[4]
            filtered_id = data_id[2:6]
            parameter = self._hex_to_params(filtered_id)
            if parameter:
                ts = line[1]
                for key in parameter.keys():
                    name = key
                    bits = parameter[key]['Bits']
                    bits = bits.split("-")
                    rate = parameter[key]['Rate']
                    offset = parameter[key]['Offset']
                    measure = parameter[key]['Measure']
                    data = ""
                    for bit in reversed(bits):
                        data = data + line[OFFSET+int(bit)]
                    data = int("0x"+data, 16)
                    value = data * float(rate) + offset
                    parsed_output.append((name, ts, value, measure))
        return parsed_output

    def get_plotting_data(self, data):
        plotting_data = []
        self.params = config.get_parameters()
        for group in self.params.keys():
            for parameter in self.params[group].keys():
                x = []
                y = []
                for d in data:
                    if d[0] == parameter:
                        x.append(float(d[1]))
                        y.append(float(d[2]))
                plotting_data.append((x, y, parameter))
        return plotting_data

    def _hex_to_params(self, filtered_id):
        return self.params.get(filtered_id)
