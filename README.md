# PDF Table Comparator

Desktop app in Python (Tkinter) to compare values between two PDF reports and export an Excel file with mismatch highlights.

## Run

1. Install dependencies:
   pip install -r requirements.txt
2. Run app:
   python app.py

## Build EXE (Windows)

1. Install build tools in your venv:
   pip install pyinstaller pillow
2. Build executable with embedded icon and model template:
   pyinstaller --noconfirm --clean --onefile --windowed --name "adcole compare" --icon "compare_4222.ico" --add-data "compare_4222.ico;." --add-data "compare_4222.png;." --add-data "modelo.xlsx;." app.py
3. Output file:
   dist\adcole compare.exe

## Output rules

- Base rows come from `Tabela_Caracteristicas` PDF.
- Secondary report can be any PDF that follows the same report layout.
- Status column uses `ok` and `not ok`.
- Comparison criteria uses only: nominal value, measured value, lower limit and upper limit.
- Deviation and exceedance are exported but not used to decide `ok`/`not ok`.
- Mismatched cells are highlighted in light red.
- `NOT OK` cell is highlighted in light red when row has at least one mismatch.
- After comparison finishes, the app opens a save dialog so the user chooses where to save the `.xlsx`.
- Default output file name suggestion: first 11 chars from `Program:` in Adcole report + current time (HHMMSS).
- If `modelo.xlsx` is not found, the app asks you to select the template file.

## Project structure

- `app.py`: entrypoint that launches the interface.
- `comparator_app/ui.py`: Tkinter interface and user flow.
- `comparator_app/parsers.py`: PDF extraction logic (base + Adcole).
- `comparator_app/comparison.py`: comparison engine (`ok` / `not ok`).
- `comparator_app/excel_export.py`: Excel output generation and highlights.
- `comparator_app/mapping.py`: editable default mapping rules.
- `comparator_app/naming.py`: output naming and desktop detection helpers.
- `comparator_app/models.py`: shared dataclasses.
- `comparator_app/utils.py`: normalization and numeric parsing helpers.
