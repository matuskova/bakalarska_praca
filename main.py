import sys
from PyQt6.QtWidgets import QApplication, QTabWidget, QMainWindow, QFileDialog

from table_tab import *
from data_processing import *


class FolderPickerApp(QWidget):
    def __init__(self):
        super().__init__()

        self.main_dir = MainDirClass()

        self.folder_label = QLabel("No folder selected", self)
        self.folder_label.setWordWrap(True)
        self.main_dir.load_last_path()
        self.update_label_text(f"{self.main_dir.last_path}/{self.main_dir.folder}")

        self.warning_label = QLabel("", self)
        self.warning_label.setWordWrap(True)

        self.choose_button = QPushButton("Select Folder", self)
        self.open_button = QPushButton("Open", self)
        self.choose_button.clicked.connect(self.open_folder_dialog)
        self.open_button.clicked.connect(self.open_main_window)

        layout = QGridLayout()
        layout.addWidget(self.folder_label, 0, 0, 1, 2)
        layout.addWidget(self.warning_label, 1, 0, 1, 2)
        layout.addWidget(self.open_button, 2, 1)
        layout.addWidget(self.choose_button, 2, 0)
        self.setLayout(layout)

        self.setWindowTitle("Folder Picker")
        self.setGeometry(200, 200, 400, 200)

    def update_label_text(self, path):
        if path:
            self.folder_label.setText(f"Selected Folder:\n{path}")

    def open_folder_dialog(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select a Folder", self.main_dir.last_path)
        if folder_path:
            self.main_dir.change_dir_info(folder_path)
            self.update_label_text(folder_path)
            self.warning_label.setText("")

    def check_necessary_files(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            self.warning_label.setText(f"Wrong directory:\nThe dir '{path}' does not exist!")
            return False
        if (not os.path.exists(f"{path}\\{self.main_dir.data_file_name}") or
                not os.path.exists(f"{path}\\{self.main_dir.images_dir_name}") or
                not os.path.exists(f"{path}\\{self.main_dir.hr_data_file_name}") or
                not os.path.isdir(f"{path}\\{self.main_dir.images_dir_name}")):
            self.warning_label.setText(f"Wrong directory:\nNecessary file or directory in '{path}' is missing!")
            return False
        return True

    def open_main_window(self):
        if self.main_dir.folder is None or not self.check_necessary_files(self.main_dir.get_folder_path()):
            return
        self.main_dir.save_last_path()
        data = DataClass(self.main_dir)
        self.main_window = MainWindow(data, self.main_dir)
        self.main_window.show()
        self.close()


class MainWindow(QMainWindow):
    def __init__(self, data, main_dir):
        super().__init__()

        self.data = data

        self.main_dir = main_dir

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.graph_tab = GraphTab(data, main_dir)
        self.table_tab = TableTab(data, main_dir)

        self.tabs.addTab(self.graph_tab, "Graph")
        self.tabs.addTab(self.table_tab, "Table")

        self.setWindowTitle("Eyetracking and heart rate data visualizer")
        self.setGeometry(100, 100, 1200, 600)

        self.tabs.currentChanged.connect(self.on_tab_changed)
        self.on_tab_changed(0)

    def on_tab_changed(self, index):
        widget = self.tabs.widget(index)
        widget.setFocus()


app = QApplication(sys.argv)
folder_picker = FolderPickerApp()
folder_picker.show()
sys.exit(app.exec())
