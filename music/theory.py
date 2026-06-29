"""Music theory helpers: scales, chords, and song definitions."""

from dataclasses import dataclass

# MIDI note numbers (C4 = 60)
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Scale intervals from root (semitones)
MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]

# Chord qualities: semitone offsets from root
CHORD_QUALITIES = {
    "maj": [0, 4, 7],
    "min": [0, 3, 7],
    "dim": [0, 3, 6],
    "dom7": [0, 4, 7, 10],
}


@dataclass(frozen=True)
class Chord:
    root: str
    quality: str = "maj"

    @property
    def symbol(self) -> str:
        suffix = {"maj": "", "min": "m", "dim": "dim", "dom7": "7"}.get(
            self.quality, ""
        )
        return f"{self.root}{suffix}"


@dataclass(frozen=True)
class SongDef:
    id: str
    title: str
    slug: str
    key_root: str
    key_mode: str  # "minor" or "major"
    bpm: int
    vibe: str
    progressions: dict[str, list[Chord]]
    hook_melody: list[int]  # scale degrees (0-indexed) relative to key
    chorus_melody: list[int]
    verse_melody: list[int]
    bass_pattern: str  # "driving", "syncopated", "arpeggiated"


FLAT_ALIASES = {
    "DB": "C#",
    "EB": "D#",
    "GB": "F#",
    "AB": "G#",
    "BB": "A#",
}


def _normalize_note_name(name: str) -> str:
    cleaned = name.strip().upper().replace("♭", "B").replace("♯", "#")
    if len(cleaned) == 1:
        return cleaned
    if cleaned in FLAT_ALIASES:
        return FLAT_ALIASES[cleaned]
    if len(cleaned) == 2 and cleaned[1] == "B":
        return FLAT_ALIASES.get(cleaned, cleaned[0] + "#")
    return cleaned[0] + cleaned[1:]


def note_to_midi(name: str, octave: int = 4) -> int:
    """Convert note name like 'A', 'F#', or 'Bb' to MIDI number."""
    normalized = _normalize_note_name(name)
    pitch = NOTE_NAMES.index(normalized)
    return (octave + 1) * 12 + pitch


def scale_notes(root: str, mode: str = "minor", octave: int = 4) -> list[int]:
    """Return MIDI notes for one octave of a scale."""
    root_midi = note_to_midi(root, octave)
    intervals = MINOR_SCALE if mode == "minor" else MAJOR_SCALE
    return [root_midi + i for i in intervals]


def chord_notes(chord: Chord, octave: int = 4) -> list[int]:
    """Return MIDI notes for a chord voicing."""
    root_midi = note_to_midi(chord.root, octave)
    offsets = CHORD_QUALITIES.get(chord.quality, CHORD_QUALITIES["maj"])
    return [root_midi + o for o in offsets]


def chord_bass_note(chord: Chord, octave: int = 2) -> int:
    return note_to_midi(chord.root, octave)


def progression_for_bars(chords: list[Chord], bars: int) -> list[Chord]:
    """Repeat or truncate chord list to fill `bars` (2 beats per chord change at 2 bars each)."""
    if not chords:
        return []
    # Each chord lasts 2 bars in our template
    needed = max(1, (bars + 1) // 2)
    result = []
    i = 0
    while len(result) < needed:
        result.append(chords[i % len(chords)])
        i += 1
    return result


# --- Three unique song definitions ---

SONGS: list[SongDef] = [
    SongDef(
        id="01",
        title="Neon Nights",
        slug="neon_nights",
        key_root="A",
        key_mode="minor",
        bpm=120,
        vibe="Driving, punchy synth-pop",
        progressions={
            "hook": [
                Chord("A", "min"),
                Chord("F", "maj"),
                Chord("C", "maj"),
                Chord("G", "maj"),
            ],
            "chorus": [
                Chord("A", "min"),
                Chord("G", "maj"),
                Chord("F", "maj"),
                Chord("E", "maj"),
            ],
            "verse": [
                Chord("D", "min"),
                Chord("A", "min"),
                Chord("F", "maj"),
                Chord("G", "maj"),
            ],
            "outro": [Chord("A", "min"), Chord("A", "min")],
        },
        hook_melody=[4, 5, 4, 2, 0, 2, 4, 5],  # E-F-E-C-A-C-E-F in A minor
        chorus_melody=[4, 5, 6, 5, 4, 3, 2, 4, 5, 6, 5, 4, 3, 2, 1, 0],
        verse_melody=[2, 3, 4, 3, 2, 1, 2, 3, 4, 3, 2, 1],
        bass_pattern="driving",
    ),
    SongDef(
        id="02",
        title="Rebel Pulse",
        slug="rebel_pulse",
        key_root="D",
        key_mode="minor",
        bpm=120,
        vibe="Darker, syncopated groove",
        progressions={
            "hook": [
                Chord("D", "min"),
                Chord("Bb", "maj"),
                Chord("F", "maj"),
                Chord("C", "maj"),
            ],
            "chorus": [
                Chord("D", "min"),
                Chord("C", "maj"),
                Chord("Bb", "maj"),
                Chord("A", "maj"),
            ],
            "verse": [
                Chord("G", "min"),
                Chord("D", "min"),
                Chord("Bb", "maj"),
                Chord("C", "maj"),
            ],
            "outro": [Chord("D", "min"), Chord("D", "min")],
        },
        hook_melody=[3, 4, 5, 4, 3, 2, 3, 4],
        chorus_melody=[5, 4, 3, 4, 5, 6, 5, 4, 3, 2, 3, 4, 5, 4, 3, 2],
        verse_melody=[1, 2, 3, 2, 1, 0, 1, 2, 3, 4, 3, 2],
        bass_pattern="syncopated",
    ),
    SongDef(
        id="03",
        title="Chrome Hearts",
        slug="chrome_hearts",
        key_root="E",
        key_mode="minor",
        bpm=120,
        vibe="Brighter, arpeggiated hooks",
        progressions={
            "hook": [
                Chord("E", "min"),
                Chord("C", "maj"),
                Chord("G", "maj"),
                Chord("D", "maj"),
            ],
            "chorus": [
                Chord("E", "min"),
                Chord("D", "maj"),
                Chord("C", "maj"),
                Chord("B", "maj"),
            ],
            "verse": [
                Chord("A", "min"),
                Chord("E", "min"),
                Chord("C", "maj"),
                Chord("D", "maj"),
            ],
            "outro": [Chord("E", "min"), Chord("E", "min")],
        },
        hook_melody=[2, 4, 6, 4, 2, 1, 2, 4],
        chorus_melody=[4, 6, 5, 4, 3, 4, 5, 6, 4, 3, 2, 3, 4, 5, 4, 3],
        verse_melody=[3, 4, 5, 4, 3, 2, 1, 2, 3, 4, 5, 4],
        bass_pattern="arpeggiated",
    ),
]


def get_song(slug: str) -> SongDef:
    for song in SONGS:
        if song.slug == slug:
            return song
    raise ValueError(f"Unknown song slug: {slug}")
