# Basic CSV IO

def read_data(file_name, off, l):
    f = open(file_name)
    #ignore header
    f.readline()
    samples = []
    for line in f:
        line = line.strip().split(",")
        if(len(line)==l):
            sample = [float(x.replace(" ","")) for x in line[off:]]
            samples.append(sample)
    return samples

def read_test_data(file_name, off, l):
    f = open(file_name)
    #ignore header
    f.readline()
    samples = []
    for line in f:
        line = line.strip().split(",")
        if (len(line)==l):
            sample = [float(x.replace(" ","")) for x in line[0:len(line)-1]]
            samples.append(sample)
    return samples

def write_delimited_file(file_path, data,header=None, delimiter=","):
    f_out = open(file_path,"w")
    if header is not None:
        f_out.write(delimiter.join(header) + "\n")
    for line in data:
        if isinstance(line, str):
            f_out.write(line + "\n")
        else:
            f_out.write(delimiter.join(line) + "\n")
    f_out.close()