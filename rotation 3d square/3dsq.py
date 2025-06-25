"""
3D Square Animation with Matplotlib
-----------------------------------
This script creates a 3D square that continuously rotates around a selected axis.
Matplotlib provides cross-platform compatibility for 3D visualization.
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import RadioButtons, Slider

# Create figure and 3D axis
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# Define the square vertices (in the XY plane)
square = np.array([
    [-1, -1, 0],  # Bottom-left
    [1, -1, 0],   # Bottom-right
    [1, 1, 0],    # Top-right
    [-1, 1, 0]    # Top-left
])

# Create the square polygon
square_poly = Poly3DCollection([square], alpha=0.7, linewidths=1, edgecolors='k')
square_poly.set_facecolor('cyan')
ax.add_collection3d(square_poly)

# Set axis limits
ax.set_xlim(-2, 2)
ax.set_ylim(-2, 2)
ax.set_zlim(-2, 2)

# Add axis labels
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')

# Add title
ax.set_title('Rotating 3D Square')

# Create rotation matrices
def rotate_x(points, angle):
    """Rotate points around X axis"""
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([
        [1, 0, 0],
        [0, c, -s],
        [0, s, c]
    ])
    return np.dot(points, R.T)

def rotate_y(points, angle):
    """Rotate points around Y axis"""
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([
        [c, 0, s],
        [0, 1, 0],
        [-s, 0, c]
    ])
    return np.dot(points, R.T)

def rotate_z(points, angle):
    """Rotate points around Z axis"""
    c, s = np.cos(angle), np.sin(angle)
    R = np.array([
        [c, -s, 0],
        [s, c, 0],
        [0, 0, 1]
    ])
    return np.dot(points, R.T)

# Global variables
rotation_axis = 'y'
rotation_speed = 0.05

# Create radio buttons for axis selection
ax_radio = plt.axes([0.02, 0.8, 0.1, 0.15])
radio_buttons = RadioButtons(ax_radio, ('X', 'Y', 'Z'), active=1)

def set_axis(label):
    global rotation_axis
    rotation_axis = label.lower()
    fig.canvas.draw_idle()

radio_buttons.on_clicked(set_axis)

# Create slider for speed control
ax_slider = plt.axes([0.2, 0.05, 0.65, 0.03])
speed_slider = Slider(ax_slider, 'Speed', 0.01, 0.2, valinit=rotation_speed)

def update_speed(val):
    global rotation_speed
    rotation_speed = val
    fig.canvas.draw_idle()

speed_slider.on_changed(update_speed)

# Animation update function
def update(frame):
    # Get current angle based on frame number and speed
    angle = frame * rotation_speed
    
    # Rotate the square based on selected axis
    if rotation_axis == 'x':
        rotated = rotate_x(square, angle)
    elif rotation_axis == 'y':
        rotated = rotate_y(square, angle)
    else:  # z-axis
        rotated = rotate_z(square, angle)
    
    # Update the polygon vertices
    square_poly.set_verts([rotated])
    
    # Update title with current information
    ax.set_title(f'Rotating 3D Square (Axis: {rotation_axis.upper()})')
    
    return square_poly,

# Create animation
ani = FuncAnimation(fig, update, frames=np.arange(0, 1000), 
                    interval=30, blit=False)

# Adjust layout and display
plt.tight_layout()
plt.show()