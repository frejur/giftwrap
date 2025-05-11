giftwrap
========

A Maya script for creating gift wrap animations.

### Functionality
1. (Re-orient object to be wrapped).
2. Create paper mesh.
3. Animate folds and ribbon.
4. (Export as alembic geo cache)

### Installation (As a module)
- Copy the contents of `src`  to a directory pointed to by the `MAYA_MODULE_PATH` environment variable, e.g.
  * `\Users\<username>\Documents\maya\modules`           (Windows)
  * `\$HOME/Library/Preferences/Autodesk/maya/modules`    (Mac)
  * `\$HOME/maya/modules`                                 (Linux)

  _<sup><sub>(Run `getenv MAYA_MODULE_PATH` in Maya to print the exact paths available)</sup></sub>_

### Usage
```python
import giftwrap
giftwrap.ui.windowUI() # Brings up the UI
```

### Compatibility
Tested using Autodesk Maya 2026 (Windows 11).
