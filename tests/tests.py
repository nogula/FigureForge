import FigureForge as FF

import matplotlib.pyplot as plt

fig, ax = plt.subplots()

ax.plot([1, 2, 3, 4], [1, 4, 2, 3])
ax.set_xlabel('test x label')
ax.set_ylabel('test y label')

fig = FF.run(fig, no_show_splash=True)

plt.show()
