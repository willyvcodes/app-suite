import streamlit as st


def top_nav():
    with st.container():
        c1, c2, c3 = st.columns(
            [
                1,
                2,
                2,
            ]
        )

        with c1:
            st.page_link("app.py", label="Home", icon="🧰")

        with c2:
            st.page_link(
                "pages/background_remover.py", label="Background Remover", icon="🪄"
            )

        with c3:
            st.page_link("pages/image_converter.py", label="Image Converter", icon="🔄")

    st.divider()
