import numpy
import numpy as np
import pyqtgraph
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QKeyEvent

from constants import *
from basic_functions import *


class ScalablePixmapLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.original_pixmap = None
        self.setScaledContents(False)
        self.setMinimumSize(1, 1)

    def setPixmap(self, pixmap):
        self.original_pixmap = pixmap
        self._update_scaled_pixmap()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_scaled_pixmap()

    def _update_scaled_pixmap(self):
        if self.original_pixmap is None:
            return
        scaled = self.original_pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        super().setPixmap(scaled)


class GraphTab(QWidget):
    def __init__(self, data, main_dir):
        super().__init__()

        self.filter_options = ("All", "Objects", "Tags")

        self.data = data
        self.start_time = time_to_sec(self.data.start_time)

        self.main_dir = main_dir

        self.layout = QVBoxLayout()

        self.setup_graph_tab()

        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Left or event.key() == Qt.Key.Key_Right:
            x = self.vertical_line.getXPos()
            idx = np.argmax(self.xs == x)
            idx += 1 if event.key() == Qt.Key.Key_Right else -1
            self.change_displayed_time(idx)
        else:
            super().keyPressEvent(event)

    @staticmethod
    def create_info_label_text(time, hr, obj):
        return f"Time: {time.strftime(TIME_FORMAT)}, Heart rate: {hr}\nObject: {obj}"

    def add_text_to_graph(self, layout):
        self.info_label = QLabel()
        self.info_label.setStyleSheet("font-size: 16px;")
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.info_label)

    def create_graph(self, splitter):
        container = QWidget()
        graph_layout = QVBoxLayout(container)

        time_axis = TimeAxisItem(orientation="bottom")
        self.graph_widget = pyqtgraph.PlotWidget(axisItems={'bottom': time_axis})
        self.graph_widget.hideButtons()
        self.graph_widget.setBackground('w')
        self.graph_widget.setYRange(0, 130)

        self.graph_widget.setMouseEnabled(x=True, y=False)

        self.xs = numpy.array([time_to_sec(t) for t in self.data.hr_data.keys()])
        self.xs = self.xs - self.start_time
        self.ys = numpy.array([x if x is not None else 0 for x in self.data.hr_data.values()])

        self.graph_widget.plot(self.xs, self.ys, pen=pyqtgraph.mkPen(color="#007CBE", width=3), name="Heart rate")
        self.graph_widget.setXRange(self.xs[0], self.xs[50])

        self.vertical_line = pyqtgraph.InfiniteLine(pos=self.xs[0], angle=90, pen=pyqtgraph.mkPen(
                                                color="#FBAF00", width=3, style=Qt.PenStyle.DashLine))
        self.graph_widget.addItem(self.vertical_line)

        self.add_text_to_graph(graph_layout)
        graph_layout.addWidget(self.graph_widget)
        splitter.addWidget(container)

    def setup_graph_tab(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.create_graph(splitter)

        self.image_label = ScalablePixmapLabel()
        self.image_label.resize(500, 500)

        splitter.addWidget(self.image_label)

        self.layout.addWidget(splitter)

        self.change_displayed_time(0)

        self.setLayout(self.layout)
        self.graph_widget.scene().sigMouseClicked.connect(self.graph_click_event)

    def create_pixmap(self, image_name):
        pixmap = QPixmap(f"{self.main_dir.get_image_dir_path()}\\{image_name}{FILE_EXTENSION}")
        return pixmap

    def find_screenshot_for_x_pos(self, x):
        real_gaze_time = x + self.start_time

        diff_array = numpy.abs(self.data.gaze_capture_times - real_gaze_time)
        time_idx = diff_array.argmin()
        gaze_capture_time = self.data.gaze_capture_times[time_idx]

        image_name = self.data.get_image_name_from_seconds(gaze_capture_time)
        return self.create_pixmap(image_name)

    def graph_click_event(self, event):
        graph_point = self.graph_widget.plotItem.vb.mapSceneToView(event.scenePos())
        x = graph_point.x()
        diff_array = numpy.abs(self.xs - x)
        idx = diff_array.argmin()
        self.change_displayed_time(idx)

    def change_displayed_time(self, idx):
        if idx >= len(self.xs) or idx < 0:
            return
        graph_x = self.xs[idx]
        pixmap = self.find_screenshot_for_x_pos(graph_x)
        self.image_label.setPixmap(pixmap)

        self.vertical_line.setPos(graph_x)

        self.info_label.setText(self.create_info_label_text(sec_to_time(graph_x), self.ys[idx], self.data.get_object_at_time(graph_x)))


class TimeAxisItem(pyqtgraph.AxisItem):
    def tickStrings(self, values, scale, spacing):
        return ["0" if v < 0 or v // 3600 > 23 else sec_to_time(int(v)).strftime("%H:%M:%S") for v in values]
