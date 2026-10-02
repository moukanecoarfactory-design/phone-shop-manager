"""
Receipt PDF generator using fpdf2.
Creates a clean, printable receipt for a sale.
"""
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from fpdf import FPDF


# ============================================================
# SHOP INFO - Edit these to change the receipt header
# ============================================================
def _get_shop_info() -> dict:
    """Read shop info from DB settings."""
    try:
        from app.locales.translations import get_setting
        return {
            "name":     get_setting("shop_name", "My Phone Shop"),
            "address":  get_setting("shop_address", ""),
            "city":     get_setting("shop_city", ""),
            "phone":    get_setting("shop_phone", ""),
            "email":    get_setting("shop_email", ""),
            "website":  get_setting("shop_website", ""),
        }
    except Exception:
        return {
            "name": "Phone Shop",
            "address": "", "city": "", "phone": "",
            "email": "", "website": "",
        }

class ReceiptPDF(FPDF):
    """Custom PDF class for receipts."""

    def __init__(self, lang: str = "en"):
        super().__init__(orientation="P", unit="mm", format=(80, 250))
        self.lang = lang
        self.set_auto_page_break(auto=True, margin=5)
        self.set_margins(4, 4, 4)

    def header_section(self):
        """Shop header with logo area."""
        info = _get_shop_info()

        # Shop name (big, centered)
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 7, info["name"], ln=True, align="C")

        # Address
        self.set_font("Helvetica", "", 8)
        if info["address"]:
            self.cell(0, 4, info["address"], ln=True, align="C")
        if info["city"]:
            self.cell(0, 4, info["city"], ln=True, align="C")

        # Phone
        if info["phone"]:
            self.set_font("Helvetica", "B", 8)
            self.cell(0, 4, f"Tel: {info['phone']}", ln=True, align="C")

        # Email
        if info["email"]:
            self.set_font("Helvetica", "", 7)
            self.cell(0, 4, info["email"], ln=True, align="C")

        # Website
        if info["website"]:
            self.set_font("Helvetica", "", 7)
            self.cell(0, 4, info["website"], ln=True, align="C")

        # Divider
        self.ln(2)
        self._divider()

    def _divider(self):
        """Dashed divider line."""
        self.set_draw_color(120, 120, 120)
        self.set_line_width(0.2)
        y = self.get_y()
        x_start = 4
        x_end = 76
        x = x_start
        while x < x_end:
            self.line(x, y, min(x + 2, x_end), y)
            x += 3
        self.ln(3)

    def _solid_line(self):
        """Solid thin line."""
        self.set_draw_color(100, 100, 100)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(4, y, 76, y)
        self.ln(2)

    def section_title(self, text: str):
        """Section title in bold."""
        self.set_font("Helvetica", "B", 9)
        self.cell(0, 5, text, ln=True)
        self._solid_line()

    def row_2col(self, left: str, right: str, bold_right: bool = False):
        """Two-column row."""
        self.set_font("Helvetica", "", 8)
        self.cell(30, 4, left, align="L")
        if bold_right:
            self.set_font("Helvetica", "B", 8)
        else:
            self.set_font("Helvetica", "", 8)
        self.cell(0, 4, right, align="R", ln=True)

    def item_row(self, name: str, qty: int, price: float, total: float):
        """One sale item (name wraps if needed)."""
        # Item name (line 1)
        self.set_font("Helvetica", "", 8)
        self.multi_cell(0, 4, name, align="L")

        # Qty × Price ... Total
        self.set_font("Helvetica", "", 7)
        self.cell(0, 4, f"  {qty} x {price:.2f}", align="L")
        self.cell(0, 4, f"{total:.2f}", align="R", ln=True)

    def total_row(self, label: str, value: str, big: bool = False):
        """Total row with bold text."""
        if big:
            self.set_font("Helvetica", "B", 11)
        else:
            self.set_font("Helvetica", "B", 9)
        self.cell(30, 6, label, align="L")
        self.cell(0, 6, value, align="R", ln=True)

    def footer_section(self):
        """Thank-you message."""
        self.ln(3)
        self._divider()

        self.set_font("Helvetica", "B", 10)
        thanks = {
            "en": "THANK YOU!",
            "fr": "MERCI !",
            "ar": "شكراً لكم",
        }.get(self.lang, "THANK YOU!")
        self.cell(0, 6, thanks, ln=True, align="C")

        self.set_font("Helvetica", "", 8)
        visit = {
            "en": "Visit us again!",
            "fr": "À bientôt !",
            "ar": "نراكم قريباً",
        }.get(self.lang, "Visit us again!")
        self.cell(0, 4, visit, ln=True, align="C")

        self.ln(2)
        self.set_font("Helvetica", "I", 6)
        self.set_text_color(120, 120, 120)
        self.cell(0, 3, "Powered by MED ACCESSOIRES", ln=True, align="C")
        self.set_text_color(0, 0, 0)


