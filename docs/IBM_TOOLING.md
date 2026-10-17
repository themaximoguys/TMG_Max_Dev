# IBM and community tooling for Maximo development

Researched 2026-10-16. Each item says what it is, what is verified, and how it relates to this repo.

## IBM

| Tool | What it is | Relevance to this repo |
|---|---|---|
| **Maximo MCP server (MAS 9.2)** — [IBM docs](https://www.ibm.com/docs/en/masv-and-l/cd?topic=developing-maximo-mcp-server-overview) | `<instance>-mcp` pod, JSON-RPC over HTTP with SSE responses. Accepts an apikey or a JWT. Manage drives the tool list (AI config tools in MAXAICFGTOOL, object structures, scripts, workflows, API routes). | Supported as a client: `maxdev ibm-mcp tools/call`, the MCP tools `ibm_mcp_tools`/`ibm_mcp_call`, and the `ibm-maximo-mcp` entry in `.mcp.json`. The feature set is partial, and the exact route and tool names need testing on your 9.2 tenant. |
| **MAF Local Dev Mode** (early access) — [ibm-mas.github.io/maf-local-dev-mode](https://ibm-mas.github.io/maf-local-dev-mode/), [GitHub](https://github.com/ibm-mas/maf-local-dev-mode) | VS Code / **IBM Bob** extension for Application Configuration: live preview and XML diff. Needs MAS 9.1.21+ or 9.2.1+ and Node 20+. | Use it for the MAF apps in `src/18-mobile/maf-apps`. maxdev doesn't replace it. |
| **Bob-driven Integration for Maximo via MCP** — [GitHub](https://github.com/ibm-self-serve-assets/Bob-driven-Integration-for-Maximo-via-MCP) | IBM self-serve demo: an MCP server over MXAPIJOBPLAN with 4 tools. | Pattern reference only. It ships with SSL verification turned off. |
| **Maximo + watsonx Orchestrate** — [GitHub](https://github.com/IBM/maximo-wxo-integration), [tutorial](https://developer.ibm.com/tutorials/create-maximo-agent-watsonx-orchestrate/) | Reference architecture and ADK for Maximo agents. | Not needed for development; useful if TMG builds agents. |
| **Manage REST API guide** — [ibm-maximo-dev.github.io/maximo-restapi-documentation](https://ibm-maximo-dev.github.io/maximo-restapi-documentation/) | The authoritative API reference: query, bulk, actions, admin mode, `/dm/*`, OAS at `/maximo/oas3/api.html`. | The source for `maxdev/client.py` and `maxdev/admin.py`. |
| **Autoscript guide** — [ibm-maximo-dev.github.io/maximo-autoscript-documentation](https://ibm-maximo-dev.github.io/maximo-autoscript-documentation/) | Launch points, implicit variables, REST script handlers. | Used alongside the TMG standards. |
| **MAF configuration practices** — [ibm-maximo-dev.github.io/configuration-practices-documentation](https://ibm-maximo-dev.github.io/configuration-practices-documentation/overview/) | Supported customisation points for app.xml and AppCustomizations.js. | Read before any MAF work. |
| **ibm-mas/cli**, **ansible-devops** | Install and operate MAS. | Platform only; not used for configuration. |

**About "IBM Bob":** it is IBM's AI coding assistant/IDE. Two IBM projects target it for Maximo: MAF Local Dev Mode and the Bob MCP demo. I found no IBM Bob tooling for automation scripts or config-as-code. That gap is what this repo covers, and its MCP server works with any MCP client, Bob included.

## Community

| Tool | Notes |
|---|---|
| Naviam (ex-Sharptree) **Maximo Development Tools** — [GitHub](https://github.com/naviam-io/vscode-autoscript-deploy), npm `maximo-dev-tools` | Mature VS Code/CLI deploy for scripts, screens, forms and reports. Installs `NAVIAM.AUTOSCRIPT.*` scripts on the server. Its `scriptConfig` uses a different key set from TMG's, so pick one tool per script. |
| markusvankempen/maximo-mcp-ai-integration-options | Generic query/CRUD MCP (9 tools). |
| themaximoguys/Max_mcp | TMG's own broader MCP. Can run alongside `tmg-maximo-dev`. |

## Claude tooling in this repo

- Project skills, loaded automatically from `.claude/skills/`:
  - `maximo-dev`: how to use this repo
  - `create-automation-script`
  - `convert-java-to-script`
  - `convert-trm-to-script`
  - `maximo-workflow`
- To write new skills, use the **skill-creator** skill, which is installed in this Claude Code session.
