# Deploy a workflow through maxdev

Read `AGENTS.md` and `skills/maximo-dev/SKILL.md`. Use `OSLCDeployment.md` only
as a payload/schema reference; all tenant operations go through maxdev.

1. Confirm the user-named environment and inspect `python3 -m maxdev types`.
   Use filtered extracts or `query`/`schema` to verify dependencies and fields.
2. Save person groups, roles and actions in their registered `src/` folders.
   Save workflows as `src/13-workflows/<PROCESS>__<REVISION>.json`.
3. Prepare manifests for dependencies, each subprocess level, then the parent.
   maxdev sorts workflows by filename within their layer; it does not compute a
   subprocess graph. Do not assume manifest list order controls deployment.
4. Run `python3 -m maxdev diff --manifest TICKET --env NAME`, then
   `python3 -m maxdev deploy --manifest TICKET --env NAME` for each stage.
5. Show the concrete plans and obtain approval before running the same deployment
   commands with `--apply`. Stop on failures; report receipts and skipped records.
6. Diff again and verify nodes, actions and assignments. Record Workflow Designer
   validation, enablement and activation as manual steps requiring user coordination.
   Never delete a live process simply to retry deployment.

Missing roles must be modeled as repo artifacts and deployed before the workflow.
A role's name is globally unique. Include happy-path and rejection-path scenarios
in the handoff, and distinguish offline validation from tenant execution.
