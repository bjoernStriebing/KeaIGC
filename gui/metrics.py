from kivy.event import EventDispatcher
from kivy.core.window import Window
from kivy.properties import AliasProperty, NumericProperty

metric = None


class DynamicMetric(EventDispatcher):
    density = NumericProperty(Window._density)

    def _get(self):
        return int(self._dp * self.density)

    def _set(self, value):
        self._dp = int(value or 0)

    def __init__(self, **kwargs):
        self._dp = 1
        super(DynamicMetric, self).__init__(**kwargs)
        self.bind(density=lambda *args: self.property('dp').dispatch(self))

    dp = AliasProperty(_get, _set, allownone=True)


def update_metrics():
    if metric is None:
        return
    density = int(float(Window.width) / float(Window.system_size[0]))
    metric.density = density


if metric is None:
    metric = DynamicMetric()
