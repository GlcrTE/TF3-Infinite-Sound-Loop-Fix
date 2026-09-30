"""Builds the replacement WAVs for the mod from the game's own construction sounds.

For every drag sound set (street, track, lane modifier) one clip is rendered:
the original drag_start sound followed by the original drag_1..5 sounds, cut to
a fixed length and faded out. The engine plays it once as `dragStart`, while the
endlessly repeating `drag` sounds are replaced with a short silent clip.

Also regenerates the mod's _content.json file list.

Usage: python tools/build_sounds.py [--game "<TF3 install dir>"] [--duration 2.0]
"""

import argparse
import array
import io
import json
import os
import wave
import zipfile

DEFAULT_GAME = r"D:\Games\SteamLibrary\steamapps\common\Transport Fever 3"
MOD_DIR = os.path.join(os.path.dirname(__file__), "..", "mod", "glcrte_infinite_sound_loop_fix_1")
SOUND_ROOT = "gui/construction/sound/"

SETS = {
    "street": "build/street/",
    "track": "build/track/",
    "lane_modifier": "tool/lane_modifier/",
}

SAMPLE_RATE = 48000
CROSSFADE = 0.015  # seconds between consecutive clips
FADE_OUT = 0.4  # seconds at the end of the clip
SILENCE = 0.05  # length of the silent replacement for the repeating drag sounds


def read_wav(zf, path):
    with wave.open(io.BytesIO(zf.read(SOUND_ROOT + path))) as w:
        assert w.getnchannels() == 1 and w.getsampwidth() == 2, path
        assert w.getframerate() == SAMPLE_RATE, path
        samples = array.array("h")
        samples.frombytes(w.readframes(w.getnframes()))
        return [float(s) for s in samples]


def write_wav(path, samples):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = array.array("h", (max(-32768, min(32767, int(round(s)))) for s in samples))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(data.tobytes())


def render(start, drags, duration):
    total = int(duration * SAMPLE_RATE)
    xf = int(CROSSFADE * SAMPLE_RATE)
    out = [0.0] * total
    pos = 0
    i = 0
    while pos < total:
        clip = start if i == 0 else drags[(i - 1) % len(drags)]
        for n, s in enumerate(clip):
            if pos + n >= total:
                break
            gain = 1.0
            if n < xf and pos > 0:
                gain = n / xf
            elif n >= len(clip) - xf:
                gain = (len(clip) - n) / xf
            out[pos + n] += s * gain
        pos += max(1, len(clip) - xf)
        i += 1

    fade = int(FADE_OUT * SAMPLE_RATE)
    for n in range(fade):
        out[total - fade + n] *= 1.0 - n / fade

    # never louder than the loudest original clip
    ref = max(abs(s) for clip in [start] + drags for s in clip)
    peak = max(abs(s) for s in out) or 1.0
    if peak > ref:
        out = [s * ref / peak for s in out]
    return out


def write_content_json():
    content = os.path.join(MOD_DIR, "content")
    files = []
    for root, _, names in os.walk(content):
        for name in names:
            files.append(os.path.relpath(os.path.join(root, name), content).replace(os.sep, "/"))
    with open(os.path.join(MOD_DIR, "_content.json"), "w", newline="\n") as f:
        json.dump({"archives": None, "files": sorted(files)}, f, indent=4)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--game", default=DEFAULT_GAME)
    parser.add_argument("--duration", type=float, default=2.0)
    args = parser.parse_args()

    sound_dir = os.path.join(MOD_DIR, "content", "sound")
    with zipfile.ZipFile(os.path.join(args.game, "base", "content", "gui.zip")) as zf:
        for name, prefix in SETS.items():
            start = read_wav(zf, prefix + "drag_start.wav")
            drags = [read_wav(zf, f"{prefix}drag_{n}.wav") for n in range(1, 6)]
            write_wav(os.path.join(sound_dir, f"{name}_drag.wav"), render(start, drags, args.duration))
            print(f"{name}_drag.wav ({args.duration:.1f}s)")

    write_wav(os.path.join(sound_dir, "silence.wav"), [0.0] * int(SILENCE * SAMPLE_RATE))
    write_content_json()


if __name__ == "__main__":
    main()
