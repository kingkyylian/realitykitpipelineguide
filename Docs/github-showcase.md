# GitHub Showcase Notes

Use this when preparing the public repository page, release, or outreach post.

## Target Lists

- GitHub Trending: needs strong first impression, GIF/video, topics, and an active release.
- iOS Dev Weekly / Swift Weekly Brief: needs a crisp learning angle and a working iOS demo.
- awesome-swift / awesome-ios: needs stable README, license, CI, and clear scope.
- RealityKit/Apple dev communities: needs screenshots, a short demo clip, and practical asset-pipeline lessons.

## Repository Description

```text
Command-first RealityKit asset pipeline toolkit with CLI, Codex skill, slash commands, and a tiny SwiftUI fixture.
```

## Topics

```text
realitykit
swift
swiftui
ios
codex-skill
blender
usdz
developer-tools
3d-pipeline
asset-pipeline
```

## First Release

Tag:

```bash
git tag v0.1.0
```

Release title:

```text
v0.1.0 - Public learning pipeline preview
```

Release summary:

```text
First public preview of a teaching-oriented RealityKit asset pipeline toolkit. Includes the `rkp` CLI, installable Codex skill, agent slash commands, CLI smoke tests, imported Blender/USDZ target assets, a SwiftUI + RealityKit verification fixture, asset manifest budgets, simulator screenshot evidence, Blender starter tooling, and a shareable PDF guide.
```

## Outreach Angle

```text
Most RealityKit examples focus only on Swift code. This repo teaches the missing production loop: Blender asset brief, mesh scale/origin, UV/material setup, USDZ export, Xcode resource import, RealityKit loader fallback, simulator screenshot, and worklog documentation.
```

## Missing Before Outreach

- README demo GIF or short MP4.
- GitHub repo description and topics set in the web UI.
- `v0.1.0` tag and GitHub Release.
- Optional: one short post showing the pipeline screenshot and guide PDF.

## Local Polish Ready

- README badges point at CI, Python 3.10+, MIT license, and the RealityKit fixture scope.
- `Docs/blender-support.md` documents Blender 4.x expectations, observed local fallback behavior, and acceptance rules.
- `Docs/first-good-issues.md` provides learner-sized issue candidates that preserve the RKP-first product boundary.
