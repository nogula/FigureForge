import FigureForge.main as FigureForge

import matplotlib.pyplot as plt

fig, ax = plt.subplots()

ax.plot([1, 2, 3, 4], [1, 4, 2, 3])

fig = FigureForge.main(fig)

plt.show()
