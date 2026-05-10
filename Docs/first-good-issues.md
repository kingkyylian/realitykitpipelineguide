# First Good Issues

Use these as learner-friendly GitHub issues or small local tasks. Each item should preserve the RKP-first product boundary: `rkp` is the stable asset pipeline, the fixture app proves assets, and `rkg` stays experimental labs unless the issue explicitly says otherwise.

| Issue | Why it is good first work | Suggested files | Verification |
| --- | --- | --- | --- |
| Add a `usdzip` troubleshooting note | Small docs task that improves the Blender fallback path without touching code. | `Docs/blender-support.md`, `Docs/cli-tool.md` | `rtk .venv/bin/python -m unittest Tests/test_public_polish_docs.py` |
| Expand the first asset screenshot checklist | Teaches the acceptance contract and keeps imported assets tied to evidence. | `Docs/production-playbook.md`, `Docs/repo-release-checklist.md` | `rtk make verify-local` |
| Draft Module 4 material-response brief | Starts the next education module without changing asset loader behavior. | `Docs/guide.md`, `Prompts/` | Regenerate guide PDF if `Docs/guide.md` changes. |
| Add one more prompt archetype example | Improves onboarding for users who do not know the supported prompt templates. | `README.md`, `Docs/cli-tool.md` | `rtk .venv/bin/python -m unittest discover -s Tests` |
| Document one real external-project setup | Converts a fresh clone or pipx install into reusable learner evidence. | `Docs/WORKLOG.md`, `Docs/ai-handoff.md` | `rkp init`, `rkp doctor`, `rkp release-check` in a temporary project |

## Scope Rules

- Keep changes small enough for one review.
- Prefer docs, examples, or focused tests before changing CLI behavior.
- Do not remove RealityKit fallback behavior.
- Do not mark assets accepted without screenshot evidence.
- Do not expand RKG unless the issue explicitly targets generated games, archetypes, store packs, or screenshot QA.

## Ready-To-File Titles

- `docs: add usdzip troubleshooting to Blender support matrix`
- `docs: expand first asset screenshot acceptance checklist`
- `docs: draft Module 4 material response learning brief`
- `docs: add another supported prompt archetype example`
- `docs: record fresh external project setup walkthrough`
