# Site build (2026 design)

Run from the `DEPLOY` folder:

```
python _src/site/build.py
```

It does two things:

1. Builds `index.html` and `features.html` for `en` and `ko` from `home.html` / `features.html`
   (markup and page CSS) and `home.py` / `features.py` (copy). Charts are drawn by `charts.py`
   from `promo-data.json`, the same data as the marketing images in `DivAlarm 오토메이션/promo`.
2. Puts the shared header and footer (`chrome.py`) on every other page in every locale and
   loads the theme (`css/site.css`, `css/legacy-skin.css`, `js/site.js`). The older Webflow pages
   keep their content and scripts; only their navigation, footer, colors and type change.

It is safe to run repeatedly.

## Other languages

`en` is the source for the other locales. After `translate_deploy_locales.py` regenerates
them (from the `Site2` folder), run `python _src/site/build.py` again. It puts the localized
header and footer back on every page, including the translated home and features pages.
The translator keeps the footer's legal block because it carries `data-keep`.

The keyword alarm and PC connection guides are available in all 17 app languages, including
Traditional Chinese. The English HTML files define their structure, and the Korean pages are
maintained directly. Edit the other translations in `guide-copy/<locale>.json`. A key is an
English message. Numbered tags keep its links and emphasis attached to the translated words.
Keep the contents of code tags, TradingView placeholders, and diagnostic variables such as
`{0}` intact. Use `python -X utf8 _src/site/tradingview_guides.py --list-strings` to list
current source messages. Run `python _src/site/tradingview_guides.py` to regenerate just
these pages, then `python -m unittest discover -s _src/site` to check the guides.

## Copy rules

From `마케터/projects/divalarm/CLAUDE.md`:

- No profit or win-rate claims.
- Keep the method note next to the TradingView comparison.
- Auto-orders always come with the real-money, no-paper-mode notice.
- Referral rewards are always shown with their conditions.
- Don't claim that API keys are never stored on a server. The app syncs them today.
