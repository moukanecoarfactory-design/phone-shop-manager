"""
Add missing translation keys for dialogs, messages, and login window.
Run once: python update_translations.py
"""
import re
from pathlib import Path


# ============================================================
# NEW KEYS to add (only the ones not already present)
# Format: key → (EN, FR, AR)
# ============================================================
NEW_KEYS = {
    # Login window
    "missing_fields":    ("Missing Fields", "Champs manquants", "حقول مفقودة"),
    "login_failed":      ("Login Failed", "Échec de connexion", "فشل تسجيل الدخول"),
    "please_enter_credentials": (
        "Please enter username and password.",
        "Veuillez entrer nom d'utilisateur et mot de passe.",
        "يرجى إدخال اسم المستخدم وكلمة المرور."
    ),
    "invalid_credentials": (
        "Invalid username or password.",
        "Nom d'utilisateur ou mot de passe invalide.",
        "اسم المستخدم أو كلمة المرور غير صحيحة."
    ),
    "welcome_back":      ("Welcome Back", "Bienvenue", "مرحباً بعودتك"),
    "sign_in_to_continue": ("Sign in to continue", "Connectez-vous pour continuer", "سجل الدخول للمتابعة"),
    "username_label":    ("USERNAME", "NOM D'UTILISATEUR", "اسم المستخدم"),
    "password_label":    ("PASSWORD", "MOT DE PASSE", "كلمة المرور"),
    "enter_username":    ("Enter your username", "Entrez votre nom d'utilisateur", "أدخل اسم المستخدم"),
    "enter_password":    ("Enter your password", "Entrez votre mot de passe", "أدخل كلمة المرور"),
    "sign_in":           ("Sign In", "Se connecter", "تسجيل الدخول"),

    # Change password dialog
    "too_short":         ("Too Short", "Trop court", "قصيرة جداً"),
    "mismatch":          ("Mismatch", "Ne correspond pas", "غير متطابق"),
    "error_title":       ("Error", "Erreur", "خطأ"),
    "success_title":     ("Success", "Succès", "نجاح"),
    "wrong_password":    ("Wrong Password", "Mot de passe incorrect", "كلمة مرور خاطئة"),
    "user_not_identified": ("User not identified.", "Utilisateur non identifié.", "المستخدم غير معروف."),
    "fill_all_fields": (
        "Please fill all fields.",
        "Veuillez remplir tous les champs.",
        "يرجى ملء جميع الحقول."
    ),
    "new_password_too_short": (
        "New password must be at least 4 characters.",
        "Le nouveau mot de passe doit contenir au moins 4 caractères.",
        "يجب أن تكون كلمة المرور الجديدة 4 أحرف على الأقل."
    ),
    "passwords_do_not_match": (
        "New password and confirmation do not match.",
        "Le nouveau mot de passe et la confirmation ne correspondent pas.",
        "كلمة المرور الجديدة والتأكيد غير متطابقين."
    ),
    "password_changed": (
        "✅ Password changed successfully!",
        "✅ Mot de passe modifié avec succès !",
        "✅ تم تغيير كلمة المرور بنجاح!"
    ),
    "current_password_incorrect": (
        "Current password is incorrect.",
        "Le mot de passe actuel est incorrect.",
        "كلمة المرور الحالية غير صحيحة."
    ),
    "change_password_title": ("Change Password", "Changer le mot de passe", "تغيير كلمة المرور"),

    # Main window (logout)
    "logout":            ("Logout", "Déconnexion", "تسجيل الخروج"),
    "confirm_logout":    ("Are you sure you want to logout?", "Voulez-vous vraiment vous déconnecter ?", "هل أنت متأكد من تسجيل الخروج؟"),

    # Generic
    "please_select_user": (
        "Please select a user first.",
        "Veuillez sélectionner un utilisateur.",
        "يرجى اختيار مستخدم أولاً."
    ),
    "not_allowed":       ("Not Allowed", "Non autorisé", "غير مسموح"),
    "cannot_delete_self_users": (
        "You cannot delete your own account.",
        "Vous ne pouvez pas supprimer votre propre compte.",
        "لا يمكنك حذف حسابك الخاص."
    ),
    "cannot_delete_last_admin": (
        "Cannot delete the last admin.",
        "Impossible de supprimer le dernier administrateur.",
        "لا يمكن حذف المدير الأخير."
    ),

    # Image copy error
    "image_copy_failed": (
        "Could not copy image:",
        "Impossible de copier l'image :",
        "تعذر نسخ الصورة:"
    ),

    # Receipt dialog
    "sale_complete_title": ("Sale Complete!", "Vente terminée !", "تم إتمام البيع!"),
    "receipt_saved_title": ("Receipt Saved", "Reçu enregistré", "تم حفظ الإيصال"),
    "receipt_saved_msg": (
        "✅ Receipt saved as PDF:",
        "✅ Reçu enregistré au format PDF :",
        "✅ تم حفظ الإيصال بصيغة PDF:"
    ),
    "cannot_open_pdf":   ("Cannot Open PDF", "Impossible d'ouvrir le PDF", "تعذر فتح PDF"),
    "save_pdf":          ("💾  Save PDF", "💾  Enregistrer PDF", "💾  حفظ PDF"),
    "open_receipt":      ("🖨  Open Receipt", "🖨  Ouvrir le reçu", "🖨  فتح الإيصال"),
    "close":             ("Close", "Fermer", "إغلاق"),
    "click_to_save_print": (
        "💡 Click a button below to save or print the receipt PDF.\nThe receipt will open in your default PDF viewer.",
        "💡 Cliquez sur un bouton ci-dessous pour enregistrer ou imprimer le reçu PDF.\nLe reçu s'ouvrira dans votre visionneuse PDF par défaut.",
        "💡 انقر على زر أدناه لحفظ أو طباعة الإيصال بصيغة PDF.\nسيفتح الإيصال في عارض PDF الافتراضي."
    ),
    "total_label_receipt": ("Total:", "Total :", "الإجمالي:"),
    "sale_number_short": ("Sale", "Vente", "بيع"),
}


