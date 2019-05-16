import matplotlib.pyplot as plt
import numpy as np

if __name__=="__main__":
    # err = []
    # X = []
    # X2 = []
    # err_val = []
    # with open("train_error.csv", 'r') as f:
    #     for linenum, line in enumerate(f):
    #         if linenum % 100 != 0:
    #             continue
    #         line = line.strip()
    #         err.append(float(line))
    #         X.append(linenum + 1)
    # with open("CoILVal1_error.csv", 'r') as f:
    #     for linenum, line in enumerate(f):
    #         line = line.strip()
    #         err_val.append(float(line))
    #         X2.append((linenum + 1) * 2000)
    # plt.plot(X, err)
    # plt.plot(X2, err_val)
    # plt.show()
    a = [0., 1.]
    b = [0., 0.]
    print(np.expand_dims(a, axis=1))
    all_ends = np.concatenate((np.expand_dims(a, axis=1), np.expand_dims(b, axis=1)), axis=1)
    print(all_ends)
    no_timeout_pos, end_cause = np.where(all_ends == 1)
    print(no_timeout_pos)
    print(end_cause)
