# notebooks/

Exploratory and manual-testing notebooks — a scratch space for trying out themes,
helper methods, and chart ideas as we develop `ecostyles`.

Notebooks placed **here** are tracked by git (see `.gitignore`), so keep them tidy:
prefer small, self-contained, re-runnable examples. Scratch notebooks created elsewhere
in the repo are ignored by default.

Suggested workflow:

```python
from ecostyles import EcoStyles
styles = EcoStyles()
styles.register_and_enable_theme("cotd")   # or "article", "newsletter"
# ... build and display charts ...
```

For reusable chart specifications used to test themes, see [`../specs/`](../specs/).
