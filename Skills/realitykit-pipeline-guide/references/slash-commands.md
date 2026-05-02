# Slash Commands

Codex uses this repository mainly through the `realitykit-pipeline-guide` skill and `Tools/rkp.py`.

Claude-style slash commands are also provided for environments that support `.claude/commands`:

```text
/rkp status
/rkp status json
/rkp asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
/rkp-asset id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
/rkp-status
```

These slash commands are wrappers around:

```bash
test -f Tools/rkp.py && test -f Tools/asset_manifest.json
python3 Tools/rkp.py status
python3 Tools/rkp.py make-asset enemy_drone --type gameplay_target --prompt "red bullseye drone target"
python3 Tools/rkp.py release-check
```

They do not bypass build, screenshot acceptance, or release gates.
If the guard command fails, do not create a fake RKP structure. Ask the user to open the real repo, clone the template, or request bootstrap.

For Codex sessions, prefer direct natural language plus the installed skill, for example:

```text
Use realitykit-pipeline-guide and make an asset:
id=enemy_drone type=gameplay_target prompt="red bullseye drone target"
```

Then run the corresponding `Tools/rkp.py` command.
