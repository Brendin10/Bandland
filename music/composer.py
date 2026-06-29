"""Multi-track MIDI composition for Bandland songs."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from midiutil import MIDIFile

from music.structures import (
    BEATS_PER_BAR,
    BPM,
    DRUM_NOTES,
    SECTIONS,
    STEM_PROGRAMS,
    TOTAL_BARS,
)
from music.theory import (
    Chord,
    SongDef,
    chord_bass_note,
    chord_notes,
    progression_for_bars,
    scale_notes,
)

if TYPE_CHECKING:
    pass

# MIDI channels (0-indexed); channel 9 = drums
CH_DRUMS = 9
CH_BASS = 0
CH_CHORDS = 1
CH_LEAD = 2

TRACK_INDEX = {"drums": 0, "bass": 1, "chords": 2, "lead": 3}


def _add_drum_hit(
    midi: MIDIFile,
    track: int,
    note: int,
    beat: float,
    duration: float = 0.25,
    velocity: int = 90,
) -> None:
    midi.addNote(track, CH_DRUMS, note, beat, duration, velocity)


def _compose_drums(
    midi: MIDIFile,
    track: int,
    start_bar: int,
    bars: int,
    section_name: str,
) -> None:
    """Kick/snare/hat patterns varying by section."""
    for bar_offset in range(bars):
        bar = start_bar + bar_offset
        base_beat = bar * BEATS_PER_BAR

        is_outro = section_name == "outro"
        is_verse = section_name == "verse"
        is_chorus = section_name == "chorus"

        # Kick
        if not is_outro or bar_offset == 0:
            _add_drum_hit(midi, track, DRUM_NOTES["kick"], base_beat, 0.25, 100)
            if not is_verse and not is_outro:
                _add_drum_hit(
                    midi, track, DRUM_NOTES["kick"], base_beat + 2, 0.25, 95
                )
            if is_chorus:
                _add_drum_hit(
                    midi, track, DRUM_NOTES["kick"], base_beat + 3, 0.25, 85
                )

        # Snare
        if not is_outro:
            vel = 70 if is_verse else 95
            _add_drum_hit(
                midi, track, DRUM_NOTES["snare"], base_beat + 1, 0.25, vel
            )
            _add_drum_hit(
                midi, track, DRUM_NOTES["snare"], base_beat + 3, 0.25, vel
            )

        # Hi-hats
        if is_outro:
            continue
        hat_vel = 55 if is_verse else 70
        for eighth in range(8):
            beat = base_beat + eighth * 0.5
            note = (
                DRUM_NOTES["open_hat"]
                if is_chorus and eighth % 4 == 3
                else DRUM_NOTES["closed_hat"]
            )
            _add_drum_hit(midi, track, note, beat, 0.2, hat_vel)

        # Fill before chorus (last bar of hook/verse going into chorus handled at section boundary)
        if bar_offset == bars - 1 and section_name in ("hook", "verse"):
            _add_drum_hit(
                midi, track, DRUM_NOTES["snare"], base_beat + 3.5, 0.2, 110
            )


def _compose_bass(
    midi: MIDIFile,
    track: int,
    start_bar: int,
    bars: int,
    chords: list[Chord],
    pattern: str,
    scale: list[int],
) -> None:
    chord_list = progression_for_bars(chords, bars)
    beat_per_chord = BEATS_PER_BAR * 2  # 2 bars per chord

    for i, chord in enumerate(chord_list):
        if i * 2 >= bars:
            break
        bar = start_bar + i * 2
        root = chord_bass_note(chord, octave=2)
        base_beat = bar * BEATS_PER_BAR

        if pattern == "driving":
            for b in range(min(2, bars - i * 2)):
                beat = base_beat + b * BEATS_PER_BAR
                midi.addNote(track, CH_BASS, root, beat, 0.9, 100)
                midi.addNote(track, CH_BASS, root, beat + 1.5, 0.4, 80)
        elif pattern == "syncopated":
            for b in range(min(2, bars - i * 2)):
                beat = base_beat + b * BEATS_PER_BAR
                midi.addNote(track, CH_BASS, root, beat + 0.5, 0.4, 95)
                midi.addNote(track, CH_BASS, root, beat + 2.5, 0.4, 85)
                midi.addNote(track, CH_BASS, root, beat + 3, 0.3, 75)
        else:  # arpeggiated
            notes = [n - 24 for n in chord_notes(chord, octave=3)]
            for b in range(min(2, bars - i * 2)):
                beat = base_beat + b * BEATS_PER_BAR
                for j, n in enumerate(notes):
                    midi.addNote(
                        track, CH_BASS, max(28, n), beat + j * 0.5, 0.4, 85
                    )


def _compose_chords(
    midi: MIDIFile,
    track: int,
    start_bar: int,
    bars: int,
    chords: list[Chord],
    section_name: str,
) -> None:
    chord_list = progression_for_bars(chords, bars)

    for i, chord in enumerate(chord_list):
        if i * 2 >= bars:
            break
        bar = start_bar + i * 2
        notes = chord_notes(chord, octave=4)
        base_beat = bar * BEATS_PER_BAR
        section_bars = min(2, bars - i * 2)

        if section_name == "hook":
            for b in range(section_bars):
                beat = base_beat + b * BEATS_PER_BAR
                for n in notes:
                    midi.addNote(track, CH_CHORDS, n, beat, 0.3, 75)
                    midi.addNote(track, CH_CHORDS, n, beat + 2, 0.3, 70)
        elif section_name == "verse":
            for b in range(section_bars):
                beat = base_beat + b * BEATS_PER_BAR
                vel = 55
                for n in notes:
                    midi.addNote(track, CH_CHORDS, n, beat, BEATS_PER_BAR - 0.1, vel)
        elif section_name == "outro":
            beat = base_beat
            vel = max(40, 70 - bar * 5)
            for n in notes:
                midi.addNote(track, CH_CHORDS, n, beat, section_bars * BEATS_PER_BAR, vel)
        else:  # chorus
            for b in range(section_bars):
                beat = base_beat + b * BEATS_PER_BAR
                for n in notes:
                    midi.addNote(track, CH_CHORDS, n, beat, BEATS_PER_BAR - 0.05, 80)


def _compose_lead(
    midi: MIDIFile,
    track: int,
    start_bar: int,
    bars: int,
    melody_degrees: list[int],
    scale: list[int],
    section_name: str,
) -> None:
    if section_name == "outro":
        # Resolve to tonic
        tonic = scale[0] + 12
        beat = start_bar * BEATS_PER_BAR
        midi.addNote(track, CH_LEAD, tonic, beat, bars * BEATS_PER_BAR, 60)
        return

    note_duration = 0.5 if section_name == "hook" else 0.75
    vel = 95 if section_name == "hook" else 80 if section_name == "chorus" else 65

    degree_idx = 0
    for bar_offset in range(bars):
        bar = start_bar + bar_offset
        beats_in_bar = 2 if section_name == "verse" else 4
        step = BEATS_PER_BAR / beats_in_bar

        for step_i in range(beats_in_bar):
            deg = melody_degrees[degree_idx % len(melody_degrees)]
            degree_idx += 1
            note = scale[deg % len(scale)]
            if section_name == "chorus" and bar_offset % 2 == 1:
                note += 12  # octave up every other bar in chorus
            beat = bar * BEATS_PER_BAR + step_i * step
            midi.addNote(track, CH_LEAD, note, beat, note_duration, vel)


def compose_song(song: SongDef) -> MIDIFile:
    """Build a 4-track MIDI file for the given song definition."""
    num_tracks = 4
    midi = MIDIFile(numTracks=num_tracks, removeDuplicates=False)

    for t in range(num_tracks):
        midi.addTempo(t, 0, song.bpm)

    # Program changes per track
    midi.addProgramChange(1, CH_BASS, 0, STEM_PROGRAMS["bass"])
    midi.addProgramChange(2, CH_CHORDS, 0, STEM_PROGRAMS["chords"])
    midi.addProgramChange(3, CH_LEAD, 0, STEM_PROGRAMS["lead"])

    scale = scale_notes(song.key_root, song.key_mode, octave=4)
    lead_scale = scale_notes(song.key_root, song.key_mode, octave=5)

    current_bar = 0
    section_occurrence: dict[str, int] = {}

    for section in SECTIONS:
        section_occurrence[section.name] = (
            section_occurrence.get(section.name, 0) + 1
        )
        chords = song.progressions.get(
            section.name,
            song.progressions.get("hook", [Chord(song.key_root, "min")]),
        )

        if section.name in ("hook", "outro"):
            melody = song.hook_melody
        elif section.name == "chorus":
            melody = song.chorus_melody
        else:
            melody = song.verse_melody

        _compose_drums(midi, 0, current_bar, section.bars, section.name)
        _compose_bass(
            midi,
            1,
            current_bar,
            section.bars,
            chords,
            song.bass_pattern,
            scale,
        )
        _compose_chords(
            midi, 2, current_bar, section.bars, chords, section.name
        )
        _compose_lead(
            midi,
            3,
            current_bar,
            section.bars,
            melody,
            lead_scale,
            section.name,
        )

        current_bar += section.bars

    assert current_bar == TOTAL_BARS, f"Expected {TOTAL_BARS} bars, got {current_bar}"
    return midi


def write_song_midi(song: SongDef, output_path: str) -> str:
    """Compose and write MIDI file; returns output path."""
    midi = compose_song(song)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "wb") as f:
        midi.writeFile(f)
    return output_path
