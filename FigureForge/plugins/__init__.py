import os
import sys
import importlib
import inspect
from FigureForge import PLUGINS_DIR


def _load_plugins():
    sys.path.append(PLUGINS_DIR)
    for filename in os.listdir(PLUGINS_DIR):
        if filename.endswith(".py") and filename != "__init__.py":
            module_name = filename[:-3]
            module = importlib.import_module(f"FigureForge.plugins.{module_name}")

            for name, obj in inspect.getmembers(module, inspect.isclass):
                if obj.__module__ == module.__name__:
                    if hasattr(obj, "run"):
                        plugin_instance = obj()
                        globals()[module_name] = plugin_instance.run
                        print(f"Loaded plugin: {module_name}")
                        break


_load_plugins()

from .add_annotation import AddAnnotation
from .add_legend import AddLegend
from .add_minor_data_ticks import AddMinorDataTicks
from .reduce_tick_limits import ReduceTickLimits
from .set_spine_bounds import SetSpineBounds
from .toggle_spines import ToggleSpines

add_annotation = AddAnnotation().run
add_legend = AddLegend().run
add_minor_data_ticks = AddMinorDataTicks().run
reduce_tick_limits = ReduceTickLimits().run
set_spine_bounds = SetSpineBounds().run
toggle_spines = ToggleSpines().run
