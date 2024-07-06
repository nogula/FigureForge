class ExamplePlugin():
    def __init__(self):
        self.name = "Remove Spines"
        self.tooltip = "Remove the top and right spines from the selected axis."
        self.icon = "FigureForge/resources/icons/new_icon.png"

    def run(self, item):
        item.spines[["top", "right"]].set_visible(False)
        print(f"Removed top and right spines from {item}.")