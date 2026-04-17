# Databricks app deployment

This directory is the source of truth for the Databricks app deployment.
It replaces the older `databricks/build` workflow, which drifted from the main
application and was excluded by the repo-level `build/` ignore rules.

## What changed

- `databricks/` is now the bundle root.
- The bundle syncs both the app directory and `../src` so the app can reuse the
  shared evaluator logic.
- The bundle writes to a stable shared workspace path:
  `/Workspace/Shared/apps/caltrans-pde-app/default/files`
- The Databricks app now imports the current evaluator APIs and builds the Excel
  output with `build_evaluation_excel`.

## Workspace deployment

Run the workspace deployment helper from this directory:

```bash
./scripts/deploy_workspace.sh
```

What it does:

- validates the bundle
- creates the shared workspace folder if needed
- grants the app service principal `CAN_READ` on the shared app folder
- deploys the app with `databricks bundle deploy`
- lists the synced source directory for a quick verification pass

## Git-backed deployment

Configure the app to use the Git repository metadata for Git-based deployments:

```bash
./scripts/configure_git_source.sh
```

This updates the app with:

- repository URL: `https://github.com/LLM-AI-INDIA/Caltrans-AI-.git`
- provider: `gitHub`

After that, redeploy from Git in the Databricks Apps UI and use:

```bash
branch: main
source code path: databricks
```

## Validation checklist

- `databricks bundle validate`
- `python3 -m py_compile databricks/app.py`
- `databricks apps get caltrans-pde-app -o json`
- `databricks workspace list /Workspace/Shared/apps/caltrans-pde-app/default/files`
