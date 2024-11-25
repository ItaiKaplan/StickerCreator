import base64
import time
from io import BytesIO
from moviepy import *
from rembg import remove
from PIL import Image, ImageFilter, ImageOps

def video_to_sticker_base64(video_path, frame_time_ms, output_sticker_path):
    sticker_path = video_to_sticker(video_path, frame_time_ms, output_sticker_path)
    sticker_base64 = webp_to_base64(sticker_path)
    return sticker_base64

def video_to_sticker(video_path, frame_time_ms, output_sticker_path):
    try:
        creation_timestamp = int(time.time() * 1000)
        frame_image_path = extract_full_frame_image(frame_time_ms, video_path, creation_timestamp)
        segmented_object_image_path = segment_object_to_image(frame_image_path, creation_timestamp)
        segmented_object_image = enhance_image_edges(segmented_object_image_path)
        square_image = resize_image_for_sticker(segmented_object_image)

        # Save the final sticker
        square_image.save(output_sticker_path, format="WEBP", lossless=True)
        print(f"Sticker saved at {output_sticker_path}")
        return output_sticker_path

    except Exception as e:
        print(f"Error: {e}")

def extract_full_frame_image(frame_time_ms, video_path, creation_timestamp):
    # Step 1: Extract frame from video
    clip = VideoFileClip(video_path)
    frame_time_s = frame_time_ms / 1000  # Convert ms to seconds
    frame = clip.get_frame(frame_time_s)
    frame_image_path = f"Images/frame_{creation_timestamp}.png"
    # Save frame as an image
    frame_image = Image.fromarray(frame)
    frame_image.save(frame_image_path)
    return frame_image_path

def segment_object_to_image(frame_image_path, creation_timestamp):
    # Step 2: Remove background and isolate the main object
    with open(frame_image_path, "rb") as input_file:
        input_image = input_file.read()
        output_image = remove(input_image, alpha_matting=True)
    object_image_path = f"Images/segmented_object_{creation_timestamp}.png"
    with open(object_image_path, "wb") as output_file:
        output_file.write(output_image)
    return object_image_path

def enhance_image_edges(object_image_path):
    # Step 3: Enhance edges and add an outline
    object_image = Image.open(object_image_path).convert("RGBA")
    bbox = object_image.getbbox()  # Get the bounding box of the non-transparent area
    if bbox:
        object_image = object_image.crop(bbox)  # Crop the image to the bounding box
    outline_image = object_image.filter(ImageFilter.FIND_EDGES)
    # Match sizes by resizing outline_image to the same size as object_image
    outline_image = ImageOps.expand(outline_image, border=10, fill=(255, 255, 255, 0))
    outline_image = outline_image.resize(object_image.size, Image.Resampling.LANCZOS)
    # Combine the images
    object_image = Image.alpha_composite(outline_image, object_image)
    return object_image

def resize_image_for_sticker(object_image):
    # Step 4: Resize for WhatsApp sticker format
    size = 1024
    square_image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    # Dynamically resize the object to take up most of the sticker
    max_dimension = max(object_image.width, object_image.height)
    scaling_factor = size / max_dimension * 1.2  # Use 90% of the sticker area
    new_width = int(object_image.width * scaling_factor)
    new_height = int(object_image.height * scaling_factor)
    # Resize and center the object
    object_image = object_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    x_offset = (size - new_width) // 2
    y_offset = (size - new_height) // 2
    square_image.paste(object_image, (x_offset, y_offset), object_image)
    return square_image


def webp_to_base64(image_path):
    # Open the image file
    with Image.open(image_path) as image:
        # Convert the image to bytes
        buffered = BytesIO()
        image.save(buffered, format="WEBP")
        image_bytes = buffered.getvalue()

        # Encode the bytes to a base64 string
        image_base64 = base64.b64encode(image_bytes).decode("utf-8")

        return image_base64