def update_translations_file():
    """Read the current file, add new keys, save back."""
    file_path = Path(__file__).parent / "app" / "locales" / "translations.py"

    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False

    content = file_path.read_text(encoding="utf-8")

    # Track additions
    added_en = 0
    added_fr = 0
    added_ar = 0

    for key, (en_text, fr_text, ar_text) in NEW_KEYS.items():
        key_line = f'"{key}":'

        # --- Check EN ---
        if key_line not in content:
            # Find the EN block end — insert before the next `},\n    "fr":`
            en_insert_marker = '    },\n    "fr":'
            if en_insert_marker in content:
                new_line = f'        "{key}": {repr(en_text)},\n'
                content = content.replace(en_insert_marker, new_line + en_insert_marker, 1)
                added_en += 1

        # --- Check FR ---
        if key_line not in content or content.count(key_line) < 2:
            fr_insert_marker = '    },\n    "ar":'
            if fr_insert_marker in content:
                new_line = f'        "{key}": {repr(fr_text)},\n'
                content = content.replace(fr_insert_marker, new_line + fr_insert_marker, 1)
                added_fr += 1

        # --- Check AR ---
        if key_line not in content or content.count(key_line) < 3:
            ar_insert_marker = '    },\n}'
            if ar_insert_marker in content:
                new_line = f'        "{key}": {repr(ar_text)},\n'
                content = content.replace(ar_insert_marker, new_line + ar_insert_marker, 1)
                added_ar += 1

    file_path.write_text(content, encoding="utf-8")

    print(f"✅ File updated: {file_path}")
    print(f"   EN keys added: {added_en}")
    print(f"   FR keys added: {added_fr}")
    print(f"   AR keys added: {added_ar}")
    print(f"\n🎉 Done! Now test with:")
    print(f'   python -c "from app.locales.translations import t; print(t(chr(39)+\'login_failed\'+chr(39), \'fr\'))"')


if __name__ == "__main__":
    update_translations_file()