import io
from PIL import Image

MAX_SIDE_DEFAULT = 2000


def limit_image_size(img: Image.Image, max_side: int = MAX_SIDE_DEFAULT) -> Image.Image:
    """Resize image so its longest side is <= max_side, preserving aspect ratio"""
    w, h = img.size
    scale = max(w, h) / max_side
    if scale > 1:
        img = img.resize((int(w / scale), int(h / scale)))
    return img


def pil_to_png_bytes(img: Image.Image) -> bytes:
    """Convert a PIL image to PNG bytes"""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def bytes_to_pil(image_bytes: bytes) -> Image.Image:
    """Convert image bytes to a PIL RGBA image"""
    return Image.open(io.BytesIO(image_bytes)).convert("RGBA")
