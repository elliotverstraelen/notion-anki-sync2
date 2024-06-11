# Notion Toggles Sync

It's an [Anki](https://apps.ankiweb.net/) addon that loads toggle lists from [Notion](https://notion.so) as notes to specified decks and keeps them syncronized.

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Codestyle: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## How it works

Short demo and configuration how-to: [YouTube link](https://www.youtube.com/watch?v=5juto4BQSYc)

![TLDR](tldr.png)

- You provide a set of Notion page ids to export
- Every "toggle list" block from Notion will be converted to an Anki note
- Title of the toggle block will become the front side and its content — the backside
- The line starting with `#tags` will be parsed as tags
- Ignore toggles by putting symbol ❕ in front of a toggle title (type ":!" in Notion and select the white one)

Clozes can be added via `code` blocks in toggle titles. Backside will be
ignored (apart from tags).

Synchronization can work in the background or can be triggered manually from the `Notion` submenu in the `Tools`
section. Note that background sync **does not remove** any notes; if you want to remove the obsolete notes, then
trigger `Load and remove obsolete` from the submenu.

## Requirements

### Notion API token

To get **Notion API token** log in to Notion via a browser (assuming Chrome here),
then press `Ctrl+Shift+I` to open Developer Tools, go to the "Application" tab
and find `token_v2` under Cookie on the left.

### Notion page ids

To get **Notion page id** open up the page in a browser and look at the
address bar. 32 chars of gibberish after a page title is the page id:
`https://www.notion.so/notion_user/My-Learning-Book-8a775ee482ab43732abc9319add819c5`
➡ `8a775ee482ab43732abc9319add819c5`

Edit plugin config file from Anki: `Tools ➡ Add-ons ➡ Notion Toggles Loader ➡ Config`
```json
{
  "debug": false,
  "sync_every_minutes": 30,
  "anki_target_deck": "Notion Sync",
  "notion_token": "<your_notion_token_here>",
  "notion_namespace": "<your_notion_username_here>",
  "notion_pages": [
    {
      "page_id": "<page_id1>",
      "recursive": false,
      "target_deck": "Math"
    },
    {
      "page_id": "<page_id2>",
      "recursive": true,
      "target_deck": "Biology"
    }
  ]
}
```

## Known issues & limitations

Behind the scenes, the addon initiates Notion pages export to HTML, then parses the HTML into notes. Since non-public
Notion API is used, the addon may break without a warning.

- As for now, LaTeX and plain text cannot be used in the same cloze: Notion puts them in separate `code` tags which
  leads to the creation of two cloze blocks.

- Some toggle blocks are empty on export which leads to empty Anki notes. The issue is on the Notion side (and they're
  aware of it).

## TODO:

- Add option to use headers (H1, H2, H3) as hierarchy to build subdecks
- Allow users to define custom note types in Anki and map different Notion blocks to these custom note types.
- Implement a bi-directional sync that not only pulls data from Notion to Anki but also pushes updates from Anki back to Notion (for hot fixes furing learning).
- Enhance error handling and provide detailed error reports to the user, including suggestions for resolving common issues like when deck names or IDs dont match
- Add option to add tags to headers preceding the toggles that apply to all the toggles undernearth (to avoid having to add them manually)
  
## Configuration parameters

- `debug`: `bool [default: false]` — enable debug logging to file.
- `sync_every_minutes`: `int [default: 30]` — auto sync interval in minutes. Set to 0 to disable auto sync.
- `anki_target_deck`: `str [default: "Notion Sync"]` —  the default deck loaded notes will be added to, if not specified in the notion pages.
- `notion_token`: `str [default: None]` — Notion APIv2 token.
- `notion_namespace`: `str [default: None]` — Notion namespace (your username) to form source URLs.
- `notion_pages`: `array [default: [] ]` — List of Notion pages to export notes from.

Additional Information
This fork is based on the unmaintained [notion-toggles loader](https://github.com/9dogs/notion-anki-sync) plugin. The enhancements are intended to provide added functionality to the original plugin.

This project is inspired by a great [Notion to Anki](https://github.com/alemayhu/Notion-to-Anki).
