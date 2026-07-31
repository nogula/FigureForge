import FigureForge as FF

import matplotlib.pyplot as plt

fig, ax = plt.subplots()

ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

fig = FF.run(fig)

plt.show()
