const SONGS = [
  {
    id: "01",
    slug: "neon_nights",
    folder: "01_neon_nights",
    title: "Neon Nights",
    key: "A minor",
    bpm: 120,
    duration_seconds: 60,
    vibe: "Driving, punchy synth-pop",
    stems: ["drums", "bass", "chords", "lead"],
  },
  {
    id: "02",
    slug: "rebel_pulse",
    folder: "02_rebel_pulse",
    title: "Rebel Pulse",
    key: "D minor",
    bpm: 120,
    duration_seconds: 60,
    vibe: "Darker, syncopated groove",
    stems: ["drums", "bass", "chords", "lead"],
  },
  {
    id: "03",
    slug: "chrome_hearts",
    folder: "03_chrome_hearts",
    title: "Chrome Hearts",
    key: "E minor",
    bpm: 120,
    duration_seconds: 60,
    vibe: "Brighter, arpeggiated hooks",
    stems: ["drums", "bass", "chords", "lead"],
  },
];

const STEM_LABELS = {
  drums: "Drums",
  bass: "Bass",
  chords: "Chords / Pads",
  lead: "Lead Melody",
};

function songBase(song) {
  return `songs/${song.folder}`;
}

function mixPath(song) {
  return `${songBase(song)}/${song.id}_${song.slug}_full_mix.wav`;
}

function midiPath(song) {
  return `${songBase(song)}/${song.id}_${song.slug}.mid`;
}

function stemPath(song, stem) {
  return `${songBase(song)}/stems/${stem}.wav`;
}

function pickRandomSong() {
  return SONGS[Math.floor(Math.random() * SONGS.length)];
}

function renderSong(song) {
  document.getElementById("meta-title").textContent = song.title;
  document.getElementById("meta-key").textContent = song.key;
  document.getElementById("meta-bpm").textContent = String(song.bpm);
  document.getElementById("meta-length").textContent = `${song.duration_seconds}s`;
  document.getElementById("meta-vibe").textContent = song.vibe;

  const mixPlayer = document.getElementById("mix-player");
  const mixUrl = mixPath(song);
  mixPlayer.src = mixUrl;
  mixPlayer.load();

  const mixDownload = document.getElementById("mix-download");
  mixDownload.href = mixUrl;
  mixDownload.download = `${song.slug}_full_mix.wav`;

  const midiDownload = document.getElementById("midi-download");
  midiDownload.href = midiPath(song);
  midiDownload.download = `${song.slug}.mid`;

  const stemsList = document.getElementById("stems-list");
  stemsList.innerHTML = "";

  for (const stem of song.stems) {
    const card = document.createElement("article");
    card.className = "stem-card";

    const title = document.createElement("h3");
    title.textContent = STEM_LABELS[stem] || stem;
    card.appendChild(title);

    const audio = document.createElement("audio");
    audio.controls = true;
    audio.preload = "none";
    audio.src = stemPath(song, stem);
    card.appendChild(audio);

    const link = document.createElement("a");
    link.className = "btn-secondary";
    link.href = stemPath(song, stem);
    link.download = `${song.slug}_${stem}.wav`;
    link.textContent = `Download ${(STEM_LABELS[stem] || stem).toLowerCase()}`;
    card.appendChild(link);

    stemsList.appendChild(card);
  }

  document.getElementById("empty").hidden = true;
  document.getElementById("result").hidden = false;
}

document.getElementById("generate-btn").addEventListener("click", () => {
  const status = document.getElementById("status");
  status.hidden = false;
  status.textContent = "Picking a song…";

  window.setTimeout(() => {
    const song = pickRandomSong();
    status.textContent = `Loaded ${song.title}`;
    renderSong(song);
    window.setTimeout(() => {
      status.hidden = true;
    }, 1200);
  }, 400);
});
