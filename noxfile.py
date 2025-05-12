import nox

@nox.session(venv_backend="conda", python=["3.9", "3.10", "3.11"])
def test(session):
    session.install(".[test]")      # install our package and test requirements
    session.run("pytest", "-q")