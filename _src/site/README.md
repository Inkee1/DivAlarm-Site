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

## Copy rules

From `마케터/projects/divalarm/CLAUDE.md`:

- No profit or win-rate claims.
- Keep the method note next to the TradingView comparison.
- Auto-orders always come with the real-money, no-paper-mode notice.
- Referral rewards are always shown with their conditions.
- Don't claim that API keys are never stored on a server. The app syncs them today.
