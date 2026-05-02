# Commands

Run from the repository root.

## Generate and Build

```bash
make generate
make build
```

## Full Local Release Check

```bash
make release-check
```

This runs XcodeGen, manifest validation, and Xcode simulator build with workspace-local DerivedData.

## Validate Manifest Only

```bash
make validate
```

## Regenerate Guide PDF

```bash
make guide
```

Use when `Docs/guide.md` changes materially.

## Install This Skill Into Codex

```bash
make install-skill
```

This copies `Skills/realitykit-pipeline-guide` into `${CODEX_HOME:-$HOME/.codex}/skills/realitykit-pipeline-guide`.

## Fast Repo Structure Check

```bash
python3 Skills/realitykit-pipeline-guide/scripts/check_repo.py
```

