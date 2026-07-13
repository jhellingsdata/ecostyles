# Releasing ecostyles

This project uses **automated testing and publishing** via GitHub Actions. This guide
explains the whole flow and, importantly, the one-time setup you need to do once.

## The mental model

There are two separate ideas — keep them distinct:

| Action | What it means | Who sees it |
| --- | --- | --- |
| **Push** (commit / branch) | Save work to GitHub | You + anyone installing from that branch |
| **Release** (version tag) | Cut a versioned build and publish it to PyPI | Everyone who `pip install ecostyles` |

Day to day you push freely. A **release only happens when a version tag** (e.g. `v0.2.0`)
is pushed — and you create that tag with one command (`bump-my-version`), not by hand.

The version lives in **one place**: `[project] version` in `pyproject.toml`. At runtime
`ecostyles.__version__` reads it back from the installed package metadata, so there's no
second copy to keep in sync.

```
     you code            ┌── CI runs tests on every PR ──┐
  feature branch ─PR──▶ main ──────────────────────────────▶ (stable)
                                        │
                     bump-my-version bump minor   (edits version, commits, tags v0.2.0)
                                        │
                          git push --follow-tags
                                        │
                        Release workflow builds + publishes to PyPI
```

## Two workflows

- **`.github/workflows/ci.yml`** — runs the test suite (`pytest`) for
  every pull request and every push to `main`, on Python 3.10–3.14. This is your safety net
  before merging.
- **`.github/workflows/release.yml`** — triggers **only on a tag** matching `v*`. It builds
  the sdist + wheel with `uv build` and publishes them to PyPI.

---

## One-time setup (do this once)

### 1. PyPI Trusted Publishing (no API tokens)

We publish using PyPI's **Trusted Publishing** (OIDC): GitHub proves its identity to PyPI,
so there are **no passwords or tokens to store**. Because `ecostyles` isn't on PyPI yet,
add a *pending* publisher:

1. Log in to <https://pypi.org> → your account → **Publishing** → **Add a pending publisher**.
2. Fill in:
   - **PyPI project name:** `ecostyles`
   - **Owner:** `jhellingsdata`
   - **Repository name:** `ecostyles`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`
3. Save. The first successful release creates the project and "graduates" the publisher.

### 2. GitHub environment `pypi`

The release workflow publishes from a GitHub *environment* called `pypi` (this matches the
trusted-publisher config above and lets you gate releases):

1. GitHub repo → **Settings** → **Environments** → **New environment** → name it `pypi`.
2. (Recommended) Under **Deployment protection rules**, add **Required reviewers** (yourself).
   Then every publish waits for a one-click approval — a nice safety catch.

That's it. No secrets to add.

---

## Cutting a release (day to day)

1. Make sure `main` is green (CI passing) and checked out with a clean working tree.
2. Choose the bump size using [semantic versioning](https://semver.org):
   - `patch` — bug fixes only, no API change (`0.2.0 → 0.2.1`)
   - `minor` — new, backward-compatible features (`0.2.0 → 0.3.0`)
   - `major` — breaking changes (`0.2.0 → 1.0.0`); pre-1.0 we may still break in `minor`.
3. Run the bump (edits the version, commits `Release vX.Y.Z`, and creates the `vX.Y.Z` tag):
   ```bash
   uv run bump-my-version bump minor        # or patch / major
   ```
   Preview first with `--dry-run --verbose` if you want to see exactly what it will do.
4. Push the commit **and** the tag:
   ```bash
   git push --follow-tags
   ```
5. Watch **Actions** → *Release*. If you enabled required reviewers, approve the `pypi`
   deployment. When it's green, the version is live on PyPI.

Colleagues then upgrade with `pip install -U ecostyles` (once the first release is published),
or keep installing a specific tag from GitHub: `pip install git+https://github.com/jhellingsdata/ecostyles.git@v0.2.0`.

## Troubleshooting

- **"Git working directory is not clean"** — commit or stash changes first; `bump-my-version`
  refuses to run on a dirty tree by default (a safety feature).
- **Release workflow didn't start** — it only runs on tags. Confirm the tag pushed:
  `git push --follow-tags` (a plain `git push` does *not* push tags).
- **PyPI publish rejected (trusted publisher)** — re-check the pending-publisher fields match
  exactly: repo `jhellingsdata/ecostyles`, workflow `release.yml`, environment `pypi`.
- **Yank a bad release** — you cannot overwrite a version on PyPI. Bump to a new patch and
  release again; optionally "yank" the bad version in the PyPI UI.
