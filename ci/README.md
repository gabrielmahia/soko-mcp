# CI Workflow

The `publish.yml` file in this directory needs to be moved to `.github/workflows/`
to activate PyPI publishing via GitHub Actions.

**One-time manual step (requires `workflows` scope on GitHub token):**

```bash
mkdir -p .github/workflows
cp ci/publish.yml .github/workflows/publish.yml
git add .github/workflows/publish.yml
git commit -m "ci: activate PyPI publish workflow"
git push
```

Or via GitHub UI:
1. Go to github.com/gabrielmahia/soko-mcp/new/main/.github/workflows
2. Filename: publish.yml
3. Paste the contents of ci/publish.yml

After the workflow is active, release with:
```bash
git tag v0.1.0 && git push origin v0.1.0
```
