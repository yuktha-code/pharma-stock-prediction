# Draft delivery QA â€” version 05

Delivery checkpoint: 8 September 2026, approximately 08:07 IST.

## Deliverables

- `Thesis_Draft.docx` â€” latest editable draft, identical to `Thesis_Draft_v05.docx`.
- `Thesis_Draft.pdf` â€” latest PDF converted from that DOCX, identical to `Thesis_Draft_v05.pdf`; 33 A4 pages.
- Earlier completed versions remain saved. `delivery_hashes.json` records hashes of the current delivery copies.

## Content completed

11,744-word manuscript with cover, abstract, executive brief, contents, figure/table lists, Chapters 1â€“9, external references and Appendices Aâ€“H. There are 18 editable Word tables and three evidence-based figures. The final predictor/model outputs were not available; the corresponding chapter sections and appendix tables explicitly state their unverified or unavailable status. Historical dimensions are labeled documentary. No missing performance metrics were invented.

## Checks actually performed

- DOCX ZIP CRC check completed without a bad member.
- Confirmed 904 Word paragraphs, including 832 nonempty paragraphs; 18 tables; three drawings; two outline-level styles; 18 repeating table-header markers; six embedded DejaVu font parts; a native page-number footer field.
- Extracted the final PDF's full text and layout XML.
- Found all 832 nonempty DOCX paragraphs in normalized PDF text, excluding standalone page-number lines. This checks text retention, not identical Word pagination.
- Rendered all 33 PDF pages to 1500-pixel-high PNGs in `qa_pages_v05/`.
- Visually reviewed all pages in four contact sheets in `qa_contact_v05/`.
- Additionally opened final pages 11, 14, 18, 21, 29 and 32 individually to inspect figures, table legibility, complete company mapping and appendix layout.
- Automated text-box page-edge check found zero overflow candidates. This does not establish absence of every possible internal overlap.
- Earlier layout issues were corrected through compact table padding, whole-table PDF break rules, neutral hyperlink styling and removal of unnecessary chapter/reference/appendix page breaks. No blank PDF page was observed in the final contact-sheet review.
- DejaVu Serif and Sans embedded and used for substantive text, tables and figures. PDF extraction also reports a Times New Roman font resource associated with an inherited blank-space run; no substantive content was identified in that font.

## Limits of this QA

- Native Word render/export could not be run: COM activation returned logon-session error 80070520. LibreOffice is not present at the checked standard installation path. The skill's native DOCX rendering route was not completed.
- The PDF is a Calibre conversion from the editable DOCX. Its text matches, but exact pagination/layout equality with Microsoft Word has not been verified.
- All-page full-resolution visual inspection was not completed; the scope was all-page contact-sheet review plus the six individual pages listed above. Do not describe this as a full native DOCX render gate pass.
- Final model training, prediction/score recomputation, leakage validation and original-environment reproducibility remain unverified for the reasons stated in the draft. The document is not submission-ready as a verified empirical research project.

## Resume only where needed

Use `Thesis_Draft.docx` / `Thesis_Draft.pdf` for review. Content source is `thesis_manuscript.md`; production scripts are `build_draft_assets.py` and `finalize_draft_docx.py`, with `pdf_final.css` for PDF table handling. No additional source inventory is needed. To finalize the empirical research project, obtain the final analytical packages, verify the actual panel/model outputs, replace unavailable result entries and perform native Word/LibreOffice rendering QA in a functioning environment.

