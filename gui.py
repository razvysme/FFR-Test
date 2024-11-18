import tkinter as tk
from PIL import Image, ImageTk

def load_sprite(path, scale=0.05):
    sprite_image = Image.open(path).convert("RGBA")
    width, height = sprite_image.size
    new_size = (int(width * scale), int(height * scale))
    return ImageTk.PhotoImage(sprite_image.resize(new_size, Image.LANCZOS))

def initialize_gui(sensors):
    """Initialize the GUI and return the root, canvas, and sprite IDs."""
    global canvas, original_image, image_width, image_height, aspect_ratio

    # Load the background image
    original_image = Image.open("Sprites/palm.png").convert("RGBA")
    image_width, image_height = original_image.size
    aspect_ratio = image_width / image_height

    root = tk.Tk()
    root.geometry(f"{image_width}x{image_height}")
    root.overrideredirect(1)  # Borderless window
    root.attributes('-transparentcolor', 'white')  # Make white transparent
    root.config(bg='white')  # Background to match transparent color
    root.minsize(100, int(100 / aspect_ratio))  # Prevent collapse

    # Canvas setup
    canvas = tk.Canvas(root, width=image_width, height=image_height, bg="white", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Initial background image
    tk_image = ImageTk.PhotoImage(original_image)
    canvas.create_image(0, 0, anchor="nw", image=tk_image, tags="background")
    canvas.image = tk_image  # Prevent GC

    # Sprite positions
    positions = {
        "pinky": [17, 92],
        "ring": [62, 44],
        "middle": [101, 28],
        "index": [151, 55],
        "thumb": [206, 160],
        "upper_palm": [66, 173],
        "lower_palm": [138, 262]
    }

    canvas.sprite_images = []  # Initialize to prevent garbage collection

    # Add sprites and initialize sprite_images
    sprite_ids = []
    for pos in positions.values():
        sprite = load_sprite("Sprites/fingerprint_red.png")  # Default red
        sprite_id = canvas.create_image(pos[0], pos[1], anchor="center", image=sprite)
        sprite_ids.append(sprite_id)
        canvas.sprite_images.append(sprite)  # Add sprite to prevent GC

    # Add resizing and drag functionality
    add_resize_and_drag(root, canvas)

    # Ensure the GUI stays on top
    def keep_on_top():
        root.attributes('-topmost', True)  # Ensure GUI stays on top
        root.after(100, keep_on_top)  # Reapply every 100ms

    keep_on_top()  # Start the topmost functionality

    return root, sprite_ids

def update_sprites(sensors, sprite_ids):
    """Update the sprites based on sensor values."""
    sprite_paths = {
        0: "Sprites/fingerprint_red.png",
        1: "Sprites/fingerprint_green.png"
    }

    for i, sensor_value in enumerate(sensors):
        sprite_path = sprite_paths[sensor_value]
        new_sprite = load_sprite(sprite_path)

        # Update the sprite on the canvas
        canvas.itemconfig(sprite_ids[i], image=new_sprite)

        # Ensure sprite_images list has enough entries
        if len(canvas.sprite_images) <= i:
            canvas.sprite_images.append(new_sprite)
        else:
            canvas.sprite_images[i] = new_sprite  # Replace old sprite image

def add_resize_and_drag(root, canvas):
    """Add window resizing and dragging capabilities."""

    def resize_window(new_width):
        new_width = int(new_width)
        new_height = int(new_width / aspect_ratio)

        resized_image = original_image.resize((new_width, new_height), Image.LANCZOS)
        tk_image = ImageTk.PhotoImage(resized_image)

        canvas.delete("background")
        canvas.create_image(0, 0, anchor="nw", image=tk_image, tags="background")
        canvas.image = tk_image

        root.geometry(f"{new_width}x{new_height}")

    def start_move(event):
        root.x_offset = event.x
        root.y_offset = event.y

    def move_window(event):
        x = root.winfo_pointerx() - root.x_offset
        y = root.winfo_pointery() - root.y_offset
        root.geometry(f"+{x}+{y}")

    def start_resize(event):
        root.resize_x = event.x
        root.resize_y = event.y

    def resize_drag(event):
        delta_x = event.x - root.resize_x
        new_width = root.winfo_width() + delta_x
        if new_width >= 100:  # Prevent collapse below minimum size
            resize_window(new_width)

    # Bind drag for window move
    canvas.bind("<Button-1>", start_move)
    canvas.bind("<B1-Motion>", move_window)

    # Resize handle in bottom right
    resize_handle = tk.Frame(root, cursor="bottom_right_corner", bg="grey", width=10, height=10)
    resize_handle.place(relx=1, rely=1, anchor="se")
    resize_handle.bind("<Button-1>", start_resize)
    resize_handle.bind("<B1-Motion>", resize_drag)
