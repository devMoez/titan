---
sidebar_position: 3
title: "Updating & Uninstalling"
description: "How to update Titan Agent to the latest version or uninstall it"
---

# Updating & Uninstalling

## Updating

### Git installs

Update to the latest version with a single command:

```bash
Titan update
```

This pulls the latest code from `main`, updates dependencies, and prompts you to configure any new options that were added since your last update.

### pip installs

PyPI releases track **tagged versions** (major and minor releases), not every commit on `main`. Check for updates and upgrade with:

```bash
Titan update --check    # see if a newer release is on PyPI
Titan update            # runs pip install --upgrade titan-agent
```

Or manually:

```bash
pip install --upgrade titan-agent    # or: uv pip install --upgrade titan-agent
```

:::tip
`Titan update` automatically detects new configuration options and prompts you to add them. If you skipped that prompt, you can manually run `Titan config check` to see missing options, then `Titan config migrate` to interactively add them.
:::

### What happens during an update (git installs)

When you run `Titan update`, the following steps occur:

1. **Pairing-data snapshot** — a lightweight pre-update state snapshot is saved (covers `~/.Titan/pairing/`, Feishu comment rules, and other state files that get modified at runtime). Recoverable via the snapshot restore flow described under [Snapshots and rollback](../user-guide/checkpoints-and-rollback.md), or by extracting the most recent quick-snapshot zip Titan wrote next to your `~/.Titan/` directory.
2. **Git pull** — pulls the latest code from the `main` branch and updates submodules
3. **Dependency install** — runs `uv pip install -e ".[all]"` to pick up new or changed dependencies
4. **Config migration** — detects new config options added since your version and prompts you to set them
5. **Gateway auto-restart** — running gateways are refreshed after the update completes so the new code takes effect immediately. Service-managed gateways (systemd on Linux, launchd on macOS) are restarted through the service manager. Manual gateways are relaunched automatically when Titan can map the running PID back to a profile.

### Preview-only: `Titan update --check`

Want to know if an update is available before pulling? Run `Titan update --check` — for git installs it fetches and compares commits against `origin/main`; for pip installs it queries PyPI for the latest release. No files are modified, no gateway is restarted. Useful in scripts and cron jobs that gate on "is there an update".

### Full pre-update backup: `--backup`

For high-value profiles (production gateways, shared team installs) you can opt into a full pre-pull backup of `Titan_HOME` (config, auth, sessions, skills, pairing):

```bash
Titan update --backup
```

Or make it the default for every run:

```yaml
# ~/.Titan/config.yaml
updates:
  pre_update_backup: true
```

`--backup` was the always-on behavior in earlier builds, but it was adding minutes to every update on large homes, so it's now opt-in. The lightweight pairing-data snapshot above still runs unconditionally.

Expected output looks like:

```
$ Titan update
Updating Titan Agent...
📥 Pulling latest code...
Already up to date.  (or: Updating abc1234..def5678)
📦 Updating dependencies...
✅ Dependencies updated
🔍 Checking for new config options...
✅ Config is up to date  (or: Found 2 new options — running migration...)
🔄 Restarting gateways...
✅ Gateway restarted
✅ Titan Agent updated successfully!
```

### Recommended Post-Update Validation

`Titan update` handles the main update path, but a quick validation confirms everything landed cleanly:

1. `git status --short` — if the tree is unexpectedly dirty, inspect before continuing
2. `Titan doctor` — checks config, dependencies, and service health
3. `Titan --version` — confirm the version bumped as expected
4. If you use the gateway: `Titan gateway status`
5. If `doctor` reports npm audit issues: run `npm audit fix` in the flagged directory

:::warning Dirty working tree after update
If `git status --short` shows unexpected changes after `Titan update`, stop and inspect them before continuing. This usually means local modifications were reapplied on top of the updated code, or a dependency step refreshed lockfiles.
:::

### If your terminal disconnects mid-update

`Titan update` protects itself against accidental terminal loss:

- The update ignores `SIGHUP`, so closing your SSH session or terminal window no longer kills it mid-install. `pip` and `git` child processes inherit this protection, so the Python environment cannot be left half-installed by a dropped connection.
- All output is mirrored to `~/.Titan/logs/update.log` while the update runs. If your terminal disappears, reconnect and inspect the log to see whether the update finished and whether the gateway restart succeeded:

```bash
tail -f ~/.Titan/logs/update.log
```

- `Ctrl-C` (SIGINT) and system shutdown (SIGTERM) are still honored — those are deliberate cancellations, not accidents.

You no longer need to wrap `Titan update` in `screen` or `tmux` to survive a terminal drop.

### Checking your current version

```bash
Titan version
```

Compare against the latest release at the [GitHub releases page](https://github.com/NousResearch/titan-agent/releases).

### Updating from Messaging Platforms

You can also update directly from Telegram, Discord, Slack, WhatsApp, or Teams by sending:

```
/update
```

This pulls the latest code, updates dependencies, and restarts running gateways. The bot will briefly go offline during the restart (typically 5–15 seconds) and then resume.

### Manual Update

If you installed manually (not via the quick installer):

```bash
cd /path/to/titan-agent
export VIRTUAL_ENV="$(pwd)/venv"

# Pull latest code
git pull origin main

# Reinstall (picks up new dependencies)
uv pip install -e ".[all]"

# Check for new config options
Titan config check
Titan config migrate   # Interactively add any missing options
```

### Rollback instructions

If an update introduces a problem, you can roll back to a previous version:

```bash
cd /path/to/titan-agent

# List recent versions
git log --oneline -10

# Roll back to a specific commit
git checkout <commit-hash>
git submodule update --init --recursive
uv pip install -e ".[all]"

# Restart the gateway if running
Titan gateway restart
```

To roll back to a specific release tag:

```bash
git checkout v0.6.0
git submodule update --init --recursive
uv pip install -e ".[all]"
```

:::warning
Rolling back may cause config incompatibilities if new options were added. Run `Titan config check` after rolling back and remove any unrecognized options from `config.yaml` if you encounter errors.
:::

### Note for Nix users

If you installed via Nix flake, updates are managed through the Nix package manager:

```bash
# Update the flake input
nix flake update titan-agent

# Or rebuild with the latest
nix profile upgrade titan-agent
```

Nix installations are immutable — rollback is handled by Nix's generation system:

```bash
nix profile rollback
```

See [Nix Setup](./nix-setup.md) for more details.

---

## Uninstalling

### Git installs

```bash
Titan uninstall
```

The uninstaller gives you the option to keep your configuration files (`~/.Titan/`) for a future reinstall.

### pip installs

```bash
pip uninstall titan-agent
rm -rf ~/.Titan            # Optional — keep if you plan to reinstall
```

### Manual Uninstall

```bash
rm -f ~/.local/bin/Titan
rm -rf /path/to/titan-agent
rm -rf ~/.Titan            # Optional — keep if you plan to reinstall
```

:::info
If you installed the gateway as a system service, stop and disable it first:
```bash
Titan gateway stop
# Linux: systemctl --user disable Titan-gateway
# macOS: launchctl remove ai.Titan.gateway
```
:::

