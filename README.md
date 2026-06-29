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

### GitHub Pages (recommended)

After pushing to `main`, enable Pages in your repo:

1. Go to **Settings → Pages**
2. Under **Build and deployment**, set **Source** to **GitHub Actions**
3. The site deploys automatically on each push to `main`

Your site will be live at: `https://brendin10.github.io/Bandland/`

The Pages dashboard lets you hit **Generate Song**, listen to the full mix, preview stems, and download WAV/MIDI files — no local setup required.

### Local Streamlit app

For live generation with FluidSynth on your machine:

```bash
streamlit run Bandland.py
```

Click **Generate Song** to compose a new track. Output is saved to `songs/.generated/`.

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

## Where songs are saved

The first 3 pre-generated songs live in the repo under:

- `songs/01_neon_nights/`
- `songs/02_rebel_pulse/`
- `songs/03_chrome_hearts/`

Each folder contains the full mix WAV, MIDI file, `metadata.json`, and a `stems/` subfolder with individual tracks.

Songs created via the Streamlit dashboard are saved to `songs/.generated/`.
