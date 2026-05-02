# RealityKit Pipeline Status

Use this command when the user asks where the RealityKit pipeline stands.

Invocation examples:

```text
/rkp-status
/rkp-status json
```

User arguments:

```text
$ARGUMENTS
```

## Behavior

Run from the repository root:

```bash
python3 Tools/rkp.py status
python3 Tools/rkp.py doctor
```

If `$ARGUMENTS` contains `json`, also run:

```bash
python3 Tools/rkp.py status --json
python3 Tools/rkp.py doctor --json
```

## Response Style

Summarize:

- imported assets
- planned assets
- prompt-backed archetypes
- next pipeline action
- doctor errors and warnings

Keep the answer short and actionable.
