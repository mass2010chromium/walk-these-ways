import os
import pickle
import sys

log_fn = os.path.expanduser(sys.argv[1])
with open(log_fn, "rb") as logfile:
    print("Loading pickle file...")
    log = pickle.load(logfile)

log_name = "hardware_closed_loop"

infos = log[log_name][1]
with open("info.pkl", "wb") as outfile:
    print("Saving log info...")
    pickle.dump(infos, outfile)

config = log[log_name][0]
with open("config.pkl", "wb") as outfile:
    print("Saving config...")
    pickle.dump(config, outfile)
