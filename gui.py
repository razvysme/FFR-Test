import tkinter as tk
from PIL import Image, ImageTk
import random

# Function to adjust the window size while maintaining the aspect ratio
def resize_window(new_width):
    new_width = int(new_width)
    new_height = int(new_width / aspect_ratio)
    
    # Resize the background image using LANCZOS resampling
    resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
    tk_image = ImageTk.PhotoImage(resized_image)
    
    # Update the canvas with the resized background image
    canvas.delete("background")  # Clear only the background
    canvas.create_image(0, 0, anchor="nw", image=tk_image, tags="background")
    canvas.image = tk_image  # Prevent garbage collection
    
    # Update the window's geometry
    root.geometry(f"{new_width}x{new_height}")

# Function to load and scale the sprite
def load_sprite(path, scale=0.05):
    sprite_image = Image.open(path).convert("RGBA")
    width, height = sprite_image.size
    new_size = (int(width * scale), int(height * scale))
    return ImageTk.PhotoImage(sprite_image.resize(new_size, Image.LANCZOS))

# Function to add sprites to the canvas
def add_sprite(position, sprite):
    x, y = position
    sprite_id = canvas.create_image(x, y, anchor="center", image=sprite, tags="sprite")
    canvas.sprite_images.append(sprite)  # Prevent garbage collection
    return sprite_id

# Function to update sprites based on the sensors array
def update_sprites():
    global sensors
    for i, sensor_value in enumerate(sensors):
        sprite_path = "Sprites/Fingerprint_green.png" if sensor_value else "Sprites/Fingerprint_red.png"
        new_sprite = load_sprite(sprite_path, scale=0.05)
        canvas.itemconfig(sprite_ids[i], image=new_sprite)
        canvas.sprite_images[i] = new_sprite  # Prevent garbage collection
    
    # Simulate sensor changes for testing
    sensors = [random.choice([0, 1]) for _ in range(len(sprite_ids))]
    
    # Schedule the next update
    root.after(500, update_sprites)  # Update every 500 ms

# Functions to enable window dragging
def start_move(event):
    root.x_offset = event.x
    root.y_offset = event.y

def move_window(event):
    x = root.winfo_pointerx() - root.x_offset
    y = root.winfo_pointery() - root.y_offset
    root.geometry(f"+{x}+{y}")

# Function to enable manual resizing
def start_resize(event):
    root.resize_x = event.x
    root.resize_y = event.y

def resize_drag(event):
    delta_x = event.x - root.resize_x
    new_width = root.winfo_width() + delta_x
    if new_width >= 100:  # Prevent collapsing below minimum width
        resize_window(new_width)

# Load the background image
original_image = Image.open("Sprites/palm.png").convert("RGBA")
image_width, image_height = original_image.size
aspect_ratio = image_width / image_height

# Create the main window
root = tk.Tk()
root.geometry(f"{image_width}x{image_height}")
root.overrideredirect(1)  # Borderless
root.attributes('-topmost', True)  # Always on top
root.attributes('-transparentcolor', 'white')  # Make white areas transparent
root.config(bg='white')  # Set the background to match transparentcolor
root.minsize(100, int(100 / aspect_ratio))  # Minimum size to avoid collapse

# Create a canvas to display the image and sprites
canvas = tk.Canvas(root, width=image_width, height=image_height, highlightthickness=0, bg="white")
canvas.pack(fill="both", expand=True)

# Display the initial background image
tk_image = ImageTk.PhotoImage(original_image)
canvas.create_image(0, 0, anchor="nw", image=tk_image, tags="background")
canvas.image = tk_image
canvas.sprite_images = []  # To prevent sprites from being garbage collected

# Touch positions
positions = {
    "pinky": [17, 92],
    "ring": [62, 44],
    "middle": [101, 28],
    "index": [151, 55],
    "thumb": [206, 160],
    "upper_palm": [128, 175],
    "lower_palm": [138, 262]
}

# Simulated sensors array
sensors = [0] * len(positions)  # Ensure sensors match the number of touch positions

# Add sprites and store their IDs
sprite_ids = []
for pos in positions.values():
    sprite_id = add_sprite(pos, load_sprite("Sprites/fingerprint_red.png", scale=0.05))
    sprite_ids.append(sprite_id)

# Add a manual resize handle
resize_handle = tk.Frame(root, cursor="bottom_right_corner", bg="grey", width=10, height=10)
resize_handle.place(relx=1, rely=1, anchor="se")

# Bind dragging functionality to canvas
canvas.bind("<Button-1>", start_move)  # Track initial click
canvas.bind("<B1-Motion>", move_window)  # Drag the window

# Bind resizing functionality to the resize handle
resize_handle.bind("<Button-1>", start_resize)  # Start resizing
resize_handle.bind("<B1-Motion>", resize_drag)  # Drag to resize

# Start the sprite update loop
update_sprites()

# Start the Tkinter event loop
root.mainloop()
