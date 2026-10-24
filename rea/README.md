# REA: Reverse Engineer Anything

Claude Code plugin packaging of [morluto/rea](https://github.com/morluto/rea), one MCP server for reverse engineering across binaries, applications, and runtime behavior.

See a feature in a shipped app and want to understand how it works, down to the binary level? REA gives Claude tools to inspect native binaries, JavaScript and Electron apps, .NET assemblies, Android APKs, firmware images, and websites without source code. Analysis runs locally, and results include the evidence and limitations behind each conclusion.

## What this plugin contains

| Component | Path | Purpose |
|-----------|------|---------|
| MCP server | `.mcp.json` | Launches the `rea-agents` npm package (`npx -y rea-agents@6.7.0 mcp`) over stdio |
| Skill | `skills/reverse-engineer-anything/` | REA's workflow instructions: when to use REA, how to pick a target, how to read Evidence, and how to recover from connection problems |

The skill and its `references/` folder are copied verbatim from the upstream repository's `.agents/skills/reverse-engineer-anything/` at REA 6.7.0 (commit `2250e67`). Upstream also ships contributor-only skills (tool design, CI audit, changelog) that depend on the REA source checkout; those are not included here.

## Requirements

- **Node.js and npm.** The MCP server is fetched and run with `npx`. See the upstream README for the supported Node.js range.
- **Linux:** a procps-compatible `ps` on `PATH` for process ownership checks (see upstream `docs/installation.md`, "Linux owned-process prerequisite").
- **Optional analysis engines.** Static JavaScript and Electron analysis needs nothing else. Native binary analysis uses an existing [Hopper](https://www.hopperapp.com/), [Ghidra](https://ghidra-sre.org/), or IDA installation. Android analysis needs JADX and Java.

## Installation

```
/plugin install rea --marketplace Zakdanger1997/zak
```

On older Claude Code releases, add the marketplace first and then install:

```
/plugin marketplace add Zakdanger1997/zak
/plugin install rea
```

Restart Claude Code. The `rea` MCP server starts with the session and the `rea:reverse-engineer-anything` skill becomes available.

## Usage

Ask Claude to investigate a shipped artifact, for example:

- "Use REA to explain how the auto-update check in this Electron app works."
- "Decompile the licensing routine in `./bin/app` and summarize what it validates."
- "Compare version 2.3 and 2.4 of this binary and tell me what changed in the network code."

The skill tells Claude to call REA only when a claim depends on a shipped binary, package, or runtime evidence. For ordinary source-repository analysis it falls back to normal repository tools.

## Configuration

Environment variables can be added to the `rea` entry in `.mcp.json`:

| Variable | Effect |
|----------|--------|
| `REA_MCP_INPUT_SCHEMA_PROFILE=full` | Advertise full input schemas instead of the compact default |
| `REA_MCP_MAX_RESPONSE_BYTES` | Cap the size of a single tool response |

To upgrade, change the pinned version in `.mcp.json` and `plugin.json`, then refresh the skill folder from upstream.

## Troubleshooting

If REA tools do not appear, run the upstream doctor without changing any configuration:

```bash
npx -y rea-agents@6.7.0 doctor --client claude_code --json
```

The skill's `references/connection-and-recovery.md` walks through the common blockers (missing registration, blocked tool call, missing engine, host timeout).

## License and attribution

REA is copyright (c) 2026 morluto and released under the MIT License. The upstream license is reproduced in [LICENSE](./LICENSE). Read the upstream [DISCLAIMER.md](https://github.com/morluto/rea/blob/main/DISCLAIMER.md) before analyzing software you do not own; you are responsible for complying with applicable laws and license terms.
