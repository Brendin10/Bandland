"""Render MIDI to WAV stems using FluidSynth."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import pretty_midi
from pydub import AudioSegment

from music.structures import SAMPLE_RATE, STEM_TRACKS, total_duration_seconds

DEFAULT_SOUNDFONT = "/usr/share/sounds/sf2/FluidR3_GM.sf2"


def _find_soundfont() -> str:
    candidates = [
        DEFAULT_SOUNDFONT,
        "/usr/share/sounds/sf2/default-GM.sf2",
        "/usr/share/soundfonts/default.sf2",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path
    raise FileNotFoundError(
        "No SoundFont found. Install fluid-soundfont-gm: "
        "sudo apt-get install fluid-soundfont-gm"
    )


def _instrument_matches_stem(instrument: pretty_midi.Instrument, stem: str) -> bool:
    if stem == "drums":
        return instrument.is_drum
    program_map = {"bass": 33, "chords": 89, "lead": 81}
    return not instrument.is_drum and instrument.program == program_map.get(stem, -1)


def _extract_stem_midi(pm: pretty_midi.PrettyMIDI, stem: str) -> pretty_midi.PrettyMIDI:
    stem_pm = pretty_midi.PrettyMIDI()
    for inst in pm.instruments:
        if _instrument_matches_stem(inst, stem):
            stem_pm.instruments.append(inst)
    return stem_pm


def _synthesize(midi_data: pretty_midi.PrettyMIDI, soundfont: str) -> np.ndarray:
    audio = midi_data.fluidsynth(fs=SAMPLE_RATE, sf2_path=soundfont)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    return audio.astype(np.float32)


def _pad_or_trim(audio: np.ndarray, target_samples: int) -> np.ndarray:
    if len(audio) >= target_samples:
        return audio[:target_samples]
    return np.pad(audio, (0, target_samples - len(audio)))


def _normalize(audio: np.ndarray, peak: float = 0.9) -> np.ndarray:
    max_val = np.max(np.abs(audio))
    if max_val > 0:
        audio = audio * (peak / max_val)
    return audio


def _float_to_wav(audio: np.ndarray, path: str) -> None:
    audio = np.clip(audio, -1.0, 1.0)
    pcm = (audio * 32767).astype(np.int16)
    # Write via pydub for consistent format
    segment = AudioSegment(
        pcm.tobytes(),
        frame_rate=SAMPLE_RATE,
        sample_width=2,
        channels=1,
    )
    segment.export(path, format="wav")


def _mix_stems(stem_audios: dict[str, np.ndarray]) -> np.ndarray:
    target_len = max(len(a) for a in stem_audios.values())
    mix = np.zeros(target_len, dtype=np.float32)
    gains = {"drums": 0.85, "bass": 0.9, "chords": 0.75, "lead": 0.8}
    for stem, audio in stem_audios.items():
        padded = _pad_or_trim(audio, target_len)
        mix += padded * gains.get(stem, 0.8)
    return _normalize(mix, peak=0.95)


def render_song(
    midi_path: str,
    output_dir: str,
    song_slug: str,
    soundfont: str | None = None,
) -> dict[str, str]:
    """
    Render per-stem WAV files and a full mix from a multi-track MIDI file.

    Returns dict mapping stem name (and 'full_mix') to output file paths.
    """
    sf2 = soundfont or _find_soundfont()
    pm = pretty_midi.PrettyMIDI(midi_path)

    target_samples = int(round(total_duration_seconds() * SAMPLE_RATE))
    stems_dir = os.path.join(output_dir, "stems")
    os.makedirs(stems_dir, exist_ok=True)

    stem_audios: dict[str, np.ndarray] = {}
    outputs: dict[str, str] = {}

    for stem in STEM_TRACKS:
        stem_pm = _extract_stem_midi(pm, stem)
        if not stem_pm.instruments:
            audio = np.zeros(target_samples, dtype=np.float32)
        else:
            audio = _synthesize(stem_pm, sf2)
            audio = _pad_or_trim(audio, target_samples)

        peak = 0.95 if stem == "drums" else 0.85
        audio = _normalize(audio, peak=peak)
        stem_audios[stem] = audio

        out_path = os.path.join(stems_dir, f"{stem}.wav")
        _float_to_wav(audio, out_path)
        outputs[stem] = out_path

    mix_audio = _mix_stems(stem_audios)
    mix_path = os.path.join(output_dir, f"{song_slug}_full_mix.wav")
    _float_to_wav(mix_audio, mix_path)
    outputs["full_mix"] = mix_path

    return outputs


def render_via_cli(
    midi_path: str,
    wav_path: str,
    soundfont: str,
    track: int | None = None,
) -> None:
    """Fallback: render using fluidsynth CLI."""
    cmd = [
        "fluidsynth",
        "-ni",
        "-F",
        wav_path,
        "-r",
        str(SAMPLE_RATE),
        soundfont,
        midi_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
