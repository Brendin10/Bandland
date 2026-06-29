# Bandland

Music generation pipeline for the Monster Rebel Chronicles project. Generates 60-second instrumental synth-pop songs with individual stems for Ableton Live.

## Song Structure

Each song is **60 seconds** at 120 BPM:

| Section | Bars | Duration |
|---------|------|----------|
| Short Hook | 4 | 8s |
| Chorus | 8 | 16s |
| Verse | 6 | 12s |
| Short Hook | 4 | 8s |
| Chorus | 6 | 12s |
| Short Outro | 2 | 4s |

## Songs

1. **Neon Nights** — A minor, driving synth-pop
2. **Rebel Pulse** — D minor, syncopated groove
3. **Chrome Hearts** — E minor, arpeggiated hooks

## Setup

### System dependencies

```bash
sudo apt-get install fluidsynth fluid-soundfont-gm
```

### Python dependencies

```bash
pip install -r requirements.txt
```

## Web dashboard

Launch the song studio in your browser:

```bash
streamlit run Bandland.py
```

Click **Generate Song** to create a random track from the library. You can listen to the full mix, preview each stem, and download WAV or MIDI files directly. Song info (title, key, BPM, length) is shown above the player.

## Generate songs (CLI)

From the project root:

```bash
python -m music.generate_songs
```

Generate a single song:

```bash
python -m music.generate_songs --song neon_nights
```

Output goes to `songs/` by default. Use `-o` to change the output directory.

## Output layout

```
songs/
  01_neon_nights/
    01_neon_nights.mid
    01_neon_nights_full_mix.wav
    metadata.json
    stems/
      drums.wav
      bass.wav
      chords.wav
      lead.wav
  02_rebel_pulse/
    ...
  03_chrome_hearts/
    ...
```

- **Stems** — 48 kHz, 16-bit WAV, time-aligned from bar 1
- **metadata.json** — BPM, key, section bar markers for Ableton locators
- **.mid** — Full arrangement for re-editing or replacing instruments in Ableton

## Ableton Live workflow

1. Drag all four stems from `stems/` into one session.
2. Use `metadata.json` section markers to place locators.
3. Optionally import the `.mid` file to replace or augment parts with your own instruments.
4. Mix, add effects, or layer additional elements per stem.

## Game app

```bash
streamlit run Bandland.py
```
