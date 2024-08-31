import pickle
import matplotlib.pyplot as plt


fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [1, 4, 2, 3], color="b")

with open("tests/demo_figure.pkl", "wb") as f:
    pickle.dump(fig, f)
