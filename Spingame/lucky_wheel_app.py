# Import specific classes from tkinter for better performance and clarity
from tkinter import Tk, Canvas, Frame, Label, Button, Entry, Text, Listbox, Scrollbar, messagebox, NORMAL, DISABLED, Toplevel

from PIL import Image, ImageDraw, ImageTk, ImageFont
import random
import os

import math # For trigonometric calculations
import threading # For non-blocking email sending
import smtplib # For sending emails
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIG CONSTANTS ---
# File for storing names
NAMES_FILE = "names.txt"

# Window dimensions (adjusted for new UI)
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700

# Colors (Inspired by the provided image, flat design)
BG_COLOR = "#33BBC5"  # Turquoise/Teal background
PRIMARY_TEXT_COLOR = "#FFFFFF" # White text for main title
SECONDARY_TEXT_COLOR = "#E0F7FA" # Lighter text for descriptions
ACCENT_COLOR = "#FFC107" # Amber for spin button
SPINNER_BG = "#E0F7FA" # Lightest blue for spinner area
WHEEL_CENTER_COLOR = "#FFFFFF" # White for center circle
POINTER_COLOR = "#F44336" # Red for pointer
BUTTON_BG_NORMAL = "#00BCD4" # Cyan for general buttons
BUTTON_FG_NORMAL = "#FFFFFF" # White for general button text
BUTTON_BG_DISABLED = "#B0BEC5" # Grey for disabled buttons
DANGER_COLOR = "#F44336" # Red for delete button

# Spinner sector colors (a pleasing pastel palette)
SECTOR_COLORS = [
    "#F48FB1",  # Pink
    "#FFEB3B",  # Yellow
    "#80CBC4",  # Teal
    "#FFE0B2",  # Orange-cream
    "#BDBDBD",  # Grey
    "#A1887F",  # Brown
    "#C5CAE9",  # Lavender
    "#E6EE9C",  # Lime
    "#BCAAA4",  # Taupe
    "#FFCDD2",  # Light Pink
]

# Fonts
FONT_LARGE_TITLE = ("Montserrat", 28, "bold") # Modern, bold title
FONT_MEDIUM_TITLE = ("Montserrat", 16, "bold")
FONT_NORMAL = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 10)
FONT_SPINNER_TEXT_MAX_SIZE = 20 # Max font size for text on spinner
FONT_SPINNER_TEXT_MIN_SIZE = 10 # Min font size for text on spinner

# Icon directory path
ICON_DIR = os.path.join(os.path.dirname(__file__), "icons")
LOGO_PATH = os.path.join(ICON_DIR, "woay_logo.png") # Path to your logo

# Spin animation settings
SPIN_DURATION_SECONDS = 5 # Total time for the spin animation
INITIAL_SPIN_SPEED_DEG_PER_FRAME = 25 # Initial rotation speed
SPIN_DECAY_FACTOR = 0.96 # How fast the speed decreases

# --- EMAIL CONFIGURATION ---
# Use environment variables for sensitive information
EMAIL_CONFIG = {
    "SMTP_SERVER": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
    "SMTP_PORT": int(os.environ.get("SMTP_PORT", 587)),
    "SENDER_EMAIL": os.environ.get("SENDER_EMAIL", "thehaotran06@gmail.com"),
    "SENDER_PASSWORD": os.environ.get("SENDER_PASSWORD", "ebgp tplw bffr lamy"),
    "ENABLE_EMAIL_SENDING": True,  # Enable email sending by default
    "DEFAULT_ATTENDANCE_MESSAGE": "Đã có tên bạn khi điểm danh, hãy đi học đúng giờ!"
}
# ---------------------------


