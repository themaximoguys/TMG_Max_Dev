# maxdev troubleshooting (learned on a live MAS 9 tenant)

## API error codes

| Code | Meaning | Fix |
|---|---|---|
| BMXAA9301E | Not authorised for the object structure. Usually the structure has no auth app while `mxe.int.enableosauth=1` | `maxdev bootstrap authapps --apply`, or grant the user's group access to that app |
| BMXAA4216E | Unknown object: the structure doesn't exist on this tenant | Check `maxdev doctor`. If none is usable, the TMG predeploy clone (ask first) |
| BMXAA1283E | Structure is Consumed By MIGRATIONMGR (DM*), and REST refuses it | Use or clone an INTEGRATION structure |
| BMXAA0031E "X is read only" on page 2 | `select=*` pulled in a read-only child set (e.g. REPORTSCHED) | Give the type an explicit `select` in registry.yaml |
| BMXAA8744E query not parsed | OSLC syntax; there is no `not in` | Use `a!="x" and a!="y"` |
| BMXAA7837E ImportError in a script | Python stdlib import in Jython | Replace it with `java.*` |

## Pull problems

- **Timeout (180 s) or HTTP 500 on a type:** the child tree is too heavy.
  - Narrow `select` and lower `page` for that type in `maxdev/registry.yaml`.
  - If one record still breaks the server, find it by pulling names in chunks, then add it to the type's `skip:` list. On the demo this was `DMEXPGROUP` in object structures.
- **"record missing name field":** the API returned `_hidden` rows without their key, e.g. SaaS-internal properties. Extract skips and counts them; this is expected.
- **App Designer XML on one line:** Maximo stores it that way. Extract pretty-prints it, with a check that only whitespace changes.

## Reading a diff

- `same` means the repo file matches live for every field the file declares.
- null vs `[]` vs `{}` is ignored on purpose, so a diff never shows only those.
- Default diff compares only fields present in the file. Use `--full` to see every live field.

## Promoting to another environment

Records pulled from one environment can carry IDs that Maximo generated there, e.g. `alndomainid`, `maxlookupmapid`, `srestrictnum` and `classstructureid`. They're harmless when deploying back to the same environment. Strip them, or match on content, before deploying to a different one. Order:
1. predeploy on the target
2. dry run
3. layered deploy
4. `dbconfig apply`
5. diff
