import io
import streamlit as st
from rembg import remove
import zipfile

from utils.image_utils import limit_image_size, pil_to_png_bytes, bytes_to_pil
from utils.nav import top_nav

top_nav()

st.set_page_config(page_title="Background Remover", page_icon="🪄")

st.title("Background Remover")
st.caption("Upload images → background removed → download PNGs (or ZIP).")
st.divider()


DEFAULT_ALPHA_MATTING = True
DEFAULT_FG = 240
DEFAULT_BG = 10
DEFAULT_ERODE = 10


@st.cache_data(show_spinner=False)
def remove_bg(input_bytes: bytes) -> bytes:
    return remove(
        input_bytes,
        alpha_matting=DEFAULT_ALPHA_MATTING,
        alpha_matting_foreground_threshold=DEFAULT_FG,
        alpha_matting_background_threshold=DEFAULT_BG,
        alpha_matting_erode_size=DEFAULT_ERODE,
    )


uploaded_files = st.file_uploader(
    "Upload one or more images", type=["png", "jpg", "jpeg"], accept_multiple_files=True
)


if not uploaded_files:
    st.info("Choose one or more PNG/JPG images to get started.")
    st.stop()

if st.button("Reset"):
    st.session_state.clear()
    st.rerun()

zip_buffer = io.BytesIO()
zip_count = 0

with zipfile.ZipFile(zip_buffer, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for uploaded in uploaded_files:
        try:
            raw = uploaded.read()
            original = bytes_to_pil(raw)

            original = limit_image_size(original)

            input_bytes = pil_to_png_bytes(original)

            with st.spinner(f"Removing background: {uploaded.name}"):
                output_bytes = remove_bg(input_bytes)

            result = bytes_to_pil(output_bytes)
            col1, col2 = st.columns(2)
            with col1:
                st.image(original, caption="Original", width="stretch")
            with col2:
                st.image(result, caption="Background removed", width="stretch")

            base = uploaded.name.rsplit(".", 1)[0]
            out_name = f"{base}_no-bg.png"

            zf.writestr(out_name, output_bytes)
            zip_count += 1

            st.download_button(
                f"Download {out_name}",
                data=output_bytes,
                file_name="no-bg.png",
                mime="image/png",
                width="stretch",
                key=f"dl_{uploaded.name}",
            )

            st.divider()

        except Exception as e:
            st.error(f"Failed on: {uploaded.name}")
            st.exception(e)
            st.divider()

zip_bytes = zip_buffer.getvalue()

if zip_count > 0:
    st.download_button(
        f"Download all ({zip_count}) as ZIP",
        data=zip_bytes,
        file_name="no-bg.png",
        mime="image/png",
        width="stretch",
    )
