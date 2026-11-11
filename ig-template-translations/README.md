# Spenser IG template

Extends `fhir2.base.template`, pinned on purpose, because it carries the page
layout and the language switcher, and ships interface text in Portuguese, Dutch
and French.

| File | What it does |
|---|---|
| `includes/fragment-css.html` | loads `content/assets/css/spenser.css` |
| `content/assets/css/spenser.css` | the colours, and the layout of the assembly guide |
| `includes/fragment-header.html` | the logo |
| `includes/fragment-footer.html` | the footer links |
| `content/assets/js/lang-redirects.js` | works around a bug in the base, see the file |
| `includes/fragment-language.html` | the base's file, reading the "Language" label from its catalogues rather than hardcoding it |
| `translations/stringsBase-*.po` | the base's interface text, with the link in the note on translated pages written as HTML, because the base does not render it as markdown |

The last three rows exist to work around the pinned base. Check whether they are still
needed each time it is updated.
