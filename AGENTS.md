# TMG_Max_Dev — agent guide

Maximo/MAS 9 development repo. Config + code live in `src/` as one file per record and move
to/from Maximo only through `maxdev` (CLI: `python3 -m maxdev`, MCP: `tmg-maximo-dev`).

- Start with the `maximo-dev` skill (.claude/skills/maximo-dev/SKILL.md) — it has the rules.
- Scripts: TMG standards in docs/standards/TMG_AUTOSCRIPT_STANDARDS.md are authoritative;
  build from catalog/templates via `maxdev build`; `maxdev lint` must be clean.
- Java → script: `maxdev java analyze` + `convert-java-to-script` skill.
- Workflow: `maximo-workflow` skill → src/13-workflows/.
- Writes: dry run first, user approval before `--apply`/`apply=true`. Never edit environments/.env.*
  secrets into Git. No demo/seed data loads unless asked.
- References are TMG-only. Do not add client names or third-party assessment content.
- Tests: `python3 -m unittest discover -s tests` (offline, no tenant needed).
