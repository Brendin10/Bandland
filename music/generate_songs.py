"""CLI to generate all Bandland songs with stems."""

from __future__ import annotations

import argparse
import json
import os
import sys

from music.composer import write_song_midi
from music.renderer import render_song
from music.structures import BPM, SAMPLE_RATE, section_markers, total_duration_seconds
from music.theory import SONGS, SongDef


def build_metadata(song: SongDef) -> dict:
    return {
        "id": song.id,
        "title": song.title,
        "slug": song.slug,
        "key": f"{song.key_root} {song.key_mode}",
        "bpm": BPM,
        "vibe": song.vibe,
        "duration_seconds": total_duration_seconds(),
        "sample_rate": SAMPLE_RATE,
        "sections": section_markers(),
        "stems": ["drums", "bass", "chords", "lead"],
        "arrangement": [
            "Short Hook",
            "Chorus",
            "Verse",
            "Short Hook",
            "Chorus",
            "Short Outro",
        ],
    }


def generate_song(song: SongDef, output_root: str) -> str:
    folder_name = f"{song.id}_{song.slug}"
    song_dir = os.path.join(output_root, folder_name)
    os.makedirs(song_dir, exist_ok=True)

    midi_path = os.path.join(song_dir, f"{song.id}_{song.slug}.mid")
    write_song_midi(song, midi_path)

    render_song(midi_path, song_dir, f"{song.id}_{song.slug}")

    meta_path = os.path.join(song_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(build_metadata(song), f, indent=2)

    return song_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate Bandland songs with Ableton-ready stems."
    )
    parser.add_argument(
        "-o",
        "--output",
        default="songs",
        help="Output directory (default: songs)",
    )
    parser.add_argument(
        "--song",
        choices=[s.slug for s in SONGS],
        help="Generate a single song by slug",
    )
    args = parser.parse_args(argv)

    songs = SONGS if args.song is None else [s for s in SONGS if s.slug == args.song]
    os.makedirs(args.output, exist_ok=True)

    print(f"Generating {len(songs)} song(s) -> {args.output}/")
    for song in songs:
        print(f"  [{song.id}] {song.title} ({song.key_root} {song.key_mode})...")
        song_dir = generate_song(song, args.output)
        print(f"       -> {song_dir}/")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
