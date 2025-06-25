# main.py
import os
import json
import shutil
from functools import partial

# --- Kivy Imports ---
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty
from kivy.core.clipboard import Clipboard

# Thư viện duyệt file của Kivy Garden
from kivy_garden.filebrowser import FileBrowser

class ScheduleGrid(GridLayout):
    """ Lớp chứa bảng lịch học, sẽ được điền dữ liệu từ Python """
    pass

class ScheduleLayout(BoxLayout):
    """ Lớp layout chính, chứa các thành phần giao diện """
    schedule_grid = ObjectProperty(None)

class ScheduleApp(App):
    def build(self):
        # Tải file âm thanh
        self.sound = SoundLoader.load(os.path.join('assets', 'justdoit.mp3'))
        
        # Dữ liệu lịch học (giữ nguyên)
        self.schedule_data = [
            ('Sáng', '#E8E8E8', [{'session': 'Ca 1', 'time': '06:45 - 09:15'}, {'session': 'Ca 2', 'time': '09:25 - 11:55'}]),
            ('Chiều', '#D9EAD3', [{'session': 'Ca 3', 'time': '12:10 - 14:40'}, {'session': 'Ca 4', 'time': ''}]),
            ('Tối', '#FFFF00', [{'session': 'Ca 5', 'time': '19:10 - 21:50'}, {'session': '', 'time': '17:30 - 20:00'}, {'session': '', 'time': '19:10 - 21:50'}, {'session': 'Ca 6', 'time': ''}])
        ]
        self.days = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
        
        self.check_buttons = [] # Lưu các nút toggle
        self.current_file_path = None
        self.last_session_file = os.path.join(self.user_data_dir, "last_session.json")

        # Tạo giao diện từ file .kv
        self.layout = ScheduleLayout()
        self.build_schedule_grid()
        self.load_last_session()
        self.update_title()
        return self.layout

    def build_schedule_grid(self):
        grid = self.layout.schedule_grid
        grid.clear_widgets() # Xóa widget cũ nếu có
        self.check_buttons = []

        # Header
        grid.add_widget(Label(text='Ca học', bold=True, color=(0,0,0,1), background_color=get_color_from_hex('#F4B183')))
        for day in self.days:
            grid.add_widget(Label(text=day, bold=True, color=(0,0,0,1), background_color=get_color_from_hex('#F4B183')))

        # Body
        logical_row_index = 0
        for section_name, section_color, cas_in_section in self.schedule_data:
            for ca_detail in cas_in_section:
                # Cột Buổi/Ca/Giờ
                info_layout = BoxLayout(orientation='vertical', size_hint_x=None, width=150)
                if cas_in_section.index(ca_detail) == 0:
                    info_layout.add_widget(Label(text=section_name, bold=True, color=(0,0,0,1), background_color=get_color_from_hex(section_color)))
                info_layout.add_widget(Label(text=ca_detail['session'], bold=True, color=(0,0,0,1), background_color=get_color_from_hex(section_color)))
                info_layout.add_widget(Label(text=ca_detail['time'].replace('\n', ' '), color=(0,0,0,1)))
                grid.add_widget(info_layout)

                # Các ô checkbox
                row_buttons = []
                for c_idx in range(len(self.days)):
                    btn = ToggleButton(text='', group=f'cell_{logical_row_index}_{c_idx}', on_press=partial(self.toggle_check, logical_row_index, c_idx))
                    row_buttons.append(btn)
                    grid.add_widget(btn)
                self.check_buttons.append(row_buttons)
                logical_row_index += 1

    def toggle_check(self, r, c, instance):
        if instance.state == 'down':
            instance.text = '☒'
            if self.sound: self.sound.play()
        else:
            instance.text = ''

    def clear_all_checks(self):
        for row in self.check_buttons:
            for btn in row:
                btn.state = 'normal'
                btn.text = ''

    def new_schedule(self):
        self.clear_all_checks()
        self.current_file_path = None
        self.update_title()

    def _save_to_path(self, path):
        data = [[(btn.state == 'down') for btn in row] for row in self.check_buttons]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def save_schedule(self):
        if self.current_file_path:
            self._save_to_path(self.current_file_path)
            self.show_popup("Thành công", "Đã lưu lịch biểu!")
        else:
            self.save_schedule_as()

    def save_schedule_as(self):
        self.open_file_browser(self._save_as_callback)

    def open_schedule(self):
        self.open_file_browser(self._open_callback)

    def _open_callback(self, selection):
        if selection:
            path = selection[0]
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.clear_all_checks()
                for r, row_data in enumerate(data):
                    for c, is_checked in enumerate(row_data):
                        if is_checked:
                            self.check_buttons[r][c].state = 'down'
                            self.check_buttons[r][c].text = '☒'
                self.current_file_path = path
                self.update_title()
            except Exception as e:
                self.show_popup("Lỗi", f"Không thể mở file:\n{e}")
        self.popup.dismiss()

    def _save_as_callback(self, selection):
        if selection:
            path = selection[0]
            if not path.endswith('.json'):
                path += '.json'
            self._save_to_path(path)
            self.current_file_path = path
            self.update_title()
        self.popup.dismiss()

    def open_file_browser(self, callback):
        self.file_browser = FileBrowser(select_string='Chọn', cancel_string='Hủy')
        self.file_browser.bind(on_success=callback, on_canceled=lambda x: self.popup.dismiss())
        self.popup = Popup(title="Chọn file", content=self.file_browser, size_hint=(0.9, 0.9))
        self.popup.open()

    def copy_image_to_clipboard(self):
        try:
            # Chụp ảnh cửa sổ và sao chép vào clipboard
            Window.screenshot(name='temp_screenshot.png')
            Clipboard.copy_image('temp_screenshot.png')
            self.show_popup("Thành công", "Đã sao chép ảnh vào clipboard!")
        except Exception as e:
            self.show_popup("Lỗi", f"Không thể sao chép ảnh:\n{e}")

    def update_title(self):
        if self.current_file_path:
            self.title = f"Lịch học - {os.path.basename(self.current_file_path)}"
        else:
            self.title = "Lịch học - (Chưa có tên)"

    def show_popup(self, title, text):
        popup = Popup(title=title, content=Label(text=text), size_hint=(0.7, 0.3))
        popup.open()

    def on_stop(self):
        # Tự động lưu phiên làm việc cuối
        data = [[(btn.state == 'down') for btn in row] for row in self.check_buttons]
        with open(self.last_session_file, 'w', encoding='utf-8') as f:
            json.dump(data, f)

    def load_last_session(self):
        if os.path.exists(self.last_session_file):
            try:
                with open(self.last_session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                for r, row_data in enumerate(data):
                    for c, is_checked in enumerate(row_data):
                        if is_checked:
                            self.check_buttons[r][c].state = 'down'
                            self.check_buttons[r][c].text = '☒'
            except Exception:
                pass

if __name__ == '__main__':
    ScheduleApp().run()