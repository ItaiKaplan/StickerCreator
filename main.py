import os
from moviepy import *
from rembg import remove
from PIL import Image, ImageFilter, ImageOps


def video_to_sticker(video_path, frame_time_ms, output_sticker_path):
    try:
        # Step 1: Extract frame from video
        clip = VideoFileClip(video_path)
        frame_time_s = frame_time_ms / 1000  # Convert ms to seconds
        frame = clip.get_frame(frame_time_s)
        frame_image_path = "frame_image.png"

        # Save frame as an image
        frame_image = Image.fromarray(frame)
        frame_image.save(frame_image_path)

        # Step 2: Remove background and isolate the main object
        with open(frame_image_path, "rb") as input_file:
            input_image = input_file.read()
            output_image = remove(input_image, alpha_matting=True)

        object_image_path = "object_image.png"
        with open(object_image_path, "wb") as output_file:
            output_file.write(output_image)

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

        # Save the final sticker
        square_image.save(output_sticker_path, format="WEBP", lossless=True)
        print(f"Sticker saved at {output_sticker_path}")

    except Exception as e:
        print(f"Error: {e}")


# Example usage
# input
video_path = "Videos/goodVideo.mp4"  # Replace with your video file path
frame_time_ms = 27800  # Extract the frame at 5 seconds (5000 ms)
# output
output_sticker_path = "Stickers/sticker1.webp"  # Path to save the sticker
video_to_sticker(video_path, frame_time_ms, output_sticker_path)
