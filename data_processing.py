import json
import os
from datetime import datetime
from pathlib import Path

from graph_tab import *
from basic_functions import *


class MainDirClass:
    def __init__(self):
        self.last_path = ""
        self.folder = "data"
        self.data_file_name = "data.csv"
        self.images_dir_name = "images"
        self.hr_data_file_name = "hr_data.csv"

    def get_folder_path(self):
        return f"{self.last_path}\\{self.folder}"

    def get_text_data_path(self):
        return f"{self.last_path}\\{self.folder}\\{self.data_file_name}"

    def get_hr_data_path(self):
        return f"{self.last_path}\\{self.folder}\\{self.hr_data_file_name}"

    def get_image_dir_path(self):
        return f"{self.last_path}\\{self.folder}\\{self.images_dir_name}"

    def change_dir_info(self, path):
        self.last_path = os.path.dirname(path)
        self.folder = os.path.basename(path)

    def load_last_path(self):
        if os.path.exists(LAST_DIR_FILE):
            with open(LAST_DIR_FILE, 'r') as file:
                data = json.load(file)
                self.last_path = data.get("last_path")
                self.folder = data.get("folder")

    def save_last_path(self):
        with open(LAST_DIR_FILE, 'w') as file:
            data = {"last_path": self.last_path, "folder": self.folder}
            json.dump(data, file)


