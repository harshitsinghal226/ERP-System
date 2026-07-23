"""
Reports Page — Generate, preview, and export all 4 report types.
"""

import customtkinter as ctk
import logging
from datetime import datetime

from utils.theme import Fonts, get_theme
from utils.helpers import format_weight, format_currency, format_date, safe_float, parse_date
from utils.constants import MONTHS
from views.components.data_table import DataTable
from views.components.toast import Toast
from views.components.searchable_combo import SearchableComboBox

logger = logging.getLogger(__name__)


class ReportPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        theme = get_theme(ctk.get_appearance_mode().lower())
        super().__init__(parent, fg_color=theme.BG_PRIMARY)
        self._app = app
        self._theme = theme
        
        from services.report_service import ReportService
        from services.export_service import ExportService
        from services.print_service import PrintService
        from services.karigar_service import KarigarService
        self._report_svc = ReportService()
        self._export_svc = ExportService()
        self._karigar_svc = KarigarService()
        
        self._build_ui()
    
    def _build_ui(self):
        theme = self._theme
        
        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=16)
        
        # ── Report Cards ─────────────────────────────────────────────
        cards_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 16))
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1, uniform="r")
        
        reports = [
            ("📋 Karigar Ledger", "Individual Karigar\nmonthly ledger", self._show_ledger_filters),
            ("📊 All Karigars Summary", "Summary of all\nKarigars at once", self._generate_summary),
            ("📅 Date Wise Report", "Entries between\nselected dates", self._show_datewise_filters),
            ("📈 Monthly Summary", "Complete monthly\noverview", self._show_monthly_filters),
        ]
        
        for i, (title, desc, cmd) in enumerate(reports):
            card = ctk.CTkFrame(cards_frame, fg_color=theme.BG_SECONDARY, corner_radius=12, cursor="hand2")
            card.grid(row=0, column=i, padx=6, pady=4, sticky="nsew")
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="both", expand=True, padx=16, pady=14)
            
            ctk.CTkLabel(inner, text=title, font=ctk.CTkFont(family=Fonts.FAMILY, size=13, weight="bold"), text_color=theme.TEXT_PRIMARY).pack(anchor="w")
            ctk.CTkLabel(inner, text=desc, font=ctk.CTkFont(family=Fonts.FAMILY, size=10), text_color=theme.TEXT_MUTED, justify="left").pack(anchor="w", pady=(4, 8))
            ctk.CTkButton(inner, text="Generate", command=cmd, fg_color=theme.ACCENT_GOLD, text_color=theme.TEXT_ON_ACCENT, height=30, width=100, corner_radius=6, font=ctk.CTkFont(family=Fonts.FAMILY, size=11, weight="bold")).pack(anchor="w")
        
        # ── Filters Area (dynamic) ───────────────────────────────────
        self._filter_frame = ctk.CTkFrame(scroll, fg_color=theme.BG_SECONDARY, corner_radius=12)
        self._filter_frame.pack(fill="x", pady=(0, 8))
        self._filter_frame.pack_forget()  # Hidden initially
        
        # ── Results Table ────────────────────────────────────────────
        self._result_frame = ctk.CTkFrame(scroll, fg_color=theme.BG_SECONDARY, corner_radius=12)
        self._result_frame.pack(fill="both", expand=True)
        
        self._result_title = ctk.CTkLabel(
            self._result_frame, text="Select a report to generate",
            font=ctk.CTkFont(family=Fonts.FAMILY, size=13, weight="bold"),
            text_color=theme.TEXT_MUTED,
        )
        self._result_title.pack(pady=40)
    
    def _clear_filters(self):
        for w in self._filter_frame.winfo_children():
            w.destroy()
    
    def _clear_results(self):
        for w in self._result_frame.winfo_children():
            w.destroy()
    
    def _show_ledger_filters(self):
        """Show filters for Karigar Ledger report."""
        self._clear_filters()
        self._filter_frame.pack(fill="x", pady=(0, 8))
        theme = self._theme
        
        inner = ctk.CTkFrame(self._filter_frame, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=12)
        
        ctk.CTkLabel(inner, text="Karigar:", font=ctk.CTkFont(family=Fonts.FAMILY, size=11, weight="bold")).pack(side="left")
        
        karigars = self._karigar_svc.get_active()
        names = [k.karigar_name for k in karigars]
        self._karigar_map_report = {k.karigar_name.lower(): k.karigar_id for k in karigars}
        
        self._ledger_karigar = SearchableComboBox(inner, values=names, height=34, width=200)
        self._ledger_karigar.pack(side="left", padx=8)
        
        ctk.CTkLabel(inner, text="Month:", font=ctk.CTkFont(family=Fonts.FAMILY, size=11, weight="bold")).pack(side="left", padx=(16, 0))
        self._ledger_month = ctk.CTkComboBox(inner, values=["All"] + MONTHS, height=34, width=120, state="readonly")
        self._ledger_month.pack(side="left", padx=4)
        self._ledger_month.set("All")
        
        ctk.CTkLabel(inner, text="Year:", font=ctk.CTkFont(family=Fonts.FAMILY, size=11, weight="bold")).pack(side="left", padx=(16, 0))
        years = [str(y) for y in range(2020, datetime.now().year + 2)]
        self._ledger_year = ctk.CTkComboBox(inner, values=years, height=34, width=80, state="readonly")
        self._ledger_year.pack(side="left", padx=4)
        self._ledger_year.set(str(datetime.now().year))
        
        ctk.CTkButton(inner, text="Generate", command=self._generate_ledger, fg_color=theme.ACCENT_GOLD, text_color=theme.TEXT_ON_ACCENT, height=34, width=100, corner_radius=8).pack(side="left", padx=12)
    
    def _generate_ledger(self):
        """Generate Karigar Ledger report."""
        karigar_name = self._ledger_karigar.get().strip()
        karigar_id = self._karigar_map_report.get(karigar_name.lower())
        if not karigar_id:
            Toast.show(self._app, "Please select a Karigar", "warning")
            return
        
        month_str = self._ledger_month.get()
        month = MONTHS.index(month_str) + 1 if month_str != "All" else None
        year = int(self._ledger_year.get()) if month else None
        
        try:
            result = self._report_svc.get_karigar_ledger(karigar_id, month, year)
            self._display_ledger(result)
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
    
    def _display_ledger(self, data):
        """Display the ledger report in the results area."""
        self._clear_results()
        theme = self._theme
        
        # Header
        header = ctk.CTkFrame(self._result_frame, fg_color="transparent")
        header.pack(fill="x", padx=16, pady=(12, 4))
        
        ctk.CTkLabel(header, text=f"Karigar Ledger — {data['karigar'].karigar_name}", font=ctk.CTkFont(family=Fonts.FAMILY, size=14, weight="bold"), text_color=theme.TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(header, text=f"Opening: {format_weight(data['opening_balance'])}g  |  Closing: {format_weight(data['closing_balance'])}g", font=ctk.CTkFont(family=Fonts.FAMILY, size=11), text_color=theme.ACCENT_GOLD).pack(side="right")
        
        # Export buttons
        btn_row = ctk.CTkFrame(self._result_frame, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=4)
        
        ctk.CTkButton(btn_row, text="📄 Export PDF", command=lambda: self._export_ledger_pdf(data), fg_color="#059669", text_color="white", height=30, width=110, corner_radius=6).pack(side="left", padx=2)
        ctk.CTkButton(btn_row, text="📊 Export Excel", command=lambda: self._export_ledger_excel(data), fg_color="#2563eb", text_color="white", height=30, width=110, corner_radius=6).pack(side="left", padx=2)
        
        # Table
        table = DataTable(
            self._result_frame,
            columns=[
                ("sn", "SN", 40), ("date", "Date", 90), ("type", "Type", 50),
                ("remark", "Remark", 150), ("received", "Jama (R)", 90),
                ("issued", "Naam (I)", 90), ("item", "Item Type", 120),
                ("labour", "Labour", 80), ("advance", "Advance", 90),
                ("balance", "Balance", 90),
            ],
        )
        table.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        
        rows = []
        for e in data["entries"]:
            rows.append([
                e["sn"], e["date"], e["entry_type"],
                e["remark"], format_weight(e["received_weight"]) if e["received_weight"] else "",
                format_weight(e["issued_weight"]) if e["issued_weight"] else "",
                e["item_type"], format_weight(e["labour_weight"]) if e["labour_weight"] else "",
                format_currency(e["advance_money"]) if e["advance_money"] else "",
                format_weight(e["running_balance"]),
            ])
        
        # Totals row
        rows.append([
            "", "TOTAL", "", "",
            format_weight(data["total_received"]),
            format_weight(data["total_issued"]),
            "", format_weight(data["total_labour"]),
            format_currency(data["total_advance"]),
            format_weight(data["closing_balance"]),
        ])
        
        table.load_data(rows)
    
    def _export_ledger_pdf(self, data):
        """Export ledger to PDF."""
        try:
            headers = ["SN", "Date", "Type", "Remark", "Jama (R)", "Naam (I)", "Item", "Labour", "Advance", "Balance"]
            rows = [[e["sn"], e["date"], e["entry_type"], e["remark"],
                      format_weight(e["received_weight"]), format_weight(e["issued_weight"]),
                      e["item_type"], format_weight(e["labour_weight"]),
                      format_currency(e["advance_money"]), format_weight(e["running_balance"])]
                     for e in data["entries"]]
            
            path = self._export_svc.export_to_pdf(
                f"Karigar Ledger — {data['karigar'].karigar_name}",
                headers, rows,
                subtitle=f"Opening: {format_weight(data['opening_balance'])}g | Closing: {format_weight(data['closing_balance'])}g"
            )
            Toast.show(self._app, f"PDF saved: {path}", "success")
            from services.print_service import PrintService
            PrintService.print_preview(path)
        except Exception as e:
            Toast.show(self._app, f"Export error: {e}", "error")
    
    def _export_ledger_excel(self, data):
        """Export ledger to Excel."""
        try:
            headers = ["SN", "Date", "Type", "Remark", "Jama (R)", "Naam (I)", "Item", "Labour", "Advance", "Balance"]
            rows = [[e["sn"], e["date"], e["entry_type"], e["remark"],
                      e["received_weight"], e["issued_weight"],
                      e["item_type"], e["labour_weight"],
                      e["advance_money"], e["running_balance"]]
                     for e in data["entries"]]
            path = self._export_svc.export_to_excel(f"Karigar Ledger — {data['karigar'].karigar_name}", headers, rows)
            Toast.show(self._app, f"Excel saved: {path}", "success")
        except Exception as e:
            Toast.show(self._app, f"Export error: {e}", "error")
    
    def _generate_summary(self):
        """Generate All Karigars Summary report."""
        try:
            data = self._report_svc.get_all_karigars_summary()
            self._clear_results()
            theme = self._theme
            
            ctk.CTkLabel(self._result_frame, text="All Karigars Summary", font=ctk.CTkFont(family=Fonts.FAMILY, size=14, weight="bold"), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 4))
            
            btn_row = ctk.CTkFrame(self._result_frame, fg_color="transparent")
            btn_row.pack(fill="x", padx=16, pady=4)
            ctk.CTkButton(btn_row, text="📄 Export PDF", command=lambda: self._export_summary_pdf(data), fg_color="#059669", text_color="white", height=30, width=110, corner_radius=6).pack(side="left", padx=2)
            
            table = DataTable(self._result_frame, columns=[
                ("sn", "SN", 40), ("name", "Karigar", 150), ("issued", "Total Issued", 100),
                ("received", "Total Received", 100), ("labour", "Total Labour", 100),
                ("advance", "Total Advance", 100), ("balance", "Closing Balance", 110),
                ("status", "Status", 70),
            ])
            table.pack(fill="both", expand=True, padx=12, pady=(0, 12))
            
            rows = [[d["sn"], d["karigar_name"], format_weight(d["total_issued"]),
                      format_weight(d["total_received"]), format_weight(d["total_labour"]),
                      format_currency(d["total_advance"]), format_weight(d["closing_balance"]),
                      d["status"]] for d in data]
            table.load_data(rows)
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
    
    def _export_summary_pdf(self, data):
        try:
            headers = ["SN", "Karigar", "Issued", "Received", "Labour", "Advance", "Balance", "Status"]
            rows = [[d["sn"], d["karigar_name"], format_weight(d["total_issued"]),
                      format_weight(d["total_received"]), format_weight(d["total_labour"]),
                      format_currency(d["total_advance"]), format_weight(d["closing_balance"]),
                      d["status"]] for d in data]
            path = self._export_svc.export_to_pdf("All Karigars Summary", headers, rows)
            Toast.show(self._app, f"PDF saved!", "success")
            from services.print_service import PrintService
            PrintService.print_preview(path)
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
    
    def _show_datewise_filters(self):
        self._clear_filters()
        self._filter_frame.pack(fill="x", pady=(0, 8))
        theme = self._theme
        inner = ctk.CTkFrame(self._filter_frame, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=12)
        
        ctk.CTkLabel(inner, text="From:", font=ctk.CTkFont(family=Fonts.FAMILY, size=11, weight="bold")).pack(side="left")
        self._dw_from = ctk.CTkEntry(inner, height=34, width=120, placeholder_text="DD-MM-YYYY")
        self._dw_from.pack(side="left", padx=4)
        
        ctk.CTkLabel(inner, text="To:", font=ctk.CTkFont(family=Fonts.FAMILY, size=11, weight="bold")).pack(side="left", padx=(12, 0))
        self._dw_to = ctk.CTkEntry(inner, height=34, width=120, placeholder_text="DD-MM-YYYY")
        self._dw_to.pack(side="left", padx=4)
        
        ctk.CTkButton(inner, text="Generate", command=self._generate_datewise, fg_color=theme.ACCENT_GOLD, text_color=theme.TEXT_ON_ACCENT, height=34, width=100).pack(side="left", padx=12)
    
    def _generate_datewise(self):
        start = parse_date(self._dw_from.get())
        end = parse_date(self._dw_to.get())
        if not start or not end:
            Toast.show(self._app, "Enter valid dates (DD-MM-YYYY)", "error")
            return
        try:
            data = self._report_svc.get_date_wise_report(start, end)
            self._clear_results()
            theme = self._theme
            
            ctk.CTkLabel(self._result_frame, text=f"Date Wise Report: {format_date(start)} to {format_date(end)}", font=ctk.CTkFont(family=Fonts.FAMILY, size=14, weight="bold"), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 4))
            
            table = DataTable(self._result_frame, columns=[
                ("sn", "SN", 40), ("date", "Date", 90), ("type", "Type", 70),
                ("karigar", "Karigar", 130), ("item", "Item", 120),
                ("issued", "Issued", 90), ("received", "Received", 90),
                ("advance", "Advance", 90), ("remark", "Remark", 160),
            ])
            table.pack(fill="both", expand=True, padx=12, pady=(0, 12))
            
            rows = [[d["sn"], d["date"], d["entry_type"], d["karigar_name"], d["item_type"],
                      format_weight(d["issued_weight"]) if d["issued_weight"] else "",
                      format_weight(d["received_weight"]) if d["received_weight"] else "",
                      format_currency(d["advance_money"]) if d["advance_money"] else "",
                      d["remark"]] for d in data]
            table.load_data(rows)
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
    
    def _show_monthly_filters(self):
        self._clear_filters()
        self._filter_frame.pack(fill="x", pady=(0, 8))
        theme = self._theme
        inner = ctk.CTkFrame(self._filter_frame, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=12)
        
        ctk.CTkLabel(inner, text="Month:", font=ctk.CTkFont(family=Fonts.FAMILY, size=11, weight="bold")).pack(side="left")
        self._ms_month = ctk.CTkComboBox(inner, values=MONTHS, height=34, width=120, state="readonly")
        self._ms_month.pack(side="left", padx=4)
        self._ms_month.set(MONTHS[datetime.now().month - 1])
        
        ctk.CTkLabel(inner, text="Year:", font=ctk.CTkFont(family=Fonts.FAMILY, size=11, weight="bold")).pack(side="left", padx=(12, 0))
        years = [str(y) for y in range(2020, datetime.now().year + 2)]
        self._ms_year = ctk.CTkComboBox(inner, values=years, height=34, width=80, state="readonly")
        self._ms_year.pack(side="left", padx=4)
        self._ms_year.set(str(datetime.now().year))
        
        ctk.CTkButton(inner, text="Generate", command=self._generate_monthly, fg_color=theme.ACCENT_GOLD, text_color=theme.TEXT_ON_ACCENT, height=34, width=100).pack(side="left", padx=12)
    
    def _generate_monthly(self):
        month = MONTHS.index(self._ms_month.get()) + 1
        year = int(self._ms_year.get())
        try:
            data = self._report_svc.get_monthly_summary(month, year)
            self._clear_results()
            theme = self._theme
            
            ctk.CTkLabel(self._result_frame, text=f"Monthly Summary — {MONTHS[month-1]} {year}", font=ctk.CTkFont(family=Fonts.FAMILY, size=14, weight="bold"), text_color=theme.TEXT_PRIMARY).pack(anchor="w", padx=16, pady=(12, 8))
            
            grid = ctk.CTkFrame(self._result_frame, fg_color="transparent")
            grid.pack(fill="x", padx=16, pady=8)
            for i in range(3):
                grid.grid_columnconfigure(i, weight=1, uniform="ms")
            
            stats = [
                ("Total Issued", format_weight(data["total_issued"]) + "g", "#d4a843"),
                ("Total Received", format_weight(data["total_received"]) + "g", "#34d399"),
                ("Closing Balance", format_weight(data["closing_balance"]) + "g", "#f87171"),
                ("Total Labour", format_weight(data["total_labour"]) + "g", "#60a5fa"),
                ("Total Scrap", format_weight(data["total_scrap"]) + "g", "#a78bfa"),
                ("Total Advance", format_currency(data["total_advance"]), "#fbbf24"),
            ]
            
            for i, (label, value, color) in enumerate(stats):
                card = ctk.CTkFrame(grid, fg_color=theme.BG_TERTIARY, corner_radius=10)
                card.grid(row=i // 3, column=i % 3, padx=6, pady=4, sticky="nsew")
                ctk.CTkLabel(card, text=label, font=ctk.CTkFont(family=Fonts.FAMILY, size=10), text_color=theme.TEXT_MUTED).pack(padx=16, pady=(10, 2), anchor="w")
                ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family=Fonts.FAMILY, size=20, weight="bold"), text_color=color).pack(padx=16, pady=(0, 10), anchor="w")
        except Exception as e:
            Toast.show(self._app, f"Error: {e}", "error")
