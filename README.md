# Infinite Sound Loop Fix (TF3)

A Transport Fever 3 mod that stops the endlessly looping construction sound while building roads, train tracks and lane modifiers.

Instead of looping for as long as you drag, the sound now plays **for 2 seconds** when you start dragging a new segment or click to set a build point, and then fades out.

## How it works

The engine plays the `dragStart` clip of a builder audio set once, then keeps retriggering the short `drag` clips while you drag. The mod registers a `loadBuilderAudioSet` modifier (`content/mod.script.tl`) that, for every sound set using the vanilla street, track or lane modifier drag sounds:

- replaces `dragStart` with a 2 second clip made from the original start and drag sounds, faded out at the end
- replaces `drag`, `dragBridge` and `dragTunnel` with a short silent clip

No base game files are overwritten. Build, bulldoze and `dragEnd` sounds stay unchanged.

## Installation

Copy `mod/glcrte_building_sounds_overhaul_1` into your local TF3 mods folder:

```
<Steam>\userdata\<your Steam ID>\3493540\local\mods\
```

Then enable the mod in the game's mod menu. `tools/deploy.ps1` does this copy automatically.

## Building the sounds

The clips in `content/sound/` are generated from the game's own sound files:

```
python tools/build_sounds.py [--game "<TF3 install dir>"] [--duration 2.0]
```

The script reads the originals from `base/content/gui.zip`, renders the clips and regenerates `_content.json`.
