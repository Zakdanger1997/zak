# Bun Commands Reference

A quick reference for the [Bun](https://bun.com/docs) CLI — a fast JavaScript runtime, package manager, bundler, and test runner. Based on Bun **1.4.0**.

```
Usage: bun <command> [...flags] [...args]
```

For detailed help on any command, run:

```sh
bun <command> --help
```

---

## Running Code

| Command | Example | Description |
|---------|---------|-------------|
| `bun run` | `bun run ./my-script.ts` | Execute a JavaScript/TypeScript file with Bun |
| `bun run` | `bun run lint` | Run a script defined in `package.json` |
| `bun test` | `bun test` | Run unit tests with Bun's built-in test runner |
| `bun x` (`bunx`) | `bunx next` | Execute a package binary (CLI), installing it if needed |
| `bun repl` | `bun repl` | Start an interactive REPL session |
| `bun exec` | `bun exec "echo hi"` | Run a shell script directly with Bun's shell |

### Notes

- `bun run <file>` supports TypeScript and JSX out of the box — no build step or config needed.
- `bun run <script>` looks up the script name in `package.json` (like `npm run`), e.g. `bun run lint`.
- `bunx` is the equivalent of `npx`: it runs a package's CLI without permanently adding it to your project.

---

## Package Management

| Command | Alias | Example | Description |
|---------|-------|---------|-------------|
| `bun install` | `bun i` | `bun install` | Install dependencies for a `package.json` |
| `bun add` | `bun a` | `bun add @remix-run/dev` | Add a dependency to `package.json` |
| `bun remove` | `bun rm` | `bun remove babel-core` | Remove a dependency from `package.json` |
| `bun update` | — | `bun update @evan/duckdb` | Update outdated dependencies |
| `bun audit` | — | `bun audit` | Check installed packages for vulnerabilities |
| `bun outdated` | — | `bun outdated` | Display latest versions of outdated dependencies |
| `bun link` | — | `bun link [<package>]` | Register or link a local npm package |
| `bun unlink` | — | `bun unlink` | Unregister a local npm package |
| `bun publish` | — | `bun publish` | Publish a package to the npm registry |
| `bun patch` | — | `bun patch <pkg>` | Prepare a package for patching |
| `bun pm` | — | `bun pm <subcommand>` | Additional package management utilities |
| `bun info` | — | `bun info @zarfjs/zarf` | Display package metadata from the registry |
| `bun why` | — | `bun why zod` | Explain why a package is installed |

### Common workflows

```sh
# Fresh install of all dependencies
bun install

# Add a runtime dependency
bun add zod

# Add a dev dependency
bun add -d typescript

# See why a package ended up in your tree
bun why zod

# Check for known vulnerabilities
bun audit
```

---

## Bundling

| Command | Example | Description |
|---------|---------|-------------|
| `bun build` | `bun build ./a.ts ./b.jsx` | Bundle TypeScript & JavaScript into a single file |

```sh
# Bundle an app entry point for the browser
bun build ./src/index.ts --outdir ./dist

# Create a single-file output
bun build ./cli.ts --compile --outfile mycli
```

---

## Project Scaffolding

| Command | Alias | Example | Description |
|---------|-------|---------|-------------|
| `bun init` | — | `bun init` | Start an empty Bun project from a built-in template |
| `bun create` | `bun c` | `bun create svelte` | Create a new project from a template |

---

## Maintenance & Misc

| Command | Example | Description |
|---------|---------|-------------|
| `bun upgrade` | `bun upgrade` | Upgrade to the latest version of Bun |
| `bun feedback` | `bun feedback ./file1 ./file2` | Send feedback (and optional files) to the Bun team |

---

## Cheat Sheet: npm → Bun

| npm | Bun equivalent |
|-----|----------------|
| `npm install` | `bun install` |
| `npm install <pkg>` | `bun add <pkg>` |
| `npm install -D <pkg>` | `bun add -d <pkg>` |
| `npm uninstall <pkg>` | `bun remove <pkg>` |
| `npm update` | `bun update` |
| `npm run <script>` | `bun run <script>` |
| `npm test` | `bun test` |
| `npx <cli>` | `bunx <cli>` |
| `npm init` | `bun init` |
| `npm publish` | `bun publish` |
| `npm audit` | `bun audit` |
| `npm outdated` | `bun outdated` |
| `npm link` | `bun link` |

---

## Learn More

- Documentation: <https://bun.com/docs>
- Discord community: <https://bun.com/discord>
