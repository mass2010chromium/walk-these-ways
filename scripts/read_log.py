
import pickle

import numpy as np
import matplotlib.pyplot as plt

log_fn = "info.pkl"
with open(log_fn, "rb") as logfile:
    infos = pickle.load(logfile)

print(len(infos), "timesteps.")
input()
accels = []
for info in infos:
    accels.append(info["body_accel"][0])

accels = np.array(accels)
print(accels)

plt.figure(0)
plt.plot(accels[:, 0])
plt.plot(accels[:, 1])
plt.plot(accels[:, 2])
plt.show()
