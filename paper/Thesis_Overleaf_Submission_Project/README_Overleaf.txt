OVERLEAF SUBMISSION PROJECT

1. Upload Thesis_Overleaf_Submission_Project.zip through Overleaf -> New Project -> Upload Project.
2. Set main.tex as the main document if required.
3. Use pdfLaTeX. The source uses standard TeX fonts and BibTeX; XeLaTeX is not required. Overleaf's normal automatic compilation runs the necessary bibliography passes.
4. Compile and use the Overleaf error log only if a package issue remains.

The source follows the supplied template's letterpaper, 10-point, two-column ieeeconf layout. The class is copied unchanged, with its licence and attribution retained. The supplied IEEEtran bibliography style is included locally. Research text, bibliography entries and figures are specific to the verified pharmaceutical-company analysis.

All empirical content comes from thesis_output/reproduction/final_run, with methodology checked against reproduction/rebuild.py and the feature implementation it calls. Metrics in prose and tables are formatted to three decimal places from the stored results. Full-precision values remain only in the existing machine-readable reproduction outputs; existing plot labels retain their display formatting. The 15 PDF files inside figures are original vector plots from the verified reproduction, not a compiled paper or an older research project PDF.

The paper includes all eight held-out confusion matrices and ROC curves, metric and class-trade-off comparisons, sample coverage, feature missingness, logistic coefficients and validation permutation importance. A compact vector workflow in figures/workflow.tex is drawn by TikZ within the Methodology section. TikZ with the arrows.meta and positioning libraries is included in standard Overleaf TeX Live installations. Tables are ordinary LaTeX inputs. No external data, code execution, fonts, absolute paths or shell escape are needed to compile the paper.

Local recompilation could not be performed: pdfLaTeX was unavailable on PATH and in the checked standard local installation locations. No new paper PDF is claimed or supplied. Compile main.tex in Overleaf to obtain the submission PDF. Source checks verify local dependencies, bibliography keys, metric transcription and ZIP contents; final pagination should be reviewed after Overleaf compilation.

The ZIP contains the project files at its root for direct upload. It intentionally does not contain itself. Original source files, prior documents and reproduction outputs were left unchanged.

