# Intent

Why this repository exists and the decisions that shape it. `README.md` says what it does
and how to run it; `AGENTS.md` says how agents must work in it. When a change seems to fit
the code but not this file, stop and ask.

## Purpose

Make IBM Maximo / MAS 9 Manage development **code-managed and AI-assisted**, without
giving up the safety a shared Maximo environment needs.

- Every configuration and code artifact is one reviewable file in Git, pulled from and
  pushed to Maximo through Maximo's own REST APIs.
- People and coding agents (Claude Code, Codex, Copilot, Cursor, Gemini, others) do the
  same work through the same CLI and MCP server.
- Feature, enhancement and bug-fix tickets follow one repeatable flow, with evidence
  that the change works on the tenant.

## Who it is for

TheMaximoGuys consultants and the agents they direct, building and fixing Maximo
configuration on development environments for clients.

## Principles

1. **The repo is the source of truth; Maximo is the target.** Change files, then deploy.
   Investigate live with read-only queries.
2. **Nothing touches a tenant without a dry run and a person's explicit yes.**
   Protected environments refuse writes, and nothing bypasses that.
3. **Proof, not claims.** A deploy is done when the re-diff says `same` and the
   acceptance tests pass on that environment, not when the API says "created".
4. **Stay left on the ladder:** out of the box → configuration → automation script →
   integration → custom Java. Each step right needs a stated reason.
5. **Use IBM's structures first.** Clone a `TMG*` object structure only when nothing
   REST-usable exists, and ask before creating one.
6. **Never break what others built.** One script per MBO and event; App Designer
   changes merge, never replace; deploys never remove grants.
7. **Keep it simple.** One ticket file, the repo skills for building, and specialist
   subagents only for design questions that need them. Add process only when a real
   failure shows it is needed.

## Scope

In scope:
- the `maxdev` CLI and MCP server;
- every artifact type in `maxdev/registry.yaml`;
- the predeployment that makes an environment REST-ready;
- the ticket engine (`skills/maximo-dev-engine/`);
- the TMG automation-script standards.

Not in scope:
- CI/CD, pipelines or automatic promotion beyond development environments;
- managing credentials (users own `environments/.env.*`);
- loading seed or demo data nobody asked for;
- bulk copies of IBM out-of-the-box configuration into Git.

## What is committed

TMG-authored work only: tooling, skills, the predeployment, and the files a ticket's
manifest names (`tools/track_work.py`). Environment extracts stay out of Git
(`src/**` is ignored). Client configuration, credentials and tenant hostnames are never
committed.

## Ownership

Proprietary to TheMaximoGuys LLC (see `LICENSE`). Connecting to Maximo requires a
TheMaximoGuys licence key.
