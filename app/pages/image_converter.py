import io
import zipfile
import streamlit as st
from PIL import Image

from pillow_heif import register_heif_opener

from utils.image_utils import limit_image_size
from utils.nav import top_nav

top_nav()

register_heif_opener()

st.set_page_config(page_title="Image Converter", page_icon="🔄")

st.title("🔄 Image Converter")
st.caption("Upload images → choose output format → click Convert → download.")
st.divider()

FORMAT_EXTS = {
    "JPEG": {"jpg", "jpeg"},
    "PNG": {"png"},
    "WEBP": {"webp"},
}

uploaded_files = st.file_uploader(
    "Upload one or more images",
    type=[
        "heic",
        "heif",
        "jpg",
        "jpeg",
        "png",
        "webp",
        "gif",
        "bmp",
        "tif",
        "tiff",
        "ico",
    ],
    accept_multiple_files=True,
)

if not uploaded_files:
    st.info("Upload images to convert.")
    st.stop()

target_format = st.selectbox("Convert to", ["JPEG", "PNG", "WEBP"], index=0)

MAX_SIDE = 2500


def already_in_target_format(filename: str, target_fmt: str) -> bool:
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in FORMAT_EXTS[target_fmt]


def ext_for(fmt: str) -> str:
    return {"JPEG": "jpg", "PNG": "png", "WEBP": "webp"}[fmt]


def mime_for(ext: str) -> str:
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
    }.get(ext, "application/octet-stream")


def convert_image_bytes(raw: bytes, fmt: str) -> bytes:
    """
    Decode with Pillow -> re-encode to fmt.
    Notes:
      - JPEG does not support transparency, so we convert to RGB.
      - Animated GIFs are not preserved (first frame only).
    """
    img = Image.open(io.BytesIO(raw))

    try:
        if getattr(img, "is_animated", False):
            img.seek(0)
    except Exception:
        pass

    try:
        tmp = img.convert("RGBA")
        tmp = limit_image_size(tmp, max_side=MAX_SIDE)
        img = tmp
    except Exception:
        pass

    if fmt == "JPEG":
        img_rgb = img.convert("RGB")
        buf = io.BytesIO()
        img_rgb.save(buf, format="JPEG", quality=85, optimize=True, progressive=True)
        return buf.getvalue()

    if fmt == "PNG":
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    if fmt == "WEBP":
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA")
        buf = io.BytesIO()
        img.save(buf, format="WEBP", quality=85, method=6)
        return buf.getvalue()

    raise ValueError(f"Unsupported target format: {fmt}")


def clear_outputs():
    for k in [
        "single_out_bytes",
        "single_out_name",
        "zip_bytes",
        "zip_name",
        "summary_msg",
    ]:
        st.session_state.pop(k, None)


col_a, col_b = st.columns([1, 1])
with col_a:
    convert_clicked = st.button("Convert", use_container_width=True)
with col_b:
    if st.button("Reset", use_container_width=True):
        st.session_state.clear()
        st.rerun()

single_mode = len(uploaded_files) == 1

if convert_clicked:
    clear_outputs()

    converted = 0
    skipped = 0
    out_ext = ext_for(target_format)

    try:
        if single_mode:
            f = uploaded_files[0]

            if already_in_target_format(f.name, target_format):
                st.session_state["summary_msg"] = (
                    f"Already {target_format}: {f.name} (no conversion needed)"
                )
            else:
                raw = f.read()
                base = f.name.rsplit(".", 1)[0]
                out_name = f"{base}.{out_ext}"

                with st.spinner("Converting..."):
                    out_bytes = convert_image_bytes(raw, target_format)

                st.session_state["single_out_bytes"] = out_bytes
                st.session_state["single_out_name"] = out_name
                st.session_state["summary_msg"] = (
                    f"Converted 1 file to {target_format}: {out_name}"
                )

        else:
            zip_buffer = io.BytesIO()
            with st.spinner("Converting files..."):
                with zipfile.ZipFile(
                    zip_buffer, "w", compression=zipfile.ZIP_DEFLATED
                ) as zf:
                    for f in uploaded_files:
                        if already_in_target_format(f.name, target_format):
                            skipped += 1
                            continue

                        raw = f.read()
                        base = f.name.rsplit(".", 1)[0]
                        out_name = f"{base}.{out_ext}"

                        out_bytes = convert_image_bytes(raw, target_format)
                        zf.writestr(out_name, out_bytes)
                        converted += 1

            if converted > 0:
                st.session_state["zip_bytes"] = zip_buffer.getvalue()
                st.session_state["zip_name"] = f"converted_{target_format.lower()}.zip"
                st.session_state["summary_msg"] = (
                    f"Converted: {converted} • Skipped (already {target_format}): {skipped}"
                )
            else:
                st.session_state["summary_msg"] = (
                    f"Nothing to convert (all files were already {target_format})."
                )

    except Exception as e:
        st.error("Conversion failed.")
        st.exception(e)

if "summary_msg" in st.session_state:
    st.info(st.session_state["summary_msg"])

if "single_out_bytes" in st.session_state and "single_out_name" in st.session_state:
    out_name = st.session_state["single_out_name"]
    out_ext2 = out_name.rsplit(".", 1)[-1].lower()
    st.download_button(
        f"Download {out_name}",
        data=st.session_state["single_out_bytes"],
        file_name=out_name,
        mime=mime_for(out_ext2),
        use_container_width=True,
    )

if "zip_bytes" in st.session_state and "zip_name" in st.session_state:
    st.download_button(
        "Download ZIP",
        data=st.session_state["zip_bytes"],
        file_name=st.session_state["zip_name"],
        mime="application/zip",
        use_container_width=True,
    )
