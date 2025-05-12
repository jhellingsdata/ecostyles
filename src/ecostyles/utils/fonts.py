"""Font utilities for registering and managing custom fonts."""

from pathlib import Path
from tempfile import mkdtemp
import shutil
import sys
import vl_convert as vlc

# ---------------------------------------------------------------------------
# importlib.resources – stdlib ≥ 3.10 already has the namespace-package fix;
# for 3.9 we fall back to the back-port.
# ---------------------------------------------------------------------------
if sys.version_info < (3, 10):
    import importlib_resources as resources          # back-port ≥ 6.4 handles NS pkgs
else:
    from importlib import resources                  # stdlib

_FONT_EXTS = {".ttf", ".otf"}

def setup_fonts():
    """
    Set up the Circular Std fonts for use with vl-convert.
    
    This function:
    1. Creates a temporary directory for fonts
    2. Copies the package's font files to the temporary directory
    3. Registers the font directory with vl-convert
    
    Returns:
        str: Path to the temporary font directory
    """
    # Create a temporary directory for fonts
    tmp_dir = Path(mkdtemp(prefix="ecostyles_fonts_"))


    # Traversable pointing at …/data/fonts/circular-std
    circular_std_dir = (
        resources.files("ecostyles.data")
        .joinpath("fonts")
        .joinpath("circular-std")
    )

    # as_file() guarantees a real on-disk path even if we're inside a wheel
    with resources.as_file(circular_std_dir) as fs_path:
        # copy *all* font files in that subtree
        for fp in fs_path.rglob("*"):
            if fp.suffix.lower() in _FONT_EXTS:
                shutil.copy2(fp, tmp_dir / fp.name)

    # Tell vl-convert where those fonts live
    vlc.register_font_directory(str(tmp_dir))
    
    return tmp_dir