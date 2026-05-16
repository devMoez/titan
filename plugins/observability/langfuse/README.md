# Langfuse Observability Plugin

This plugin ships bundled with Titan but is **opt-in** — it only loads when
you explicitly enable it.

## Enable

Pick one:

```bash
# Interactive: walks you through credentials + SDK install + enable
Titan tools  # → Langfuse Observability

# Manual
pip install langfuse
Titan plugins enable observability/langfuse
```

## Required credentials

Set these in `~/.Titan/.env` (or via `Titan tools`):

```bash
Titan_LANGFUSE_PUBLIC_KEY=pk-lf-...
Titan_LANGFUSE_SECRET_KEY=sk-lf-...
Titan_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or your self-hosted URL
```

Without the SDK or credentials the hooks no-op silently — the plugin fails
open.

## Verify

```bash
Titan plugins list                 # observability/langfuse should show "enabled"
Titan chat -q "hello"              # then check Langfuse for a "Titan turn" trace
```

## Optional tuning

```bash
Titan_LANGFUSE_ENV=production       # environment tag
Titan_LANGFUSE_RELEASE=v1.0.0       # release tag
Titan_LANGFUSE_SAMPLE_RATE=0.5      # sample 50% of traces
Titan_LANGFUSE_MAX_CHARS=12000      # max chars per field (default: 12000)
Titan_LANGFUSE_DEBUG=true           # verbose plugin logging
```

## Disable

```bash
Titan plugins disable observability/langfuse
```

