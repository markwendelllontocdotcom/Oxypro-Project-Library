# Oxypro Project Library

One shared library of Oxypro Electromechanical's projects: project details and photos, presentation sheets, the Project Quality Plan hand-off to PQP Maker and each project's Method Statement Log.

**Use the app:** [Oxypro Project Library on Claude](https://claude.ai/artifact/T3U712ufURSuMQTfsGDkMy) (shared as "Anyone with the link")
**Version:** 1.10.2 (27 Oct 2026)
**Developed by** Mark Lontoc | Dubai, United Arab Emirates | © 2026 MLWorks. All rights reserved.

This repository holds the source code and history. The app runs as a Claude artifact: its project list, photos and MSRA Logs live in the artifact's shared database and storage, not here.

## What it does

- **Projects:** search and filter by emirate, status and sector. Each project shows its details from the Projects Master List and up to five photos.
- **Presentations:** select one or more projects for a top sheet (four designs), an Oxypro Project Presentation Sheet per project and a summary page, as PDF or PowerPoint. View / Present runs them full screen first.
- **PQP details and file:** opens [PQP Maker](https://markwendelllontocdotcom.github.io/MEP-PQP-Maker/) with the project's PQP already created (the cover photo goes by copy and paste), or saves a PQP file.
- **MSRA Log:** each project's Method Statement Submittal Log in the Oxypro template (The Borough): Summary, seven discipline logs (MEC, PLU, ELE, ELV, FF, LPG, MEP), the planner's MSL and the master list. Start from the standard list of 72 method statements, the project's MSL or an empty log; edit, save to the library, save as Excel or PDF and print. Set in Open Sans.
- **Master List:** add projects, import from the Projects Master List (Excel) and export the whole list in the same layout.
- **View:** Light, Dark or Auto. The PROJECT LIBRARY title goes back to the list from any page. About explains the app and lists the changes.

## Who can do what

- Anyone with the link can view projects, make presentations and download files.
- The artifact's owner and editors can add and change projects, photos and MSRA Logs.
- Claude cannot open the print window, so Print makes a print-ready PDF.

## Repository layout

| Path | What it is |
|---|---|
| `src/library.html` | The Library page (HTML, CSS and JavaScript in one file) with placeholders for the embedded assets |
| `src/msra/` | The MSRA Log: `core.js` (standard list, counts, MSL reading and matching), `xlsx.js` (Excel in the template layout, ExcelJS), `pdf.js` (PDF, jsPDF + AutoTable), `ui.js` (the page), `msra.css` |
| `build.py` | Builds `dist/Oxypro Project Library.html`: inlines the logos, fonts, MSRA code and the MSRA standard |
| `build/assets.json` | Logos (light and dark) and the sheet fonts Caladea and Carlito, base64 |
| `build/msra-assets.json` | The MSRA standard (72 method statements and The Borough's material list), the Oxypro logo used in the log and Open Sans (regular and bold), base64 |
| `dist/` | The built page, as published to Claude |
| `docs/project-notes.md` | Working notes: decisions, data layout, version history |
| `history/patches/` | The scripts that made each version from 1.1.0 to 1.10.2 (kept for history; they patch `src/library.html` in order) |
| `tests/msra/` | Node tests for the MSRA Log: MSL matching, the Excel workbook and the PDF |
| `tests/browser/` | Playwright scripts that ran the page with a mocked Claude runtime (paths point at the development machine; adjust before use) |
| `tools/msra/` | The standard list and The Borough MSL Ref as extracted from "Method Statement Log - The Borough R0.xlsx" |

## Build and publish

```
python3 build.py
```

Then publish `dist/Oxypro Project Library.html` to the same Claude artifact (same link). The artifact declares the capabilities `db`, `assets`, `downloads` and `user`.

Shared data in the artifact's database:

- `projects/<project no.>`: the project details and `photos` (five slots of `{id, x, y}` or null)
- `settings/cover`, `settings/columns`, `settings/summary`: library-wide settings
- `mslogs/<project no.>`: the whole MSRA Log; `mslogmeta/<project no.>`: `{no, n, updatedAt}` for the project list

Libraries are loaded from cdnjs when first needed: jsPDF 2.5.1, PptxGenJS 3.12.0, SheetJS 0.18.5, ExcelJS 4.4.0 and jsPDF-AutoTable 3.8.4. Page fonts: Barlow and Barlow Condensed (Google Fonts).

## Tests

```
cd tests/msra
npm install exceljs@4.4.0 xlsx@0.18.5 jspdf@2.5.1 jspdf-autotable@3.8.4
node test-core.js "The Borough_Material_Submittal_Log.xlsx"   # every material should be covered
node test-xlsx.js "The Borough_Material_Submittal_Log.xlsx"   # writes test.xlsx
node test-pdf.js                                              # writes test.pdf
```

## Credits

Fonts: Barlow; Caladea (Apache 2.0) and Carlito (SIL OFL) on the presentation sheets; Open Sans by Steve Matteson (SIL OFL) in the MSRA Log. Built with jsPDF, jsPDF-AutoTable, PptxGenJS, SheetJS and ExcelJS.
