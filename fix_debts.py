from pathlib import Path

def main():
    path = Path(__file__).parent / "app" / "ui" / "debts_report_page.py"
    content = path.read_text(encoding="utf-8")

    # Find the refresh method and replace it
    old_refresh = '''    def refresh(self):
        L = lambda key: t(key, self.lang)
        C = currency(self.lang)

        debts = get_all_debts()
        total = get_total_debts()

        self.total_debts_lbl.setText(f"{total:.2f} {C}")
        self.count_lbl.setText(f"{len(debts)} {L('customers_label')}")

        self.table.setRowCount(len(debts))

        # Show/hide empty state
        if len(debts) == 0:
            self.empty_label.setVisible(True)
            self.table.setVisible(False)
        else:
            self.empty_label.setVisible(False)
            self.table.setVisible(True)

            for row, d in enumerate(debts):
                name_item = QTableWidgetItem(d["name"])
                name_item.setData(Qt.ItemDataRole.UserRole, d["customer_id"])
                self.table.setItem(row, 0, name_item)

                self.table.setItem(row, 1, QTableWidgetItem(d["phone"]))

                sales_item = QTableWidgetItem(f"{d['total_sales']:.2f} {C}")
                sales_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, sales_item)

                paid_item = QTableWidgetItem(f"{d['total_paid']:.2f} {C}")
                paid_item.setForeground(QColor("#16a34a"))
                paid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 3, paid_item)

                debt_item = QTableWidgetItem(f"{d['debt']:.2f} {C}")
                debt_item.setForeground(QColor("#dc2626"))
                debt_item.setBackground(QColor("#fef2f2"))
                debt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, debt_item)'''

    new_refresh = '''    def refresh(self):
        L = lambda key: t(key, self.lang)
        C = currency(self.lang)

        debts = get_all_debts()
        total = get_total_debts()

        self.total_debts_lbl.setText(f"{total:.2f} {C}")
        self.count_lbl.setText(f"{len(debts)} {L('customers_label')}")

        # If no debts: hide table, show big message
        if len(debts) == 0:
            self.table.setVisible(False)
            self.table_card.setVisible(False)
            self.empty_label.setVisible(True)
        else:
            self.table.setVisible(True)
            self.table_card.setVisible(True)
            self.empty_label.setVisible(False)

            self.table.setRowCount(len(debts))
            for row, d in enumerate(debts):
                name_item = QTableWidgetItem(d["name"])
                name_item.setData(Qt.ItemDataRole.UserRole, d["customer_id"])
                self.table.setItem(row, 0, name_item)

                self.table.setItem(row, 1, QTableWidgetItem(d["phone"]))

                sales_item = QTableWidgetItem(f"{d['total_sales']:.2f} {C}")
                sales_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 2, sales_item)

                paid_item = QTableWidgetItem(f"{d['total_paid']:.2f} {C}")
                paid_item.setForeground(QColor("#16a34a"))
                paid_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 3, paid_item)

                debt_item = QTableWidgetItem(f"{d['debt']:.2f} {C}")
                debt_item.setForeground(QColor("#dc2626"))
                debt_item.setBackground(QColor("#fef2f2"))
                debt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, debt_item)'''

    if old_refresh in content:
        content = content.replace(old_refresh, new_refresh)
        path.write_text(content, encoding="utf-8")
        print("refresh() updated ✅")
    else:
        print("refresh() pattern not found — will fix manually")
        for i, line in enumerate(content.split("\n")):
            if "table_card" in line or "empty_label" in line:
                print(f"  Line {i+1}: {line.strip()}")


if __name__ == "__main__":
    main()