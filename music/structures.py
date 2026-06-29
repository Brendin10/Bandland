"""Song structure definitions for 60-second tracks."""

from dataclasses import dataclass

BPM = 120
BEATS_PER_BAR = 4
TOTAL_BARS = 30
SAMPLE_RATE = 48000

STEM_TRACKS = ("drums", "bass", "chords", "lead")

# GM program numbers for each stem
STEM_PROGRAMS = {
    "drums": 0,  # channel 10, percussion
    "bass": 33,  # Electric Bass (finger)
    "chords": 89,  # Warm Pad
    "lead": 81,  # Lead 2 (sawtooth)
}

DRUM_NOTES = {
    "kick": 36,
    "snare": 38,
    "closed_hat": 42,
    "open_hat": 46,
}


@dataclass(frozen=True)
class Section:
    name: str
    bars: int


# Hook(4) + Chorus(8) + Verse(6) + Hook(4) + Chorus(6) + Outro(2) = 30 bars = 60s
SECTIONS: tuple[Section, ...] = (
    Section("hook", 4),
    Section("chorus", 8),
    Section("verse", 6),
    Section("hook", 4),
    Section("chorus", 6),
    Section("outro", 2),
)


def bar_to_seconds(bar: int) -> float:
    """Convert 1-indexed bar number to start time in seconds."""
    return (bar - 1) * BEATS_PER_BAR * 60.0 / BPM


def bars_to_seconds(bars: int) -> float:
    return bars * BEATS_PER_BAR * 60.0 / BPM


def total_duration_seconds() -> float:
    return bars_to_seconds(TOTAL_BARS)


def section_markers() -> list[dict]:
    """Return Ableton-friendly section markers."""
    markers = []
    bar = 1
    for section in SECTIONS:
        markers.append(
            {
                "name": section.name,
                "start_bar": bar,
                "bars": section.bars,
                "start_seconds": round(bar_to_seconds(bar), 3),
                "duration_seconds": round(bars_to_seconds(section.bars), 3),
            }
        )
        bar += section.bars
    return markers
