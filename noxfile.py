import nox

# Use uv to create the per-version virtualenvs (fast, and matches our dev workflow).
nox.options.default_venv_backend = "uv"


@nox.session(python=["3.9", "3.10", "3.11", "3.12", "3.13"])
def test(session):
    session.install("-e", ".[test]")
    session.run("pytest", "-q")
