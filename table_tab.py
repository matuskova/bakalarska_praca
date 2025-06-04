from PyQt6.QtWidgets import (QWidget, QPushButton, QTableWidget,
                             QTableWidgetItem, QComboBox, QGridLayout, QHeaderView, QLabel)

from constants import *
from basic_functions import *


class TableTab(QWidget):
    def __init__(self, data, main_dir):
        super().__init__()

        self.filter_options = ("All", "Objects", "Tags")
        self.table_header = ["Object", "Tag", "From", "To", "Time", "Heart Rate (avg.)", "ΔHR", "min. HR", "max. HR", "HR range", "view count"]

        self.data = data
        self.main_dir = main_dir

        self.layout = QGridLayout()

        self.setup_table_tab()

    def setup_table_tab(self):
        self.table = self.setup_table()
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(True)
        self.fill_table_with_data(self.data.object_data)

        self.filter_dropdown = QComboBox()
        self.filter_dropdown.addItems(self.filter_options)
        self.layout.addWidget(self.filter_dropdown, 0, 0)

        self.filter_button = QPushButton("Apply")
        self.filter_button.setMaximumWidth(200)
        self.filter_button.clicked.connect(self.apply_filter)
        self.layout.addWidget(self.filter_button, 0, 1)

        self.layout.addWidget(self.table, 1, 0, 1, 2)

        self.setLayout(self.layout)

    def setup_table(self):
        table = QTableWidget()
        table.setColumnCount(len(self.table_header))

        table.setHorizontalHeaderLabels(self.table_header)

        header = table.horizontalHeader()
        for col in range(table.columnCount()):
            header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

        return table

    def create_formatted_record(self, record):
        if len(record) != len(self.table_header):
            record = [None] * len(self.table_header)
        obj, tag, from_t, to_t, sum_t, hr, hr_change, hr_max, hr_min, hr_range, view_count = record
        obj_s = "-" if obj is None else obj
        tag_s = "-" if tag is None else tag
        from_s = "-" if from_t is None or not isinstance(from_t, time) else formate_time(from_t)
        to_s = "-" if to_t is None or not isinstance(to_t, time) else formate_time(to_t)
        sec = sum_t
        if sum_t is None or not isinstance(sum_t, float):
            sec = 0
        sum_s = formate_time(sec_to_time(sec))
        hr_s = "N/A" if hr is None or hr == 0 else str(int(hr))

        if hr_change is None:
            hr_change_s = "N/A"
        else:
            hr_change = int(hr_change)
            arrow = "↓" if hr_change <= 0 else "↑"
            color = "green" if hr_change <= 0 else "red"

            hr_change_s = f'<span style="color:{color}; font-size:18px">{arrow}</span> {str(int(hr_change))}'

        hr_change_label = QLabel()
        hr_change_label.setText(hr_change_s)
        hr_change_label.setStyleSheet("margin-left:2px;")

        hr_max_s = "N/A" if hr_max is None or not isinstance(hr_max, int) else str(hr_max)
        hr_min_s = "N/A" if hr_min is None or not isinstance(hr_min, int) else str(hr_min)
        hr_range_s = "N/A" if hr_range is None or not isinstance(hr_range, int) else str(hr_range)
        view_count_s = "-" if view_count is None or not isinstance(view_count, int) else str(view_count)

        return obj_s, tag_s, from_s, to_s, sum_s, hr_s, hr_change_label, hr_min_s, hr_max_s, hr_range_s, view_count_s

    def fill_table_with_data(self, data):
        self.table.sortItems(-1)
        self.table.setSortingEnabled(False)

        self.table.clearContents()
        self.table.setRowCount(len(data))
        for row, record in enumerate(data):
            formatted_record = self.create_formatted_record(record)

            for i, table_item in enumerate(formatted_record):
                if i == 6:
                    self.table.setCellWidget(row, i, table_item)
                else:
                    self.table.setItem(row, i, QTableWidgetItem(table_item))

        self.table.setSortingEnabled(True)

    @staticmethod
    def average_data_ignoring_zeros(data1, time1, data2, time2):
        if data1 is None:
            return data2
        if data2 is None:
            return data1
        return ((data1 * time1) + (data2 * time2)) / (time1 + time2)

    def combine_data(self, record1, record2):
        obj, tag, _, _, sum_t, hr, hr_change, hr_max, hr_min, hr_range, view_count = record1
        _, _, _, _, sum_t2, hr2, hr_change2, hr_max2, hr_min2, hr_range2, view_count2 = record2
        total_sec = sum_t + sum_t2
        hr_avg = self.average_data_ignoring_zeros(hr, sum_t, hr2, sum_t2)
        hr_change_avg = self.average_data_ignoring_zeros(hr_change, sum_t, hr_change2, sum_t2)
        hr_max_total = custom_max(hr_max, hr_max2)
        hr_min_total = custom_min(hr_min, hr_min2)
        hr_range_total = None if hr_max_total is None or hr_min_total is None else hr_max_total - hr_min_total
        view_count_total = view_count + view_count2
        return [obj, tag, None, None, total_sec, hr_avg, hr_change_avg, hr_max_total, hr_min_total, hr_range_total, view_count_total]

    def apply_filter(self):
        filter_id = self.filter_dropdown.currentIndex()

        filtered_data = list()
        data = self.data.object_data

        # All
        if filter_id == 0:
            filtered_data = data[:]
        # Objects
        elif filter_id == 1:
            data_dict = dict()
            for record in data:
                obj = record[0]
                if data_dict.get(obj) is None:
                    new_record = list(record)
                    new_record[2:4] = [None, None]
                    data_dict[obj] = new_record
                else:
                    data_dict[obj] = self.combine_data(record, data_dict[obj])
            filtered_data = list(data_dict.values())
        # Tags
        elif filter_id == 2:
            data_dict = dict()
            for record in data:
                tag = record[1]
                if data_dict.get(tag) is None:
                    new_record = list(record)
                    new_record[0] = None
                    new_record[2:4] = [None, None]
                    data_dict[tag] = new_record
                else:
                    combined_data = self.combine_data(record, data_dict[tag])
                    combined_data[0] = None
                    data_dict[tag] = combined_data
            filtered_data = list(data_dict.values())

        self.fill_table_with_data(filtered_data)
