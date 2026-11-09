"""Build the DivAlarm site pages.

    python _src/site/build.py            # run from the DEPLOY folder

1. Home (index.html) and Features (features.html) for en and ko, from the templates and
   copy in this folder.
2. The shared header, footer and theme on every other page in every locale
   (apply_chrome.py), so the navigation is the same everywhere.

Other locales get the new home and features layouts when translate_deploy_locales.py
regenerates them from en/. Run this script again afterwards to restore the localized
header and footer.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import apply_chrome  # noqa: E402
import features  # noqa: E402
import home  # noqa: E402

BUILT_LANGS = sorted(apply_chrome.BUILT_LANGS)

if __name__ == "__main__":
    for lang in BUILT_LANGS:
        home.build(lang)
        features.build(lang)
        print(f"{lang}: index.html, features.html")
    apply_chrome.main()
