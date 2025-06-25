# Lucky Wheel App

A spinning wheel application for randomly selecting names with animated celebration effects.

## Features

- Animated spinning wheel with customizable names
- Animated celebration popup when a winner is selected
- Email notification system
- Name management (add, delete, reset)
- Persistent storage of names in a text file

## Setup

1. Make sure you have Python installed with tkinter and Pillow libraries
2. Run the application: `python lucky_wheel_app.py`
3. The app will create an "icons" folder on first run - add your icons there

## Usage

1. Add names using the input field on the right side
2. Click "QUAY NGAY" to spin the wheel
3. When the wheel stops, an animated celebration popup will appear
4. Optional: Enter an email address to receive notifications

## Email Configuration

To enable email notifications, make sure to:
1. Use a valid email address
2. Configure your email provider to allow app passwords if using Gmail
3. Check the console for any email sending errors

## Customization

You can customize colors, fonts, and other settings by modifying the constants at the top of the script.