class WinnerPopup(Toplevel):
    """
    Animated popup window to display the winner's name with celebration effects.
    """
    def __init__(self, parent, winner_name):
        super().__init__(parent)
        self.title("Kết Quả Quay")
        self.geometry("400x300")
        self.configure(bg="#33BBC5")
        self.resizable(False, False)
        
        # Make window appear on top
        self.transient(parent)
        self.grab_set()
        
        # Center the window on the parent
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - (width // 2)
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")
        
        # Create celebration canvas
        self.canvas = Canvas(self, bg="#33BBC5", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        # Congratulation text
        self.canvas.create_text(200, 50, text="🎉 Chúc mừng 🎉", 
                               font=("Montserrat", 24, "bold"), fill="white")
        
        # Winner name (will be animated)
        self.winner_text_id = self.canvas.create_text(200, 150, text=winner_name.upper(),
                                                    font=("Montserrat", 32, "bold"), fill="white",
                                                    anchor="center")
        
        # Close button
        close_button = Button(self, text="Đóng", font=("Segoe UI", 12), 
                             bg="#FFC107", fg="white", command=self.destroy)
        close_button.pack(pady=20)
        
        # Confetti particles
        self.particles = []
        self.create_particles()
        
        # Start animations
        self.animate_winner_text()
        self.animate_particles()
    
    def create_particles(self):
        """Create confetti particles"""
        colors = ["#F48FB1", "#FFEB3B", "#80CBC4", "#FFE0B2", "#BDBDBD", 
                 "#A1887F", "#C5CAE9", "#E6EE9C", "#BCAAA4", "#FFCDD2"]
        
        for _ in range(50):
            x = random.randint(0, 400)
            y = random.randint(-50, 0)
            size = random.randint(5, 15)
            color = random.choice(colors)
            speed = random.uniform(1, 3)
            angle = random.uniform(-0.5, 0.5)
            
            particle_id = self.canvas.create_oval(x, y, x+size, y+size, fill=color, outline="")
            self.particles.append({
                "id": particle_id,
                "speed": speed,
                "angle": angle
            })
    
    def animate_particles(self):
        """Animate falling confetti"""
        for particle in self.particles:
            # Move particle down and slightly to the side
            self.canvas.move(particle["id"], particle["angle"], particle["speed"])
            
            # Get current position
            pos = self.canvas.coords(particle["id"])
            
            # If particle is out of view, reset to top
            if pos[1] > 300:
                x = random.randint(0, 400)
                y = random.randint(-50, 0)
                self.canvas.coords(particle["id"], x, y, x+10, y+10)
        
        # Continue animation
        self.after(20, self.animate_particles)
    
    def animate_winner_text(self):
        """Animate the winner's name with scaling effect"""
        scale_factors = [1.0, 1.1, 1.2, 1.1, 1.0, 0.9, 1.0]
        colors = ["white", "#FFC107", "#F44336", "#FFC107", "white"]
        
        def animate_scale(index=0):
            if index >= len(scale_factors):
                index = 0
            
            # Get current font and update size
            current_font = self.canvas.itemcget(self.winner_text_id, "font")
            base_size = 32
            new_size = int(base_size * scale_factors[index])
            new_font = ("Montserrat", new_size, "bold")
            
            # Update font and color
            color = colors[index % len(colors)]
            self.canvas.itemconfig(self.winner_text_id, font=new_font, fill=color)
            
            # Continue animation
            self.after(150, lambda: animate_scale(index + 1))
        
        animate_scale()


class SpinnerCanvas(Canvas):
    """
    Lớp điều khiển việc vẽ và hoạt ảnh vòng quay.
    """
    def __init__(self, master, names_list, logo_path=None, **kwargs):
        super().__init__(master, **kwargs)
        self.names = names_list # Reference to the list of names from parent app
        self.sector_colors = SECTOR_COLORS
        self.winner_popup = None # Reference to winner popup window
        
        # Store the effective max/min font sizes as instance variables
        # Initialize them with the global constant values
        self.effective_font_max_size = FONT_SPINNER_TEXT_MAX_SIZE
        self.effective_font_min_size = FONT_SPINNER_TEXT_MIN_SIZE

        # Try to load a system font, fallback if not found
        try:
            # Use the instance variable for font size
            self.base_text_font = ImageFont.truetype("arial.ttf", self.effective_font_max_size)
        except IOError:
            print("Warning: 'arial.ttf' not found. Using default PIL font. Text scaling might be less accurate.")
            self.base_text_font = ImageFont.load_default()
            # Adjust effective sizes for the default font if arial.ttf is not found
            self.effective_font_max_size = 16 
            self.effective_font_min_size = 8  
        
        self.text_color = "black"

        self.current_rotation_offset_deg = 0 # Current rotational offset of the entire wheel
        self.spin_speed_deg_per_frame = 0 # Current speed of rotation
        self.target_winner_name = None # The name that should land under the pointer
        self.animation_id = None # ID for the after() call
        self.spinning = False # Flag to indicate if wheel is spinning

        self.sector_item_ids = [] # List to store (arc_id, text_image_id) for items
        self.photo_images = [] # Store references to PhotoImage objects to prevent GC

        self.logo_tk_image = None
        if logo_path and os.path.exists(logo_path):
            try:
                original_logo = Image.open(logo_path).resize((70, 70), Image.Resampling.LANCZOS)
                self.logo_tk_image = ImageTk.PhotoImage(original_logo)
            except Exception as e:
                print(f"Error loading logo: {logo_path} - {e}")
        
        # Bind resize event to redraw the wheel
        self.bind("<Configure>", self._on_resize)
        
        # Initial drawing (will be refined by _on_resize)
        self.center_x = self.winfo_width() / 2
        self.center_y = self.winfo_height() / 2
        self.radius = min(self.center_x, self.center_y) * 0.8
        
        # Draw the initial wheel structure without full rotation
        self.draw_wheel()

    def _on_resize(self, event):
        """Adjust canvas elements when window is resized."""
        self.center_x = event.width / 2
        self.center_y = event.height / 2
        # Max radius for the wheel, leaving some margin
        self.radius = min(self.center_x, self.center_y) * 0.85 
        self.draw_wheel() # Redraw the wheel with new dimensions

    def draw_wheel(self):
        """Draws all elements of the wheel on the canvas."""
        self.delete("all") # Clear existing drawings
        self.sector_item_ids = []
        self.photo_images = [] # Clear old photo images

        if not self.names:
            # Draw a placeholder circle if no names
            self.create_oval(self.center_x - self.radius, self.center_y - self.radius,
                             self.center_x + self.radius, self.center_y + self.radius,
                             fill=SPINNER_BG, outline="white", width=2)
            self.create_text(self.center_x, self.center_y, text="Thêm tên để quay!", 
                             font=FONT_NORMAL, fill="grey", tag="info_text") 
            self._draw_pointer()
            return

        num_sectors = len(self.names)
        sector_angle = 360 / num_sectors

        for i, name in enumerate(self.names):
            # Calculate start and end angles for the current sector, adjusted by overall rotation
            # Tkinter arcs start at 3 o'clock (0 deg) and go counter-clockwise for positive extent.
            start_angle = (i * sector_angle + self.current_rotation_offset_deg) % 360
            
            color = self.sector_colors[i % len(self.sector_colors)]

            # Draw the arc (sector)
            arc_id = self.create_arc(
                self.center_x - self.radius, self.center_y - self.radius,
                self.center_x + self.radius, self.center_y + self.radius,
                start=start_angle, extent=sector_angle,
                fill=color, outline="white", width=2, style="pieslice"
            )

            # Calculate text position and rotation
            # Mid-angle for the text, adjusted for the current rotation
            mid_angle_deg = (start_angle + sector_angle / 2) % 360
            mid_angle_rad = math.radians(mid_angle_deg)
            
            # Position text slightly inward from the radius (adjust for aesthetic)
            # This is the distance from the center of the wheel to the center of the text.
            text_radial_offset = self.radius * 0.65 
            text_x = self.center_x + text_radial_offset * math.cos(mid_angle_rad)
            text_y = self.center_y + text_radial_offset * math.sin(mid_angle_rad)

            # --- REFINED TEXT ROTATION LOGIC ---
            # Angle for PIL rotate. PIL rotates counter-clockwise.
            # We want the text to be oriented such that its "bottom" is closer to the center.
            # If mid_angle_deg is 0 (right), text is horizontal (0 deg rotation).
            # If mid_angle_deg is 90 (up), text is vertical, reading upwards (90 deg rotation).
            # If mid_angle_deg is 180 (left), text is horizontal, reading left-to-right (180 deg rotation).
            # If mid_angle_deg is 270 (down), text is vertical, reading downwards (270 deg rotation).
            text_rotation_pil_deg = mid_angle_deg 
            
            # If the text is in the "bottom" half of the wheel (where it would appear upside down if not flipped)
            # This is typically from 90 degrees (top-left) to 270 degrees (bottom-right)
            # We flip it by adding 180 degrees to make it readable from the top of the screen.
            if 90 < mid_angle_deg < 270:
                text_rotation_pil_deg = (text_rotation_pil_deg + 180) % 360

            # --- REFINED TEXT FITTING CALCULATIONS ---
            # max_width_for_unrotated_text: This is the maximum radial depth the text can occupy.
            # It's the space from the inner edge of the text area (near center circle) to the outer edge of the wheel.
            # Text is centered at text_radial_offset. Inner boundary is self.radius * 0.15. Outer boundary is self.radius.
            # So, available radial space is (self.radius - self.radius * 0.15) = self.radius * 0.85.
            # We want the text's *width* (when unrotated) to fit within this radial space.
            # Use a safe fraction of this total radial space.
            max_width_for_unrotated_text = self.radius * 0.8 # A good portion of the radial space

            # max_height_for_unrotated_text: This is the maximum angular width the text can occupy.
            # This is the chord length of the sector at the text_radial_offset.
            # It represents the "width" of the sector at the point where the text is centered.
            # We want the text's *height* (when unrotated) to fit within this angular space.
            # Use 90% of the chord length for padding.
            max_height_for_unrotated_text = 2 * text_radial_offset * math.sin(math.radians(sector_angle / 2)) * 0.9 
            
            text_img_pil = self._create_rotated_text_image(
                name, self.base_text_font, self.text_color, text_rotation_pil_deg,
                max_width=max_width_for_unrotated_text, 
                max_height=max_height_for_unrotated_text 
            )
            tk_text_img = ImageTk.PhotoImage(text_img_pil)
            self.photo_images.append(tk_text_img) # Crucial: keep reference to avoid garbage collection

            text_image_id = self.create_image(text_x, text_y, image=tk_text_img)
            self.sector_item_ids.append((arc_id, text_image_id))
        
        # Draw the central circle
        self.create_oval(self.center_x - self.radius*0.15, self.center_y - self.radius*0.15,
                         self.center_x + self.radius*0.15, self.center_y + self.radius*0.15,
                         fill=WHEEL_CENTER_COLOR, outline="white", width=2)

        # Draw central logo if available
        if self.logo_tk_image:
            self.create_image(self.center_x, self.center_y, image=self.logo_tk_image)

        # Draw the pointer (static)
        self._draw_pointer()

    def _draw_pointer(self):
        """Draws the static pointer at the top of the wheel."""
        pointer_width = self.radius * 0.1 # Width relative to radius
        pointer_height = self.radius * 0.2 # Height relative to radius
        
        # Pointer points downwards towards the wheel from slightly above
        self.create_polygon(
            self.center_x - pointer_width / 2, self.center_y - self.radius - 5,
            self.center_x + pointer_width / 2, self.center_y - self.radius - 5,
            self.center_x, self.center_y - self.radius + pointer_height - 5,
            fill=POINTER_COLOR, outline="white", width=2
        )

    def _create_rotated_text_image(self, text, base_font, color, angle_deg, max_width, max_height):
        """
        Creates a PIL Image with rotated text, scaling down font size if necessary.
        Returns a PIL Image object.
        max_width and max_height here refer to the constraints for the *unrotated* text.
        """
        current_font_size = base_font.size
        font = base_font
        
        # Iteratively reduce font size until text fits or min size is reached
        while True:
            # Estimate text bounding box for the *unrotated* text
            temp_img = Image.new("RGBA", (1, 1))
            temp_draw = ImageDraw.Draw(temp_img)
            bbox = temp_draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Check both width and height constraints for the *unrotated* text
            # Add a small buffer (e.g., 2 pixels) to max_width/height for safety
            if (text_width <= max_width - 2 and text_height <= max_height - 2) or current_font_size <= self.effective_font_min_size:
                break # Text fits or reached minimum size
            
            current_font_size -= 1
            if current_font_size < self.effective_font_min_size: # Ensure we don't go below min size
                current_font_size = self.effective_font_min_size
                break # Break if min size reached and still doesn't fit (will be clipped)

            try:
                # Recreate font with new size. base_font.path is crucial here.
                font = ImageFont.truetype(base_font.path, current_font_size)
            except AttributeError: # Fallback for default font which doesn't have .path
                font = ImageFont.load_default()
                if current_font_size < self.effective_font_min_size:
                    break 

        # Create a new image large enough to contain the rotated text.
        # The diagonal of the unrotated text's bounding box is a good estimate for the max dimension
        # needed for the square image that will contain the rotated text.
        # Add more padding to img_dim to ensure rotated text doesn't clip at edges.
        diagonal = int(math.sqrt(text_width**2 + text_height**2))
        img_dim = max(diagonal, text_width, text_height) + 40 # Increased padding significantly for safety
        
        img = Image.new("RGBA", (img_dim, img_dim), (255, 255, 255, 0)) # Transparent background
        draw = ImageDraw.Draw(img)

        # Draw the text centered in the new image
        text_origin_x = (img_dim - text_width) / 2 - bbox[0]
        text_origin_y = (img_dim - text_height) / 2 - bbox[1]
        draw.text((text_origin_x, text_origin_y), text, font=font, fill=color)

        # Rotate the image
        rotated_img = img.rotate(angle_deg, expand=True, center=(img_dim/2, img_dim/2))
        return rotated_img

    def show_winner_popup(self, winner_name):
        """Creates and shows the winner popup, keeping a reference to prevent garbage collection."""
        self.winner_popup = WinnerPopup(self.master.master, winner_name)
        return self.winner_popup
        
    def start_spin(self, winner_name):
        """Initiates the spin animation for a given winner."""
        if self.spinning or not self.names:
            return

        self.spinning = True
        self.target_winner_name = winner_name
        self.spin_speed_deg_per_frame = INITIAL_SPIN_SPEED_DEG_PER_FRAME

        # Calculate the target final rotation offset
        num_sectors = len(self.names)
        sector_angle = 360 / num_sectors
        
        try:
            target_index = self.names.index(winner_name)
        except ValueError:
            print(f"Error: Winner '{winner_name}' not found in names list.")
            self.spinning = False
            return

        # Angle of the center of the target sector if rotation_offset is 0
        # We want the winner to land at the top, which corresponds to 90 degrees (up)
        # Tkinter's arc angles are standard math, 0=right, 90=up, 180=left, 270=down.
        # Our pointer is at the top, pointing down. This means the *center* of the winning sector
        # should align with the 90-degree mark (upwards).
        
        # Current center angle of the winner's sector (if wheel rotation offset was 0)
        target_sector_center_angle_initial = (target_index * sector_angle + sector_angle / 2) % 360

        # We want this `target_sector_center_angle_initial` to align with 90 degrees (top)
        # after rotation.
        # The wheel rotates by `current_rotation_offset_deg`.
        # So, `(90 - target_sector_center_angle_initial + 360) % 360` is the required final offset.
        # Add several full rotations to make it spin longer and look more random
        # (e.g., 5-10 full spins)
        self.final_target_rotation_offset = (90 - target_sector_center_angle_initial + 360) % 360 + random.randint(5, 10) * 360

        self.animation_id = self.after(50, self._animate_spin) # Start animation loop

    def _animate_spin(self):
        """Performs the spin animation frame by frame."""
        if not self.spinning:
            return

        # Apply rotation
        self.current_rotation_offset_deg = (self.current_rotation_offset_deg + self.spin_speed_deg_per_frame)

        # Decay speed
        self.spin_speed_deg_per_frame *= SPIN_DECAY_FACTOR

        # Redraw the wheel with the new offset
        self.draw_wheel()

        # Check for stop condition: If speed is very low AND we are close to the target.
        # Calculate the difference between current rotation and target rotation.
        diff = (self.final_target_rotation_offset - self.current_rotation_offset_deg) % 360
        
        # If the remaining difference is small and speed is low, snap to target
        if self.spin_speed_deg_per_frame < 0.2 and diff < self.spin_speed_deg_per_frame * 2: # Within 2 frames of target
            # Snap to the exact target rotation
            self.current_rotation_offset_deg = self.final_target_rotation_offset % 360
            self.draw_wheel() # Final redraw
            self.spinning = False
            self.animation_id = None
            
            # Create animated popup with the winner's name and keep a reference to it
            self.master.master.after(500, lambda: self.show_winner_popup(self.target_winner_name))
            # Add a small delay before re-enabling the button to ensure UI updates are complete
            self.master.master.after(200, lambda: self.master.master.spin_finished(self.target_winner_name))

        else:
            self.animation_id = self.after(50, self._animate_spin) # Continue animation (approx. 20 frames/sec)

class LuckySpinApp:
    """
    Ứng dụng Vòng Quay May Mắn để điểm danh ngẫu nhiên thành viên.
    """
    def __init__(self, master):
        self.master = master
        master.title("Vòng Quay May Mắn Điểm Danh")
        master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        master.resizable(False, False) # Cannot resize window for consistent UI
        master.config(bg=BG_COLOR)

        self.names_original = [] # Full list of names
        self.names_current_spin = [] # List of names available for the current spin session
        self.load_names_from_file() # Load names on startup
        
        self.spinning = False # Flag to prevent multiple spins

        self.setup_ui() # Setup all user interface elements

    def setup_ui(self):
        """Sets up all UI components based on the target design."""
        # --- Main Content Frame (split into left/right) ---
        main_content_frame = Frame(self.master, bg=BG_COLOR)
        main_content_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # --- Left Side: Wheel Canvas ---
        wheel_area_frame = Frame(main_content_frame, bg=SPINNER_BG, bd=5, relief="groove")
        wheel_area_frame.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        self.wheel_canvas = SpinnerCanvas(
            wheel_area_frame, 
            names_list=self.names_current_spin, # Pass the dynamic list
            logo_path=LOGO_PATH,
            bg=SPINNER_BG, 
            highlightthickness=0 # No default border
        )
        self.wheel_canvas.pack(fill="both", expand=True, padx=20, pady=20)
        # The initial draw will be handled by _on_resize after the widget is laid out.

        # --- Right Side: Controls and Info ---
        # Use a Canvas for the right side to allow scrolling if content overflows
        self.right_side_canvas = Canvas(main_content_frame, bg=BG_COLOR, highlightthickness=0)
        self.right_side_canvas.pack(side="right", fill="both", expand=True)

        self.right_side_frame = Frame(self.right_side_canvas, bg=BG_COLOR)
        
        # LƯU Ý QUAN TRỌNG: Lưu lại ID của cửa sổ được tạo trên canvas
        self.right_side_frame_id = self.right_side_canvas.create_window((0,0), window=self.right_side_frame, anchor="nw")

        # Configure scrollbar
        self.right_side_scrollbar = Scrollbar(main_content_frame, orient="vertical", command=self.right_side_canvas.yview)
        self.right_side_canvas.config(yscrollcommand=self.right_side_scrollbar.set)
        self.right_side_scrollbar.pack(side="right", fill="y")

        # Bind frame size to canvas scrollregion
        self.right_side_frame.bind("<Configure>", lambda e: self.right_side_canvas.configure(scrollregion = self.right_side_canvas.bbox("all")))
        
        # SỬA ĐỔI DÒNG NÀY: Sử dụng self.right_side_frame_id thay vì winfo_children()[0]
        self.right_side_canvas.bind('<Configure>', lambda e: self.right_side_canvas.itemconfig(self.right_side_frame_id, width=e.width))


        # Title and description
        Label(self.right_side_frame, text="Vòng Quay May Mắn", font=FONT_LARGE_TITLE, 
                 bg=BG_COLOR, fg=PRIMARY_TEXT_COLOR) \
            .pack(pady=(0, 10), anchor="w")
        Label(self.right_side_frame, text="Quay để điểm danh ngẫu nhiên thành viên!", 
                 font=FONT_MEDIUM_TITLE, bg=BG_COLOR, fg=SECONDARY_TEXT_COLOR, wraplength=350) \
            .pack(pady=(0, 20), anchor="w")

        # Email Input (for visual parity with original image, no actual functionality)
        Label(self.right_side_frame, text="Để nhận thông báo về điểm danh, vui lòng nhập email:", 
                 font=FONT_NORMAL, bg=BG_COLOR, fg=PRIMARY_TEXT_COLOR) \
            .pack(pady=(0,5), anchor="w") 
        
        email_input_frame = Frame(self.right_side_frame, bg="white", bd=1, relief="flat")
        email_input_frame.pack(fill="x", pady=5)
        self.email_icon = self.load_icon("email_icon.png", 20)
        if self.email_icon:
            Label(email_input_frame, image=self.email_icon, bg="white").pack(side="left", padx=10)
        self.email_entry = Entry(email_input_frame, font=FONT_NORMAL, bd=0, relief="flat", bg="white", fg="grey")
        self.email_entry.insert(0, "Nhập email hợp lệ") # Placeholder text
        self.email_entry.bind("<FocusIn>", self._clear_placeholder)
        self.email_entry.bind("<FocusOut>", self._add_placeholder)
        self.email_entry.pack(side="left", fill="x", expand=True, pady=10, padx=(0,10))

        # Custom Message Input
        Label(self.right_side_frame, text="Nội dung tin nhắn (để trống nếu dùng mặc định):", 
                 font=FONT_NORMAL, bg=BG_COLOR, fg=PRIMARY_TEXT_COLOR) \
            .pack(pady=(10,5), anchor="w")
        self.message_text = Text(self.right_side_frame, height=3, font=FONT_NORMAL, bd=2, relief="groove", bg="white", fg="black", wrap="word")
        self.message_text.pack(fill="x", pady=5)
        self.message_text.insert("1.0", EMAIL_CONFIG["DEFAULT_ATTENDANCE_MESSAGE"]) # Default message
        self.message_text.bind("<FocusIn>", self._clear_message_placeholder)
        self.message_text.bind("<FocusOut>", self._add_message_placeholder)


        # Spin Button
        self.spin_icon = self.load_icon("spin_icon.png", 32)
        self.spin_button = Button(self.right_side_frame, text=" QUAY NGAY ", image=self.spin_icon, compound="left",
                                     command=self.start_spin, font=FONT_MEDIUM_TITLE, bg=ACCENT_COLOR, fg=PRIMARY_TEXT_COLOR,
                                     activebackground=ACCENT_COLOR, activeforeground=PRIMARY_TEXT_COLOR, 
                                     bd=0, relief="flat", padx=15, pady=10, cursor="hand2")
        self.spin_button.pack(pady=(20, 10), fill="x")

        # Rules/Info from original image (adapted to attendance app)
        Label(self.right_side_frame, text="* Mỗi lần quay chỉ chọn một thành viên duy nhất.\n* Thành viên đã được chọn sẽ không bị loại bỏ khỏi danh sách quay.",
                 font=FONT_SMALL, bg=BG_COLOR, fg=SECONDARY_TEXT_COLOR, justify="left", wraplength=350) \
            .pack(pady=5, anchor="w")

        # "No, I don't feel lucky" - as a visual placeholder
        Label(self.right_side_frame, text="Bỏ qua việc điểm danh hôm nay ✕",
                 font=FONT_SMALL, bg=BG_COLOR, fg="#90A4AE", cursor="hand2") \
            .pack(pady=(10,0), anchor="e")

        # --- Name Management Section (now inside right_side_frame) ---
        name_management_frame = Frame(self.right_side_frame, bg=BG_COLOR, padx=0, pady=10) # Removed outer padding
        name_management_frame.pack(fill="x", pady=(20,0)) # Added top padding to separate from above controls

        Label(name_management_frame, text="Quản lý danh sách thành viên:", font=FONT_MEDIUM_TITLE, bg=BG_COLOR, fg=PRIMARY_TEXT_COLOR) \
            .pack(anchor="w", pady=(0, 5))

        # Input to add new name
        input_name_frame = Frame(name_management_frame, bg=BG_COLOR)
        input_name_frame.pack(fill="x", pady=5)
        self.name_entry = Entry(input_name_frame, width=30, font=FONT_NORMAL, bd=2, relief="groove", bg="white", fg="black")
        self.name_entry.pack(side="left", expand=True, fill="x", padx=(0, 10))
        self.name_entry.bind("<Return>", lambda event: self.add_name())

        self.add_icon = self.load_icon("add_icon.png", 24)
        add_button = Button(input_name_frame, text=" Thêm", image=self.add_icon, compound="left",
                                command=self.add_name, font=FONT_NORMAL, bg=BUTTON_BG_NORMAL, fg=BUTTON_FG_NORMAL, 
                                activebackground=BUTTON_BG_NORMAL, activeforeground=BUTTON_FG_NORMAL, 
                                bd=0, relief="flat", padx=10, pady=5, cursor="hand2")
        add_button.pack(side="left")

        # Listbox for current names
        list_frame = Frame(name_management_frame, bg=BG_COLOR)
        list_frame.pack(fill="both", expand=True, pady=5)

        # Create a frame to contain the listbox and its scrollbar
        listbox_container = Frame(list_frame, bg=BG_COLOR)
        listbox_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        self.name_listbox = Listbox(listbox_container, height=5, font=FONT_NORMAL, bd=2, relief="sunken", 
                                    selectmode="single", bg="white", fg="black", selectbackground=ACCENT_COLOR, 
                                    selectforeground="black")
        self.name_listbox.pack(side="left", fill="both", expand=True)
        
        scrollbar = Scrollbar(listbox_container, command=self.name_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.name_listbox.config(yscrollcommand=scrollbar.set)

        # Delete and Reset Buttons
        action_buttons_frame = Frame(list_frame, bg=BG_COLOR)
        action_buttons_frame.pack(side="left", fill="y")

        self.delete_icon = self.load_icon("delete_icon.png", 24)
        delete_button = Button(action_buttons_frame, text=" Xóa", image=self.delete_icon, compound="left",
                                  command=self.delete_selected_name, font=FONT_NORMAL, bg=DANGER_COLOR, fg="white",
                                  activebackground=DANGER_COLOR, activeforeground="white", 
                                  bd=0, relief="flat", padx=10, pady=5, cursor="hand2")
        delete_button.pack(pady=(0, 5), fill="x")

        self.reset_icon = self.load_icon("reset_icon.png", 24)
        reset_button = Button(action_buttons_frame, text=" Reset", image=self.reset_icon, compound="left",
                                  command=self.reset_list, font=FONT_NORMAL, bg=BUTTON_BG_NORMAL, fg=BUTTON_FG_NORMAL,
                                  activebackground=BUTTON_BG_NORMAL, activeforeground=BUTTON_FG_NORMAL, 
                                  bd=0, relief="flat", padx=10, pady=5, cursor="hand2")
        reset_button.pack(pady=(5, 0), fill="x")

        # Initial UI updates
        self.update_name_listbox()
        self.check_spin_button_state()

        # Handle window closing protocol
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def _clear_placeholder(self, event):
        if self.email_entry.get() == "Nhập email hợp lệ":
            self.email_entry.delete(0, "end")
            self.email_entry.config(fg="black")

    def _add_placeholder(self, event):
        if not self.email_entry.get():
            self.email_entry.insert(0, "Nhập email hợp lệ")
            self.email_entry.config(fg="grey")

    def _clear_message_placeholder(self, event):
        if self.message_text.get("1.0", "end").strip() == EMAIL_CONFIG["DEFAULT_ATTENDANCE_MESSAGE"]:
            self.message_text.delete("1.0", "end")
            self.message_text.config(fg="black")

    def _add_message_placeholder(self, event):
        if not self.message_text.get("1.0", "end").strip():
            self.message_text.insert("1.0", EMAIL_CONFIG["DEFAULT_ATTENDANCE_MESSAGE"])
            self.message_text.config(fg="grey")

    def load_icon(self, icon_name, size):
        """Loads and returns a PhotoImage object for an icon using Pillow."""
        icon_path = os.path.join(ICON_DIR, icon_name)
        try:
            original_image = Image.open(icon_path)
            resized_image = original_image.resize((size, size), Image.Resampling.LANCZOS)
            tk_image = ImageTk.PhotoImage(resized_image)
            return tk_image
        except FileNotFoundError:
            print(f"Warning: Icon file not found: {icon_name}")
            return None # Return None if not found
        except Exception as e:
            print(f"Warning: Could not load/process icon '{icon_name}': {e}")
            return None

    def load_names_from_file(self):
        """Loads names from the text file."""
        if os.path.exists(NAMES_FILE):
            with open(NAMES_FILE, "r", encoding="utf-8") as f:
                names = [line.strip() for line in f if line.strip()]
                self.names_original = sorted(list(set(names))) # Remove duplicates, sort
                self.names_current_spin = list(self.names_original) # Copy for current spin session
        else:
            self.names_original = []
            self.names_current_spin = []

    def save_names_to_file(self):
        """Saves the original list of names to the text file."""
        try:
            with open(NAMES_FILE, "w", encoding="utf-8") as f:
                for name in self.names_original:
                    f.write(name + "\n")
        except IOError as e:
            print(f"Error saving names to file: {e}")

    def update_name_listbox(self):
        """Updates the Listbox display with current names."""

        self.name_listbox.delete(0, "end")
        for name in self.names_original:
            self.name_listbox.insert("end", name)
        # Also update the names list in the SpinnerCanvas
        # For continuous play, names_current_spin is always a copy of names_original
        self.wheel_canvas.names = list(self.names_original) 
        self.wheel_canvas.draw_wheel()

    def add_name(self):
        """Adds a new name from the entry field to the list."""
        name = self.name_entry.get().strip()
        if name and name not in self.names_original:
            self.names_original.append(name)
            self.names_original.sort()
            self.names_current_spin = list(self.names_original) # Reset current spin list to include new name
            self.update_name_listbox()
            self.name_entry.delete(0, "end")
            self.save_names_to_file()
            self.check_spin_button_state()
        elif name in self.names_original:
            messagebox.showwarning("Trùng tên", f"Tên '{name}' đã có trong danh sách.", parent=self.master)
        elif not name:
            messagebox.showwarning("Không hợp lệ", "Vui lòng nhập tên thành viên.", parent=self.master)

    def delete_selected_name(self):
        """Deletes the selected name from the list."""
        selected_indices = self.name_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Chọn tên", "Vui lòng chọn một tên để xóa.", parent=self.master)
            return

        index = selected_indices[0]
        name_to_delete = self.name_listbox.get(index)

        if messagebox.askyesno("Xác nhận xóa", f"Bạn có chắc chắn muốn xóa '{name_to_delete}'?", parent=self.master):
            self.names_original.pop(self.names_original.index(name_to_delete))
            self.names_current_spin = list(self.names_original) # Reset current spin list after deletion
            self.update_name_listbox()
            self.save_names_to_file()
            self.check_spin_button_state()
            self.wheel_canvas.draw_wheel() # Redraw wheel with updated names

    def reset_list(self):
        """Resets the current spin list, allowing all original names to be chosen again."""
        if messagebox.askyesno("Xác nhận Reset", "Bạn có muốn đưa tất cả thành viên về trạng thái chưa điểm danh không?", parent=self.master):
            self.names_current_spin = list(self.names_original)
            self.check_spin_button_state()
            self.wheel_canvas.draw_wheel() # Redraw wheel with all names
            messagebox.showinfo("Reset Thành Công", "Danh sách đã được Reset! Toàn bộ thành viên có thể được chọn lại.", parent=self.master)

    def check_spin_button_state(self):
        """Checks and updates the state of the spin button."""
        # Remove any previous info text on the canvas
        self.wheel_canvas.delete("info_text")

        if not self.names_original: # If original list is empty, no names to spin
            self.spin_button.config(state=DISABLED, bg=BUTTON_BG_DISABLED, cursor="arrow")
            self.wheel_canvas.create_text(self.wheel_canvas.center_x, self.wheel_canvas.center_y + self.wheel_canvas.radius * 0.3,
                                           text="Vui lòng thêm thành viên!", font=FONT_NORMAL, fill="grey", tag="info_text")
        elif self.spinning: # If currently spinning
            self.spin_button.config(state=DISABLED, bg=BUTTON_BG_DISABLED, cursor="arrow")
        else: # Ready to spin (names_original is not empty)
            self.spin_button.config(state=NORMAL, bg=ACCENT_COLOR, cursor="hand2")
        

    def start_spin(self):
        """Starts the spinning process."""
        if self.spinning:
            return

        if not self.names_original: # Check original list, as current_spin is always full copy
            messagebox.showinfo("Hết tên", "Vui lòng thêm thành viên vào danh sách để quay.", parent=self.master)
            self.check_spin_button_state()
            return
        
        self.spinning = True
        self.spin_button.config(state=DISABLED, bg=BUTTON_BG_DISABLED)

        # Determine the winner randomly from the current available names (which is always full list now)
        winner = random.choice(self.names_original) # Use names_original for selection
        
        # Start the animation in the SpinnerCanvas
        self.wheel_canvas.start_spin(winner)

    def spin_finished(self, winner_name):
        """Callback function called by SpinnerCanvas when the spin animation finishes."""
        # No longer remove winner from names_current_spin for continuous play
        
        self.spinning = False
        # Add a small delay before re-enabling the button to ensure UI updates are complete
        self.master.after(200, self.check_spin_button_state) 
        self.update_name_listbox() # Update listbox (though it won't change much now)

        # Get custom message from text field
        custom_message = self.message_text.get("1.0", "end").strip()
        if custom_message == EMAIL_CONFIG["DEFAULT_ATTENDANCE_MESSAGE"]:
            custom_message = "" # Treat default placeholder as empty if not modified

        # Attempt to send email if enabled
        if EMAIL_CONFIG["ENABLE_EMAIL_SENDING"]:
            recipient_email = self.email_entry.get().strip()
            if recipient_email and "@" in recipient_email and "." in recipient_email and recipient_email != "Nhập email hợp lệ":
                print(f"Preparing to send email to: {recipient_email}")
                # Send email in a separate thread to avoid freezing the GUI
                email_thread = threading.Thread(target=self._send_attendance_email_threaded, 
                                              args=(recipient_email, winner_name, custom_message))
                email_thread.daemon = True  # Make thread daemon so it doesn't block application exit
                email_thread.start()
                print(f"Email thread started for: {recipient_email}")
            else:
                print("Invalid email address entered")
                messagebox.showwarning("Email không hợp lệ", "Vui lòng nhập một địa chỉ email hợp lệ để nhận thông báo.", parent=self.master)

    def _send_attendance_email_threaded(self, recipient_email, winner_name, custom_message):
        """Wrapper for sending email to be called in a separate thread."""
        try:
            print(f"Email thread running for: {recipient_email}")
            self._send_attendance_email(recipient_email, winner_name, custom_message)
            print(f"Email sent successfully to: {recipient_email}")
            # Use after method to safely update GUI from a non-main thread
            self.master.after(0, lambda: messagebox.showinfo("Gửi Email", 
                                                           f"Thông báo điểm danh đã được gửi tới {recipient_email}!", 
                                                           parent=self.master))
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            # Use after method to safely update GUI from a non-main thread
            self.master.after(0, lambda: messagebox.showerror("Lỗi Gửi Email", 
                                                            f"Không thể gửi email tới {recipient_email}.\nLỗi: {e}\n"
                                                            f"Vui lòng kiểm tra cấu hình email và kết nối mạng.", 
                                                            parent=self.master))

    def _send_attendance_email(self, recipient_email, winner_name, custom_message=""):
        """Sends an attendance notification email."""
        sender_email = EMAIL_CONFIG["SENDER_EMAIL"]
        sender_password = EMAIL_CONFIG["SENDER_PASSWORD"]
        smtp_server = EMAIL_CONFIG["SMTP_SERVER"]
        smtp_port = EMAIL_CONFIG["SMTP_PORT"]

        print(f"Sending email to {recipient_email} via {smtp_server}:{smtp_port}")
        print(f"Using credentials: {sender_email}")
        
        # Determine message content
        message_content = custom_message if custom_message else EMAIL_CONFIG["DEFAULT_ATTENDANCE_MESSAGE"]
        
        msg = MIMEMultipart("alternative")
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = f"Thông báo Điểm Danh Vòng Quay May Mắn - {winner_name} đã được chọn!"

        # Email body (plain text and HTML)
        text_body = f"""
        Xin chào,

        Đây là thông báo từ ứng dụng Vòng Quay May Mắn Điểm Danh.

        Thành viên được chọn trong lần quay gần nhất là: {winner_name.upper()}

        Tin nhắn: {message_content}

        Chúc một ngày tốt lành!

        Trân trọng,
        Ứng dụng Vòng Quay May Mắn
        """
        html_body = f"""
        <html>
            <body>
                <p>Xin chào,</p>
                <p>Đây là thông báo từ ứng dụng <b>Vòng Quay May Mắn Điểm Danh</b>.</p>
                <p>Thành viên được chọn trong lần quay gần nhất là:</p>
                <h2 style="color: #33BBC5;"><b>🎉 {winner_name.upper()} 🎉</b></h2>
                <p>Tin nhắn: <i>{message_content}</i></p>
                <p>Chúc một ngày tốt lành!</p>
                <p>Trân trọng,<br>
                Ứng dụng Vòng Quay May Mắn</p>
            </body>
        </html>
        """

        part1 = MIMEText(text_body, "plain", "utf-8")
        part2 = MIMEText(html_body, "html", "utf-8")

        msg.attach(part1)
        msg.attach(part2)

        try:
            print("Establishing connection to SMTP server...")
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                print("Starting TLS...")
                server.starttls() # Secure the connection
                print("Logging in...")
                server.login(sender_email, sender_password)
                print("Sending email...")
                server.sendmail(sender_email, recipient_email, msg.as_string())
                print("Email sent successfully!")
        except smtplib.SMTPAuthenticationError as e:
            print(f"SMTP Authentication Error: {e}")
            raise Exception("Lỗi xác thực SMTP. Vui lòng kiểm tra email và mật khẩu ứng dụng (app password) của bạn.")
        except smtplib.SMTPConnectError as e:
            print(f"SMTP Connection Error: {e}")
            raise Exception("Không thể kết nối tới máy chủ SMTP. Vui lòng kiểm tra địa chỉ máy chủ và cổng.")
        except Exception as e:
            print(f"Unexpected error during email sending: {e}")
            raise Exception(f"Lỗi không xác định khi gửi email: {e}")

    def on_closing(self):
        """Function called when the user closes the window."""
        if messagebox.askokcancel("Thoát Ứng Dụng", "Bạn có muốn thoát ứng dụng không? Các thay đổi sẽ được lưu.", parent=self.master):
            self.save_names_to_file()
            self.master.destroy()

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # Create icons directory if it doesn't exist
    if not os.path.exists(ICON_DIR):
        os.makedirs(ICON_DIR)
        messagebox.showinfo("Thông báo", 
                            "Thư mục 'icons' đã được tạo. Vui lòng đặt các file ảnh (png/gif) của icon "
                            "và logo (woay_logo.png) vào thư mục này để hiển thị đầy đủ các nút bấm "
                            "và vòng quay.", icon="info", parent=Tk().withdraw()) # Use a dummy Tk for message

    root = Tk()
    app = LuckySpinApp(root)
    root.mainloop()