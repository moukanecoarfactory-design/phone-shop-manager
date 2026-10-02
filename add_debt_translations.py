"""
Add debt/payment translation keys to all 3 languages.
Run once: python add_debt_translations.py
"""
from pathlib import Path


NEW_KEYS = {
    # Payment dialog
    "pay_debt_title":       ("Pay Debt", "Payer la dette", "دفع الدين"),
    "current_debt":         ("CURRENT DEBT", "DETTE ACTUELLE", "الدين الحالي"),
    "payment_amount":       ("Payment Amount", "Montant du paiement", "مبلغ الدفع"),
    "pay_full":             ("💰 Pay Full", "💰 Payer tout", "💰 دفع الكل"),
    "payment_history":      ("Payment History", "Historique des paiements", "سجل المدفوعات"),
    "enter_notes_optional": ("Notes (optional)", "Notes (optionnel)", "ملاحظات (اختياري)"),
    "save_payment":         ("Save Payment", "Enregistrer le paiement", "حفظ الدفع"),
    "date":                 ("Date", "Date", "التاريخ"),
    "amount":               ("Amount", "Montant", "المبلغ"),

    # Messages
    "amount_must_be_positive": (
        "Amount must be greater than 0.",
        "Le montant doit être supérieur à 0.",
        "يجب أن يكون المبلغ أكبر من 0."
    ),
    "amount_exceeds_debt": (
        "Amount cannot exceed the current debt ({max}).",
        "Le montant ne peut pas dépasser la dette actuelle ({max}).",
        "لا يمكن أن يتجاوز المبلغ الدين الحالي ({max})."
    ),
    "payment_saved_title":  ("Payment Saved", "Paiement enregistré", "تم حفظ الدفع"),
    "payment_saved_msg": (
        "✅ Payment of {amount} recorded successfully!",
        "✅ Paiement de {amount} enregistré avec succès !",
        "✅ تم تسجيل دفعة بقيمة {amount} بنجاح!"
    ),

    # Customers page
    "debt_col":             ("Debt", "Dette", "الدين"),
    "pay_debt":             ("💰 Pay Debt", "💰 Payer la dette", "💰 دفع الدين"),
    "customer_debts":       ("Customer Debts", "Dettes clients", "ديون العملاء"),
    "total_debts":          ("Total Debts", "Total des dettes", "إجمالي الديون"),
    "no_debts":             ("No debts! All customers are paid up.", "Aucune dette ! Tous les clients sont à jour.", "لا توجد ديون! جميع العملاء مسددون."),
    "paid_label":           ("Paid", "Payé", "المدفوع"),
    "select_customer_first_debt": (
        "Please select a customer first.",
        "Veuillez sélectionner un client.",
        "يرجى اختيار عميل أولاً."
    ),
    "no_debt_for_customer": (
        "This customer has no debt.",
        "Ce client n'a aucune dette.",
        "هذا العميل ليس عليه ديون."
    ),

    # New Sale
    "paid_at_checkout":     ("Paid (at checkout)", "Payé (à la caisse)", "المدفوع (عند الدفع)"),
    "customer_debt_created": (
        "⚠️ Customer debt: {amount}",
        "⚠️ Dette client : {amount}",
        "⚠️ دين العميل: {amount}"
    ),
    "walk_in_no_debt": (
        "Walk-in customers must pay in full.",
        "Les clients de passage doivent payer en totalité.",
        "يجب على العملاء العابرين الدفع بالكامل."
    ),
}


def main():
    path = Path(__file__).parent / "app" / "locales" / "translations.py"
    lines = path.read_text(encoding="utf-8").split("\n")

    # Find blocks
    en_start = fr_start = ar_start = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == '"en": {':
            en_start = i
        elif stripped == '"fr": {':
            fr_start = i
        elif stripped == '"ar": {':
            ar_start = i

    if None in (en_start, fr_start, ar_start):
        print("❌ Could not find all language blocks")
        return

    def insert_keys(block_start, block_end, keys_index):
        """Insert keys before the closing `},` of the block."""
        # Find the closing `},` before the next language block starts
        insert_at = block_end - 1
        while insert_at > block_start and lines[insert_at].strip() != "},":
            insert_at -= 1

        # Build new lines
        new_lines = []
        for key, translations in NEW_KEYS.items():
            text = translations[keys_index]
            new_lines.append(f'        "{key}": {repr(text)},')

        # Insert at position
        for j, ln in enumerate(new_lines):
            lines.insert(insert_at + j, ln)

        return len(new_lines)

    # Insert in reverse order so indexes don't shift
    ar_added = insert_keys(ar_start, len(lines), 2)
    fr_added = insert_keys(fr_start, ar_start + ar_added, 1)
    en_added = insert_keys(en_start, fr_start + fr_added, 0)

    path.write_text("\n".join(lines), encoding="utf-8")

    print(f"✅ Added keys:")
    print(f"   EN: {en_added}")
    print(f"   FR: {fr_added}")
    print(f"   AR: {ar_added}")


if __name__ == "__main__":
    main()