# CLI runtime and output handling

External CLI examples are hints, not contracts. Validate the installed binary before relying on flags or output shape.

## Validate local CLI capabilities first

Before using a CLI option that has not already been verified in the current environment, run the local help command and inspect the supported flags:

```text
<cli> --help
```

For subcommands, inspect the relevant subcommand help as needed.

Do not assume that documentation, another machine, or a previous version matches the installed binary. In particular, verify flags such as `--cwd`, `--sandbox`, permission modes, and structured-output options before use.

If the execution tool already provides a working directory, prefer that tool-level `workdir` instead of adding a CLI-specific cwd flag unless the CLI explicitly requires one.

## Structured output is a transport envelope

Do not assume `--output-format json` means the top-level JSON is the requested business object.

Treat CLI output as layered transport data:

1. parse the outer JSON object;
2. inspect status/error metadata before trusting the payload;
3. locate the semantic payload field, commonly `result`;
4. if that field is a string containing a fenced block such as `````json ... `````, strip the fence;
5. parse the inner JSON only when the task requested structured JSON;
6. retain useful outer metadata such as model usage, cost, duration, service tier, session id, or errors.

Conceptually:

```text
stdout
  -> outer CLI JSON envelope
      -> metadata / usage / cost
      -> result
          -> optional markdown code fence
              -> business JSON or text
```

Never silently discard the outer envelope before recording execution metadata.

If the inner value is not valid JSON, treat it as text rather than forcing a parse.

## Record actual runtime identity and cost

The executable name is not the model identity. When output exposes runtime metadata, record the actual values returned by the service, for example:

```text
cli
actual_model
service_tier
cost_usd
usage
```

Do not infer `actual_model` from a command name such as `claude` or `agy`.

## Lightweight health checks and cost

Do not invoke a paid model merely to prove that a CLI binary exists.

Prefer, in order:

1. `<cli> --help` or version/help output;
2. a documented local/non-model diagnostic if available;
3. a minimal model-backed probe only when model connectivity itself must be verified.

A model-backed health check can have non-trivial cost even when the prompt is simple. If the task is tiny and delegation overhead or expected model cost is comparable to doing it directly in Codex, do not delegate solely for a health check.

When a model-backed probe is necessary, keep the prompt minimal and record the reported cost/usage.

## Windows path and encoding hygiene

External-agent text may pass through shells, JSON encoders, consoles, and model output. Non-ASCII Windows filenames can therefore become mojibake.

- Prefer UTF-8 structured output when the CLI supports it.
- Ask agents to return paths in structured fields rather than prose when possible.
- Preserve the raw returned path string for diagnostics.
- If a path contains replacement-looking text such as `锟斤拷`, do not assume that is the real filename; verify the path against the filesystem before using it for edits or conclusions.
- When exact filenames matter, have Codex/tooling enumerate the directory and reconcile the agent-reported path with the actual filesystem entry.
