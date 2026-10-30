# Oxypro Project Library

One shared library of Oxypro Electromechanical's projects: project details and photos, presentation sheets, QA/QC (the Project Quality Plan hand-off to PQP Maker and each project's Method Statement Log) and HSE (the hand-off to HSE Plan Maker).

**Use the app:** [Oxypro Project Library on Claude](https://claude.ai/artifact/T3U712ufURSuMQTfsGDkMy) (shared as "Anyone with the link")
**Version:** 1.13.0 (30 Oct 2026)
**Developed by** Mark Lontoc | Dubai, United Arab Emirates | © 2026 MLWorks. All rights reserved.

This repository holds the source code and the GitHub edition website. The app runs as a Claude artifact: its project list, photos and MSRA Logs live in the artifact's shared database and storage.

## GitHub edition

`docs/` is the same Library as a plain website that runs without Claude, for GitHub Pages:

- The projects, photos and company logos are a copy of the library as of 30 Oct 2026 (`github/snapshot.json`, `docs/photos/`). They are read-only here: no Add, Import, Edit or photo upload. Changes are made in the Claude library and copied here with a new snapshot.
- Presentations (PDF, PowerPoint), Export to Excel, QA/QC (PQP details and file, the MSRA Log) and HSE all work. MSRA Logs are saved in the visitor's browser on that device; Save as gives the Excel or PDF to keep or share. Print opens the PDF in a new tab.
- `src/github/runtime.js` stands in for Claude's runtime (`window.claude`); the page code is the same as the Claude edition.

**Online with GitHub Pages:** `https://markwendelllontocdotcom.github.io/Oxypro-Project-Library/`. Pages publishes `main` from the repository root, where `index.html` opens `docs/` (the Library); with the folder set to `/docs` the same address opens the Library directly. GitHub Pages needs a public repository on a free account (a paid plan for a private one). The website itself can be opened by anyone who has its address.

**To refresh the copy:** read the live projects, add new photos to `github/photos/<asset id>.jpg`, update `github/snapshot.json`, run `python3 build.py` and push.

## What it does

- **Projects:** search and filter by emirate, status and sector. Each project shows its details from the Projects Master List and up to five photos.
- **Presentations:** select one or more projects for a top sheet (four designs), an Oxypro Project Presentation Sheet per project and a summary page, as PDF or PowerPoint. View / Present runs them full screen first.
- **QA/QC:** a menu on each project with **PQP details and file**, the **MSRA Log** and **Generate MSRA**.
- **Generate MSRA:** saves `MS Project - <code> - <name>.json`, a whole project for the Oxypro MSRA Generator (its project file format, version 1): the project name, code, emirate, client, consultant (the lead consultant, or the MEP consultant; a choice when there are both), main contractor and MEP contractor in capitals, the client, consultant and main contractor logos (PNG, up to 700 px), a cover photo of your choice and the Generator's standard list of 76 Method Statements (`build/msra-gen-std.json`, from its repository data). In the Generator: **Open project** (it replaces the project open there). The two apps are not linked: the file is the hand-off.
- **Company logos:** one logo per company (client, consultant, contractor), shown on every project with that company; editors add, replace or remove them on the project.
- **PQP details and file:** opens [PQP Maker](https://markwendelllontocdotcom.github.io/MEP-PQP-Maker/) with the project's PQP already created (the cover photo goes by copy and paste), or saves a PQP file.
- **HSE:** sends the project's details to HSE Plan Maker for the Project HSE Plan, with the main photo, another library photo or no photo as the cover. **Save HSE Plan file** saves them as `<code> - <name> - HSE Plan details.json`; in HSE Plan Maker choose Import project and pick the file. **Open in HSE Plan Maker** opens [HSE Plan Maker](https://markwendelllontocdotcom.github.io/HSE-Plan-Maker/) with the project in its link and copies the cover photo: HSE Plan Maker asks you to paste it (Ctrl+V), as PQP Maker does.
- **MSRA Log:** each project's Method Statement Submittal Log in the Oxypro template (The Borough): Summary, seven discipline logs (MEC, PLU, ELE, ELV, FF, LPG, MEP), the planner's MSL and the master list. Start from the standard list of 72 method statements, the project's MSL or an empty log; edit, save to the library, save as Excel or PDF and print. Set in Open Sans.
- **Master List:** add projects, import from the Projects Master List (Excel) and export the whole list in the same layout.
- **View:** Light, Dark or Auto. The PROJECT LIBRARY title goes back to the list from any page. About explains the app and lists the changes.
- **Icon:** the Oxypro Library open book, used for the browser tab, the home-screen shortcut and About (the book alone at 16 to 32 px, where the words cannot be read).

## Who can do what

- Anyone with the link can view projects, make presentations and download files.
- The artifact's owner and editors can add and change projects, photos and MSRA Logs.
- Claude cannot open the print window, so Print makes a print-ready PDF.

## Repository layout

| Path | What it is |
|---|---|
| `src/library.html` | The Library page (HTML, CSS and JavaScript in one file) with placeholders for the embedded assets |
| `src/msra/` | The MSRA Log: `core.js` (standard list, counts, MSL reading and matching), `xlsx.js` (Excel in the template layout, ExcelJS), `pdf.js` (PDF, jsPDF + AutoTable), `ui.js` (the page), `msra.css` |
| `build.py` | Builds `dist/Oxypro Project Library.html` (Claude) and `docs/` (GitHub edition): inlines the logos, fonts, MSRA code and the MSRA standard |
| `build/assets.json` | Logos (light and dark) and the sheet fonts Caladea and Carlito, base64 |
| `build/app-icon-512.png`, `build/app-icon.json`, `build/favicon.ico` | The app icon (512 px), its 32, 128 and 180 px versions (base64) and the website's favicon |
| `build/msra-assets.json` | The MSRA standard (72 method statements and The Borough's material list), the Oxypro logo used in the log and Open Sans (regular and bold), base64 |
| `dist/` | The built page, as published to Claude |
| `docs/` | The GitHub edition website: `index.html`, `photos/`, `logos/`, `.nojekyll` and the icons `favicon.ico`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` (built by `build.py`) |
| `src/github/runtime.js` | The GitHub edition's stand-in for Claude's runtime: snapshot projects, MSRA Logs in the browser, downloads |
| `github/snapshot.json` | The projects copied from the live library for the GitHub edition |

## Build and publish

```
python3 build.py
```

Then publish `dist/Oxypro Project Library.html` to the same Claude artifact (same link). The artifact declares the capabilities `db`, `assets`, `downloads` and `user`.

Shared data in the artifact's database:

- `projects/<project no.>`: the project details and `photos` (five slots of `{id, x, y}` or null)
- `settings/cover`, `settings/columns`, `settings/summary`: library-wide settings
- `mslogs/<project no.>`: the whole MSRA Log; `mslogmeta/<project no.>`: `{no, n, updatedAt}` for the project list
- `logos/<company key>`: `{name, id, w, h, updatedAt}`, one per company (key = the name in lower case without punctuation or endings such as LLC / Co.; the image in the asset store)

Libraries are loaded from cdnjs when first needed: jsPDF 2.5.1, PptxGenJS 3.12.0, SheetJS 0.18.5, ExcelJS 4.4.0 and jsPDF-AutoTable 3.8.4. Page fonts: Barlow and Barlow Condensed (Google Fonts).

## Credits

Fonts: Barlow; Caladea (Apache 2.0) and Carlito (SIL OFL) on the presentation sheets; Open Sans by Steve Matteson (SIL OFL) in the MSRA Log. Built with jsPDF, jsPDF-AutoTable, PptxGenJS, SheetJS and ExcelJS.
