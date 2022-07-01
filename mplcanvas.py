from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class MplCanvas(FigureCanvas):
    def __init__(self, *args, **kwargs):
        self.fig = Figure()
        super(MplCanvas, self).__init__(self.fig, *args, **kwargs)

        self.ax = None
        self.data = None
        self.x = None
        self.y = None
        self.begin = 0
        self.end = 0

        self.fig.set_facecolor("#ffe6ea")

        hint = "левый клик - приближение\n" \
               "правый клик - отдаление\n" \
               "колесико мыши - перемещение по оси времени"

        self.setToolTip(hint)

    def plot(self, x, y):
        self.fig.clear()
        self.ax = self.fig.add_subplot(111)
        self.data = self.ax.plot(x, y)
        self.draw()

    def clear(self):
        self.fig.clear()
        self.draw()

    def get_xdata(self):
        return self.data[0].get_xdata()

    def get_ydata(self):
        return self.data[0].get_ydata()

    def scale_up(self, s, ratio):
        if self.begin is None or self.end is None:
            return

        length = self.end - self.begin
        s = int(s * length)
        self.end = self.begin + min(length, int(s + length * ratio / 2))
        self.begin = self.begin + max(0, int(s - length * ratio / 2))

        self.plot(self.x[self.begin:self.end], self.y[self.begin:self.end])
        self.set_ylim()

    def scale_down(self, s, ratio):
        if self.begin is None or self.end is None:
            return

        length = self.end - self.begin
        s = int(s * length)
        self.end = min(len(self.x), int(self.begin + s + length / ratio / 2))
        self.begin = max(0, int(self.begin + s - length / ratio / 2))

        self.plot(self.x[self.begin:self.end], self.y[self.begin:self.end])
        self.set_ylim()

    def scroll(self, direction):
        if self.begin is None or self.end is None:
            return

        length = self.end - self.begin
        if direction == -1:
            delta_begin = min(self.begin, int(length * 0.1))
        else:
            delta_begin = length

        if direction == 1:
            delta_end = min(len(self.x) - self.end, int(length * 0.1))
        else:
            delta_end = length

        self.begin += direction * min(delta_begin, delta_end)
        self.end += direction * min(delta_end, delta_begin)

        self.plot(self.x[self.begin:self.end], self.y[self.begin:self.end])
        self.set_ylim()

    def set_ylim(self):
        min_value = min(self.y)
        max_value = max(self.y)
        amplitude = max_value - min_value
        self.ax.set_ylim(min_value - amplitude * 0.1, max_value + amplitude * 0.1)
        self.draw()

    def save_data(self):
        self.x = self.get_xdata()
        self.y = self.get_ydata()
        self.begin = 0
        self.end = len(self.x)

    def mousePressEvent(self, event):
        width = self.frameGeometry().width()
        s = event.x() / width
        if event.button() == 1:
            self.scale_up(s, 0.8)
        elif event.button() == 2:
            self.scale_down(s, 0.8)

    def wheelEvent(self, event):
        self.scroll(1 if event.angleDelta().y() == 120 else -1)
