import tkinter as tk
from pathlib import Path
import sys
from tkinter import filedialog, messagebox, ttk
from tkinter.scrolledtext import ScrolledText

from .comparison import compare_rows
from .excel_export import write_output_excel
from .mapping import DEFAULT_MAPPING_TEXT, parse_mapping_rules
from .naming import get_desktop_dir, suggested_output_name
from .parsers import parse_caracteristicas_pdf, parse_secondary_pdf


class ComparatorApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Report Comparison - Caracteristicas vs Relatorio Secundario")
        self.geometry("1200x780")
        self._icon_image = None
        self._configure_window_icon()

        self.desktop_dir = get_desktop_dir()
        self.pdf_base_var = tk.StringVar(value="")
        self.pdf_secondary_var = tk.StringVar(value="")
        self.model_var = tk.StringVar(value="modelo.xlsx")
        self.output_var = tk.StringVar(
            value=str(self.desktop_dir / suggested_output_name())
        )

        self._build_ui()

    def _configure_window_icon(self) -> None:
        base_candidates = [Path.cwd()]

        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base_candidates.insert(0, Path(sys._MEIPASS))

        for base in base_candidates:
            ico_path = base / "compare_4222.ico"
            if ico_path.exists():
                try:
                    self.iconbitmap(default=str(ico_path))
                    return
                except Exception:
                    pass

            png_path = base / "compare_4222.png"
            if png_path.exists():
                try:
                    self._icon_image = tk.PhotoImage(file=str(png_path))
                    self.iconphoto(True, self._icon_image)
                    return
                except Exception:
                    pass

    def _build_ui(self) -> None:
        container = ttk.Frame(self, padding=12)
        container.pack(fill=tk.BOTH, expand=True)

        row = 0
        ttk.Label(container, text="PDF base (Tabela Caracteristicas):").grid(row=row, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.pdf_base_var, width=95).grid(row=row, column=1, sticky="ew", padx=8)
        ttk.Button(container, text="Selecionar", command=lambda: self._pick_file(self.pdf_base_var, [("PDF", "*.pdf")])).grid(row=row, column=2)

        row += 1
        ttk.Label(container, text="PDF Adcole:").grid(row=row, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.pdf_secondary_var, width=95).grid(row=row, column=1, sticky="ew", padx=8)
        ttk.Button(container, text="Selecionar", command=lambda: self._pick_file(self.pdf_secondary_var, [("PDF", "*.pdf")])).grid(row=row, column=2)

        row += 1
        ttk.Label(container, text="Modelo Excel:").grid(row=row, column=0, sticky="w")
        ttk.Entry(container, textvariable=self.model_var, width=95).grid(row=row, column=1, sticky="ew", padx=8)
        ttk.Button(container, text="Selecionar", command=lambda: self._pick_file(self.model_var, [("Excel", "*.xlsx")])).grid(row=row, column=2)

        row += 1
        ttk.Label(container, text="Regras de mapeamento (editavel):").grid(row=row, column=0, sticky="nw", pady=(12, 4))

        self.mapping_text = ScrolledText(container, width=120, height=7)
        self.mapping_text.grid(row=row, column=1, columnspan=2, sticky="ew", pady=(12, 4))
        self.mapping_text.insert("1.0", DEFAULT_MAPPING_TEXT)

        row += 1
        button_row = ttk.Frame(container)
        button_row.grid(row=row, column=1, columnspan=2, sticky="w", pady=8)
        ttk.Button(button_row, text="Comparar e Exportar", command=self._run_compare).pack(side=tk.LEFT)

        row += 1
        ttk.Label(container, text="Resumo de divergencias:").grid(row=row, column=0, sticky="w", pady=(8, 4))

        row += 1
        columns = ("characteristic", "status", "detail")
        self.tree = ttk.Treeview(container, columns=columns, show="headings", height=18)
        self.tree.heading("characteristic", text="Characteristic")
        self.tree.heading("status", text="Status")
        self.tree.heading("detail", text="Detalhes")
        self.tree.column("characteristic", width=500)
        self.tree.column("status", width=90, anchor="center")
        self.tree.column("detail", width=500)
        self.tree.grid(row=row, column=0, columnspan=3, sticky="nsew")

        scroll = ttk.Scrollbar(container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scroll.set)
        scroll.grid(row=row, column=3, sticky="ns")

        container.columnconfigure(1, weight=1)
        container.rowconfigure(row, weight=1)

    def _pick_file(self, target_var: tk.StringVar, filetypes: list[tuple[str, str]]) -> None:
        path = filedialog.askopenfilename(filetypes=filetypes)
        if path:
            target_var.set(path)
            if target_var is self.pdf_secondary_var:
                self._refresh_output_suggestion_from_secondary(Path(path))

    def _refresh_output_suggestion_from_secondary(self, secondary_path: Path) -> None:
        suggested_name = suggested_output_name(secondary_path)
        current_output = Path(self.output_var.get())

        if current_output.parent and str(current_output.parent) not in {"", "."}:
            folder = current_output.parent
        else:
            folder = self.desktop_dir

        self.output_var.set(str(folder / suggested_name))

    def _resolve_output_path(self, output_path: Path) -> Path:
        if output_path.suffix.lower() != ".xlsx":
            output_path = output_path.with_suffix(".xlsx")
        if not output_path.is_absolute():
            return self.desktop_dir / output_path
        return output_path

    def _resolve_existing_model_path(self, raw_model_path: Path) -> Path | None:
        if raw_model_path.is_absolute():
            return raw_model_path if raw_model_path.exists() else None

        candidates: list[Path] = [Path.cwd() / raw_model_path]

        # Source mode (project root) candidate.
        candidates.append(Path(__file__).resolve().parent.parent / raw_model_path)

        # Frozen executable mode candidate.
        if getattr(sys, "frozen", False):
            candidates.append(Path(sys.executable).resolve().parent / raw_model_path)

        # PyInstaller temporary extraction folder candidate.
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            candidates.append(Path(sys._MEIPASS) / raw_model_path)

        for candidate in candidates:
            if candidate.exists():
                return candidate
        return None

    def _ask_model_file_if_missing(self) -> Path | None:
        path = filedialog.askopenfilename(
            title="Selecione o modelo Excel (.xlsx)",
            initialdir=str(self.desktop_dir),
            filetypes=[("Excel", "*.xlsx")],
        )
        if not path:
            return None
        selected = Path(path)
        self.model_var.set(str(selected))
        return selected

    def _ask_output_path_after_compare(self) -> Path | None:
        suggested = Path(self.output_var.get())
        path = filedialog.asksaveasfilename(
            title="Salvar resultado da comparacao",
            initialdir=str(suggested.parent if suggested.parent else self.desktop_dir),
            initialfile=suggested.name,
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
        )
        if not path:
            return None
        return self._resolve_output_path(Path(path))

    def _run_compare(self) -> None:
        try:
            base_pdf = Path(self.pdf_base_var.get()).expanduser()
            secondary_pdf = Path(self.pdf_secondary_var.get()).expanduser()
            raw_model_xlsx = Path(self.model_var.get()).expanduser()
            model_xlsx = self._resolve_existing_model_path(raw_model_xlsx)

            for required in [base_pdf, secondary_pdf]:
                if not required.exists():
                    raise FileNotFoundError(f"Arquivo nao encontrado: {required}")

            if model_xlsx is None:
                model_xlsx = self._ask_model_file_if_missing()
                if model_xlsx is None:
                    messagebox.showinfo("Cancelado", "Modelo Excel nao selecionado.")
                    return

            mapping_rules = parse_mapping_rules(self.mapping_text.get("1.0", tk.END))

            base_rows = parse_caracteristicas_pdf(base_pdf)
            secondary_rows = parse_secondary_pdf(secondary_pdf)

            compared_rows = compare_rows(base_rows, secondary_rows, mapping_rules)

            output_xlsx = self._ask_output_path_after_compare()
            if output_xlsx is None:
                messagebox.showinfo("Cancelado", "Salvamento cancelado pelo usuario.")
                return

            self.output_var.set(str(output_xlsx))
            write_output_excel(compared_rows, model_xlsx, output_xlsx)

            self._render_summary(compared_rows)

            not_ok = sum(1 for r in compared_rows if r.status == "not ok")
            messagebox.showinfo(
                "Concluido",
                f"Comparacao finalizada.\nTotal de linhas: {len(compared_rows)}\nnot ok: {not_ok}\nArquivo: {output_xlsx}",
            )

        except Exception as exc:
            messagebox.showerror("Erro", str(exc))

    def _render_summary(self, compared_rows) -> None:
        self.tree.delete(*self.tree.get_children())

        for compared in compared_rows:
            if compared.status == "ok":
                continue

            if compared.secondary_missing:
                detail = "Metrica nao encontrada no relatorio secundario"
            else:
                labels = {
                    "nominal_value": "nominal value",
                    "measured_value": "measured value",
                    "lower_limit": "lower limit",
                    "upper_limit": "upper limit",
                    "deviation": "deviation",
                    "exceedance": "exceedance",
                }
                ordered = [labels[name] for name in labels if name in compared.mismatched_fields]
                detail = ", ".join(ordered)

            self.tree.insert("", tk.END, values=(compared.row.characteristic_name, compared.status, detail))