# ============================================================
# PUBLIC API
# ============================================================

def generate_receipt(sale: Dict, items: List[Dict],
                     customer_name: str = "",
                     cashier_name: str = "admin",
                     lang: str = "en",
                     currency_symbol: str = "MAD",
                     change: float = 0.0) -> ReceiptPDF:
    """
    Build a receipt PDF and return the FPDF object (not yet saved).

    Args:
        sale: dict with id, sale_date, total, profit, paid
        items: list of dicts with name, qty, price, subtotal
        customer_name: customer's name (or "")
        cashier_name: who processed the sale
        lang: "en", "fr", or "ar"
        currency_symbol: "MAD", "DH", "درهم"
        change: change amount (paid - total)
    """
    pdf = ReceiptPDF(lang=lang)
    pdf.add_page()

    # ---------- Header ----------
    pdf.header_section()

    # ---------- Sale info ----------
    pdf.set_font("Helvetica", "", 8)

    labels = {
        "en": {"receipt": "Receipt #", "date": "Date", "customer": "Customer", "cashier": "Cashier"},
        "fr": {"receipt": "Reçu #", "date": "Date", "customer": "Client", "cashier": "Caissier"},
        "ar": {"receipt": "إيصال #", "date": "التاريخ", "customer": "العميل", "cashier": "البائع"},
    }
    L = labels.get(lang, labels["en"])

    pdf.row_2col(L["receipt"], str(sale.get("id", "-")))
    pdf.row_2col(L["date"], str(sale.get("sale_date", "-")))
    pdf.row_2col(L["customer"], customer_name or "-")
    pdf.row_2col(L["cashier"], cashier_name or "-")

    pdf.ln(2)

    # ---------- Items ----------
    headers = {
        "en": "ITEMS",
        "fr": "ARTICLES",
        "ar": "العناصر",
    }
    pdf.section_title(headers.get(lang, "ITEMS"))

    for it in items:
        pdf.item_row(
            name=it["name"],
            qty=it["qty"],
            price=it["price"],
            total=it["subtotal"],
        )

    pdf.ln(2)
    pdf._solid_line()

    # ---------- Totals ----------
    total_labels = {
        "en": {"total": "TOTAL", "paid": "Paid", "change": "Change"},
        "fr": {"total": "TOTAL", "paid": "Payé", "change": "Monnaie"},
        "ar": {"total": "الإجمالي", "paid": "المدفوع", "change": "الباقي"},
    }
    T = total_labels.get(lang, total_labels["en"])

    pdf.total_row(T["total"], f"{sale['total']:.2f} {currency_symbol}", big=True)

    paid = sale.get("paid", sale["total"])
    pdf.total_row(T["paid"], f"{paid:.2f} {currency_symbol}")

    if change > 0:
        pdf.total_row(T["change"], f"{change:.2f} {currency_symbol}")

    # ---------- Footer ----------
    pdf.footer_section()

    return pdf


def save_receipt_pdf(pdf: ReceiptPDF, output_path: Path) -> Path:
    """Save the receipt PDF to a file."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path

