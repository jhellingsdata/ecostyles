"""Font utilities for registering and managing custom fonts."""

import os
import importlib.resources
import shutil
import tempfile
import vl_convert as vlc

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
    temp_font_dir = os.path.join(tempfile.gettempdir(), 'ecostyles_fonts')
    os.makedirs(temp_font_dir, exist_ok=True)
    
    # Get the package's font directory
    with importlib.resources.path('ecostyles.data.fonts', 'circular-std') as font_path:
        # Copy all font files to the temporary directory
        for font_file in os.listdir(font_path):
            src = os.path.join(font_path, font_file)
            dst = os.path.join(temp_font_dir, font_file)
            if not os.path.exists(dst):  # Only copy if doesn't exist
                shutil.copy2(src, dst)
    
    # Register the font directory with vl-convert
    vlc.register_font_directory(temp_font_dir)
    
    return temp_font_dir