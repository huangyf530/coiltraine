import matplotlib.pyplot as plt

if __name__=="__main__":
    err = []
    X = []
    X2 = []
    err_val = []
    with open("train_error.csv", 'r') as f:
        for linenum, line in enumerate(f):
            if linenum % 100 != 0:
                continue
            line = line.strip()
            err.append(float(line))
            X.append(linenum + 1)
    with open("CoILVal1_error.csv", 'r') as f:
        for linenum, line in enumerate(f):
            line = line.strip()
            err_val.append(float(line))
            X2.append((linenum + 1) * 2000)
    plt.plot(X, err)
    plt.plot(X2, err_val)
    plt.show()