class DataClass:
    def __init__(self, main_dir: MainDirClass):
        self.hr_data = self.load_heart_rate_data(main_dir)

        self.hr_log_interval = self.calculate_hr_log_interval()
        self.hr_baseline = self.calculate_hr_baseline()

        image_names = self.get_image_names(main_dir)
        self.gaze_capture_times = self.get_capture_times_from_names(image_names)

        text_data_list = self.load_text_data(main_dir)
        self.start_time = self.calculate_start_time(text_data_list)
        self.object_data = self.create_object_data(text_data_list)

    def get_object_at_time(self, t):
        selected_entry = next(
            (entry for entry in self.object_data if time_to_sec(entry[2]) <= t <= time_to_sec(entry[3])),
            None)

        if selected_entry:
            return selected_entry[0]
        return ""

    def calculate_hr_baseline(self):
        hr_values = list(filter(lambda x: x is not None, self.hr_data.values()))
        return sum(hr_values) // len(hr_values)

    @staticmethod
    def get_capture_times_from_names(image_names):
        gaze_times = list()
        for name in image_names:
            if len(name) != 6 or not name[0:2].isdigit() or not name[2:4].isdigit() or not name[4:6].isdigit():
                continue
            hours = int(name[0:2])
            minutes = int(name[2:4])
            seconds = int(name[4:6])
            if 60 > minutes > 0 or 60 > seconds > 0:
                gaze_time = hours * 3600 + minutes * 60 + seconds
                gaze_times.append(gaze_time)
        return numpy.array(gaze_times)

    @staticmethod
    def get_image_name_from_seconds(s):
        hours = s // 3600
        minutes = (s % 3600) // 60
        seconds = s % 60
        return f"{hours:02}{minutes:02}{seconds:02}"

    def calculate_start_time(self, text_data_list):
        hr_first_time = min(list(self.hr_data.keys()))
        objects_data_first_time = text_data_list[0][2]
        return min(hr_first_time, objects_data_first_time)

    def calculate_hr_log_interval(self):
        hr_data_iter = iter(self.hr_data)
        hr_time1 = next(hr_data_iter)
        hr_time2 = next(hr_data_iter)
        hr_time3 = next(hr_data_iter)
        interval = time_to_sec(hr_time2) - time_to_sec(hr_time1)
        if interval != time_to_sec(hr_time3) - time_to_sec(hr_time2):
            print(f"HR data times are inconsistent. (Using hr time interval {interval}.)")
        return interval

    @staticmethod
    def load_heart_rate_data(main_dir):
        data = dict()
        with open(main_dir.get_hr_data_path(), 'r') as file:
            file.readline()
            for line in file:
                record = line.strip().split(DELIMITER)
                if len(record) != 3:
                    continue
                real_time_string, therapy_time_string, hr = record
                try:
                    real_time = datetime.strptime(real_time_string, TIME_FORMAT_HR).time()
                except ValueError:
                    real_time = datetime.min.time()
                if not hr.isdigit():
                    hr_num = None
                else:
                    hr_num = int(hr)
                data[real_time] = hr_num
        return data

    @staticmethod
    def load_text_data(main_dir):
        data = list()
        with open(main_dir.get_text_data_path(), 'r') as file:
            file.readline()
            for line in file:
                record = line.strip().split(DELIMITER)
                if len(record) == DATA_COLUMN_COUNT:
                    obj, tag = record[0], record[1]
                    try:
                        from_t = datetime.strptime(record[2], TIME_FORMAT_EYETRACKING)
                        to_t = datetime.strptime(record[3], TIME_FORMAT_EYETRACKING)
                    except ValueError:
                        continue
                    data.append(tuple([obj, tag, from_t.time(), to_t.time()]))
        return data

    @staticmethod
    def get_image_names(main_dir):
        directory = Path(main_dir.get_image_dir_path())
        return [file.name.strip(FILE_EXTENSION) for file in directory.glob(f"*{FILE_EXTENSION}")]

    def get_all_heart_rates(self, time_from_s, time_to_s):
        if time_from_s < 0:
            time_from_s = 0
        hr_list = list()
        log_interval = self.hr_log_interval
        weighing = False
        hr_data_iter = iter(self.hr_data)
        while True:
            try:
                t = next(hr_data_iter)
            except StopIteration:
                break
            session_time_sec = time_to_sec(t) - time_to_sec(self.start_time)
            if self.hr_data[t] is None:
                if session_time_sec + log_interval / 2 >= time_to_s:
                    return []
                continue
            if weighing:
                if session_time_sec + log_interval / 2 >= time_to_s:
                    time_interval = log_interval - ((session_time_sec + log_interval // 2) - time_to_s)
                    hr_list.append((self.hr_data[t], time_interval))
                    break
                hr_list.append((self.hr_data[t], log_interval))
            else:
                if session_time_sec + log_interval / 2 > time_from_s:
                    weighing = True
                    time_interval = (session_time_sec + log_interval // 2) - time_from_s
                    hr_list.append((self.hr_data[t], time_interval))
                    if time_to_s - time_from_s == 0:
                        return [(self.hr_data[t], 1)]
        return hr_list

    def get_hr_change(self, record_avg):
        if record_avg is None:
            return None
        return record_avg - self.hr_baseline

    @staticmethod
    def remove_noise(data):
        clean_data = list()
        focused_obj = None
        noise_record = None
        for record in data:
            obj, tag, from_t, to_t = record
            if focused_obj == obj:
                focused_obj_record = clean_data.pop()
                _, _, foc_from_t, foc_to_t = focused_obj_record
                clean_data.append((obj, tag, foc_from_t, to_t))
                noise_record = None
                continue

            sum_sec = time_to_sec(to_t) - time_to_sec(from_t)
            if sum_sec < 0.1:
                continue

            if noise_record is not None:
                if noise_record[0] == obj:
                    record = obj, tag, noise_record[2], to_t
                else:
                    clean_data.append(noise_record)
                    focused_obj = noise_record[0]
                    noise_record = None

            if sum_sec < 0.5:
                noise_record = record
            else:
                clean_data.append(record)
                focused_obj = obj

        if noise_record is not None:
            clean_data.append(noise_record)
        return clean_data

    @staticmethod
    def make_average_from_hr_list(hr_list):
        if not hr_list:
            return None
        hr_sum = 0
        hr_time = 0
        for hr, interval in hr_list:
            hr_sum += hr * interval
            hr_time += interval
        return hr_sum / hr_time

    @staticmethod
    def get_max_min_from_hr_list(hr_list):
        if not hr_list:
            return None, None
        hr_max, hr_min = 0, 1000
        for hr, interval in hr_list:
            if hr > hr_max:
                hr_max = hr
            if hr < hr_min:
                hr_min = hr
        return hr_max, hr_min

    def create_object_data(self, text_data):
        object_data = list()
        clean_data = self.remove_noise(text_data)
        for object_record in clean_data:
            obj, tag, from_t, to_t = object_record

            from_s = time_to_sec(from_t) - time_to_sec(self.start_time)
            from_t = sec_to_time(from_s)
            to_s = time_to_sec(to_t) - time_to_sec(self.start_time)
            to_t = sec_to_time(to_s)

            if int(from_s) == 0 and int(to_s) == 0:
                continue

            sum_t = to_s - from_s
            if sum_t <= 0:
                sum_t = 1

            hr_list = self.get_all_heart_rates(from_s, to_s)

            hr_avg = self.make_average_from_hr_list(hr_list)
            hr_change = self.get_hr_change(hr_avg)
            hr_max, hr_min = self.get_max_min_from_hr_list(hr_list)
            if hr_max is None:
                hr_range = None
            else:
                hr_range = hr_max - hr_min + 1
            view_count = 1

            object_data.append((obj, tag, from_t, to_t, sum_t, hr_avg, hr_change, hr_max, hr_min, hr_range, view_count))
        return object_data
