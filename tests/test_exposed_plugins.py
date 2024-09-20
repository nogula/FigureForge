import FigureForge as FF
import matplotlib.pyplot as plt

fig, ax = plt.subplots()
ax.plot([1, 2, 3, 4], [1, 4, 2, 3], color="b")

FF.plugins.set_spine_bounds(ax)
FF.plugins.toggle_spines(ax)
# FF.plugins.add_annotation(ax)

plt.show()
