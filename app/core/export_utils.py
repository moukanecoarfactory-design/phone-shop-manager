"""
CSV export utilities — using semicolon delimiter for French/European Excel.
"""
import csv
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def _get_exports_dir() -> Path:
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent.parent
    d = base / "data" / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# Semicolon delimiter for French/European Excel
DELIM = ";"


def export_sales(sales: list) -> Path:
    path = _get_exports_dir() / f"sales_{_timestamp()}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=DELIM)
        w.writerow(["Sale #", "Date", "Customer", "Total (MAD)", "Profit (MAD)", "Items"])
        for s in sales:
            items = " | ".join(
                f"{it.get('name', '?')} x{it.get('qty', 1)}"
                for it in s.get("items", [])
            )
            w.writerow([
                s.get("id", ""),
                s.get("sale_date", ""),
                s.get("customer_name", "") or "Walk-in",
                f"{s.get('total', 0):.2f}",
                f"{s.get('profit', 0):.2f}",
                items,
            ])
    return path


def export_products(products: list, categories: dict = None) -> Path:
    categories = categories or {}
    path = _get_exports_dir() / f"products_{_timestamp()}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=DELIM)
        w.writerow([
            "ID", "Name", "Category", "Brand", "Capacity",
            "Buy Price", "Sell Price", "Quantity", "Profit/Unit", "Low Stock Alert"
        ])
        for p in products:
            w.writerow([
                p.id, p.name, categories.get(p.category_id, ""),
                p.brand, p.capacity,
                f"{p.buying_price:.2f}", f"{p.selling_price:.2f}",
                p.quantity, f"{p.profit:.2f}", p.low_stock_alert,
            ])
    return path


def export_customers(customers: list, debts: dict = None) -> Path:
    debts = debts or {}
    path = _get_exports_dir() / f"customers_{_timestamp()}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=DELIM)
        w.writerow(["ID", "Name", "Phone", "Address", "Notes", "Debt (MAD)"])
        for c in customers:
            w.writerow([
                c.id, c.name, c.phone, c.address, c.notes,
                f"{debts.get(c.id, 0.0):.2f}",
            ])
    return path


def export_phone_units(units: list) -> Path:
    path = _get_exports_dir() / f"phone_units_{_timestamp()}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=DELIM)
        w.writerow(["ID", "Product", "IMEI", "Buy Price", "Sell Price", "Status", "Notes"])
        for u in units:
            w.writerow([
                u.id,
                getattr(u, "product_name", ""),
                u.imei,
                f"{u.buying_price:.2f}", f"{u.selling_price:.2f}",
                u.status, u.notes,
            ])
    return path


def export_debts(debts: list) -> Path:
    path = _get_exports_dir() / f"debts_{_timestamp()}.csv"
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=DELIM)
        w.writerow(["Customer", "Phone", "Total Sales (MAD)", "Total Paid (MAD)", "Debt (MAD)"])
        for d in debts:
            w.writerow([
                d.get("name", ""), d.get("phone", ""),
                f"{d.get('total_sales', 0):.2f}",
                f"{d.get('total_paid', 0):.2f}",
                f"{d.get('debt', 0):.2f}",
            ])
    return path


def open_file(path: Path):
    """Open the exported file with the default application."""
    try:
        if sys.platform == "win32":
            os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        print(f"Could not open file: {e}")