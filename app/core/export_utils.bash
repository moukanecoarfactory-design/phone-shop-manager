"""
CSV export utilities.
Exports data to CSV files that open in Excel, Google Sheets, etc.
"""
import csv
from datetime import datetime
from pathlib import Path
import sys


def _get_exports_dir() -> Path:
    """Get the exports folder — works from source and .exe."""
    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent.parent.parent
    d = base / "data" / "exports"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def export_sales_csv(sales: list, output_path: Path = None) -> Path:
    """
    Export sales to CSV.
    Each sale: {id, sale_date, customer_name, total, profit, items: [...]}
    """
    if output_path is None:
        output_path = _get_exports_dir() / f"sales_{_timestamp()}.csv"

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "Sale #", "Date", "Customer", "Total (MAD)", "Profit (MAD)", "Items"
        ])

        # Rows
        for s in sales:
            items_summary = ""
            if s.get("items"):
                items_summary = " | ".join(
                    f"{it.get('name', '?')} x{it.get('qty', 1)}"
                    for it in s["items"]
                )

            writer.writerow([
                s.get("id", ""),
                s.get("sale_date", ""),
                s.get("customer_name", "") or "Walk-in",
                f"{s.get('total', 0):.2f}",
                f"{s.get('profit', 0):.2f}",
                items_summary,
            ])

    return output_path


def export_products_csv(products: list, categories: dict = None,
                        output_path: Path = None) -> Path:
    """
    Export products to CSV.
    categories: {category_id: category_name}
    """
    if output_path is None:
        output_path = _get_exports_dir() / f"products_{_timestamp()}.csv"

    categories = categories or {}

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            "ID", "Name", "Category", "Brand", "Capacity",
            "Buy Price", "Sell Price", "Quantity", "Profit/Unit", "Low Stock Alert"
        ])

        for p in products:
            cat_name = categories.get(p.category_id, "")
            writer.writerow([
                p.id,
                p.name,
                cat_name,
                p.brand,
                p.capacity,
                f"{p.buying_price:.2f}",
                f"{p.selling_price:.2f}",
                p.quantity,
                f"{p.profit:.2f}",
                p.low_stock_alert,
            ])

    return output_path


def export_customers_csv(customers: list, debts: dict = None,
                         output_path: Path = None) -> Path:
    """
    Export customers to CSV.
    debts: {customer_id: debt_amount}
    """
    if output_path is None:
        output_path = _get_exports_dir() / f"customers_{_timestamp()}.csv"

    debts = debts or {}

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        writer.writerow([
            "ID", "Name", "Phone", "Address", "Notes", "Debt (MAD)"
        ])

        for c in customers:
            debt = debts.get(c.id, 0.0)
            writer.writerow([
                c.id,
                c.name,
                c.phone,
                c.address,
                c.notes,
                f"{debt:.2f}",
            ])

    return output_path


def export_phone_units_csv(units: list, output_path: Path = None) -> Path:
    """Export phone units to CSV."""
    if output_path is None:
        output_path = _get_exports_dir() / f"phone_units_{_timestamp()}.csv"

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        writer.writerow([
            "ID", "Product", "IMEI", "Buy Price", "Sell Price", "Status", "Notes"
        ])

        for u in units:
            writer.writerow([
                u.id,
                getattr(u, "product_name", ""),
                u.imei,
                f"{u.buying_price:.2f}",
                f"{u.selling_price:.2f}",
                u.status,
                u.notes,
            ])

    return output_path


def export_debts_csv(debts: list, output_path: Path = None) -> Path:
    """Export customer debts to CSV."""
    if output_path is None:
        output_path = _get_exports_dir() / f"debts_{_timestamp()}.csv"

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        writer.writerow([
            "Customer", "Phone", "Total Sales (MAD)", "Total Paid (MAD)", "Debt (MAD)"
        ])

        for d in debts:
            writer.writerow([
                d.get("name", ""),
                d.get("phone", ""),
                f"{d.get('total_sales', 0):.2f}",
                f"{d.get('total_paid', 0):.2f}",
                f"{d.get('debt', 0):.2f}",
            ])

    return output_path


def open_file(path: Path):
    """Open the exported file with the default application."""
    import subprocess
    try:
        if sys.platform == "win32":
            import os
            os.startfile(str(path))
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception as e:
        print(f"Could not open file: {e}")