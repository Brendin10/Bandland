"""Streamlit dashboard for generating and previewing Bandland songs."""

from __future__ import annotations

import random
from pathlib import Path

import streamlit as st

from music.generate_songs import generate_song
from music.theory import SONGS

OUTPUT_DIR = Path("songs/.generated")
STEM_LABELS = {
    "drums": "Drums",
    "bass": "Bass",
    "chords": "Chords / Pads",
    "lead": "Lead Melody",
}


def _file_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _render_song_info(metadata: dict) -> None:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Title", metadata["title"])
    col2.metric("Key", metadata["key"])
    col3.metric("BPM", metadata["bpm"])
    col4.metric("Length", f"{int(metadata['duration_seconds'])}s")
    st.caption(metadata["vibe"])


def _render_full_mix(result: dict, metadata: dict) -> None:
    st.subheader("Full Song")
    st.audio(result["mix_path"], format="audio/wav")
    mix_name = f"{metadata['slug']}_full_mix.wav"
    st.download_button(
        label="Download full mix",
        data=_file_bytes(result["mix_path"]),
        file_name=mix_name,
        mime="audio/wav",
        use_container_width=True,
    )


def _render_stems(result: dict, metadata: dict) -> None:
    st.subheader("Stems")
    st.caption("Individual tracks for Ableton Live — drag into your session or download below.")

    for stem in metadata["stems"]:
        stem_path = result["stems"][stem]
        label = STEM_LABELS.get(stem, stem.title())

        with st.container(border=True):
            st.markdown(f"**{label}**")
            st.audio(stem_path, format="audio/wav")
            st.download_button(
                label=f"Download {label.lower()}",
                data=_file_bytes(stem_path),
                file_name=f"{metadata['slug']}_{stem}.wav",
                mime="audio/wav",
                key=f"download_{metadata['slug']}_{stem}",
                use_container_width=True,
            )


def main() -> None:
    st.set_page_config(
        page_title="Bandland Song Studio",
        page_icon="🎵",
        layout="centered",
    )

    st.title("Bandland Song Studio")
    st.write(
        "Generate a 60-second instrumental track with stems ready for Ableton Live. "
        "Each song follows: **Hook → Chorus → Verse → Hook → Chorus → Outro**."
    )

    if st.button("Generate Song", type="primary", use_container_width=True):
        song = random.choice(SONGS)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        with st.spinner(f"Composing **{song.title}**..."):
            try:
                result = generate_song(song, str(OUTPUT_DIR))
                st.session_state["generation"] = result
            except FileNotFoundError as exc:
                st.error(
                    "SoundFont not found. Install system audio deps:\n\n"
                    "`sudo apt-get install fluidsynth fluid-soundfont-gm`"
                )
                st.caption(str(exc))
            except Exception as exc:
                st.error(f"Generation failed: {exc}")

    if "generation" not in st.session_state:
        st.info("Hit **Generate Song** to create a track.")
        return

    result = st.session_state["generation"]
    metadata = result["metadata"]

    st.divider()
    _render_song_info(metadata)
    st.divider()
    _render_full_mix(result, metadata)
    st.divider()
    _render_stems(result, metadata)

    with st.expander("Arrangement & section markers"):
        st.write(" → ".join(metadata["arrangement"]))
        for section in metadata["sections"]:
            st.write(
                f"- **{section['name'].title()}** — bar {section['start_bar']}, "
                f"{section['duration_seconds']}s"
            )

    st.divider()
    st.download_button(
        label="Download MIDI",
        data=_file_bytes(result["midi_path"]),
        file_name=f"{metadata['slug']}.mid",
        mime="audio/midi",
        use_container_width=True,
    )


if __name__ == "__main__":
    main()
