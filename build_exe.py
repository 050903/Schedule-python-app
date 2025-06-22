import PyInstaller.__main__
import os

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# PyInstaller arguments
args = [
    '--onefile',  # Create a single executable file
    '--windowed',  # Hide console window (GUI app)
    '--name=ScheduleApp',  # Name of the executable
    '--icon=schedule_icon.ico',  # Custom schedule icon
    '--add-data=justdoit.mp3;.',  # Include the sound file
    '--distpath=dist',  # Output directory
    '--workpath=build',  # Build directory
    'schedule.py'  # Main Python file
]

# Run PyInstaller
PyInstaller.__main__.run(args)