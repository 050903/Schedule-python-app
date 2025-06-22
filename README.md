![image](https://github.com/user-attachments/assets/fa658732-f0f3-4de2-9f0e-5b398ce872ed)# Weekly Schedule App

A simple desktop and mobile application built with Python and Tkinter to help you manage your weekly schedule.

## Features

- **Visual Grid Layout:** View your entire week's schedule at a glance.
- **Easy Check-in:** Simply click to mark a time slot as scheduled.
- **Sound Notification:** Get an audible confirmation when you check a time slot.
- **Save/Load:** Save your schedule to a file and load it back anytime.
- **Session Management:** Automatically saves your last session and reloads it on startup.
- **Export to Image:** Save your current schedule view as a JPG or PNG image.
- **Copy to Clipboard:** Quickly copy the schedule image to your clipboard to paste into other applications like messengers or documents (Windows only).
- **File Management:** Standard New, Open, Save, and Save As functionalities.

## Screenshots

*(screenshot of the application here)*

![image](https://github.com/user-attachments/assets/d621f1b7-0bdf-4a63-bae3-1e8a30d4d4f6)
![image](https://github.com/user-attachments/assets/8178ec55-0df5-4ea2-a367-7878b529feac)
![image](https://github.com/user-attachments/assets/d299c85b-fc70-4fcd-87d6-f5d4fcfb4862)
![image](https://github.com/user-attachments/assets/666570d8-b1a2-40c3-ae19-557eb5eff3f2)

## Dependencies

The application is built using Python and requires the following libraries:

- **pygame:** For playing sound effects.
- **Pillow:** For image manipulation (capturing the schedule grid).
- **pywin32:** For accessing the Windows clipboard to copy images.

You can install them using pip:
```bash
pip install pygame Pillow pywin32
```

To build the executable, you will also need `pyinstaller`:
```bash
pip install pyinstaller
```

## How to Run

1.  **Clone the repository or download the source code.**
2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: It's recommended to create a new `requirements.txt` with only `pygame`, `Pillow`, and `pywin32` for clarity).*
3.  **Run the application:**
    ```bash
    python schedule.py
    ```

## How to Build

The project includes a `build_exe.py` script and a `ScheduleApp.spec` file for PyInstaller.

To build the standalone executable:

1.  **Make sure PyInstaller is installed:** `pip install pyinstaller`
2.  **Run the build script:**
    ```bash
    python build_exe.py
    ```
3.  The final executable will be located in the `dist` directory.

## File Descriptions

- `schedule.py`: The main application code.
- `build_exe.py`: The script to build the executable using PyInstaller.
- `ScheduleApp.spec`: PyInstaller specification file.
- `requirements.txt`: List of Python packages (Note: may contain more than required).
- `schedule_data.json`: (Example) file for storing schedule data.
- `last_session.json`: Stores the state of the last session.
- `justdoit.mp3`: Sound file played on check-in.
- `schedule_icon.ico`/`scheduleicon.png`: Application icons.
- `create_icon.py`: Script to generate the `.ico` file from the `.png`. 
