from pathlib import Path

NEW_KEYS = {
    "sign_in_to_continue": ("Sign in to continue", "Connectez-vous pour continuer", "سجل الدخول للمتابعة"),
    "username_label": ("USERNAME", "NOM D'UTILISATEUR", "اسم المستخدم"),
    "password_label": ("PASSWORD", "MOT DE PASSE", "كلمة المرور"),
    "enter_username": ("Enter your username", "Entrez votre nom d'utilisateur", "أدخل اسم المستخدم"),
    "enter_password": ("Enter your password", "Entrez votre mot de passe", "أدخل كلمة المرور"),
    "sign_in": ("Sign In", "Se connecter", "تسجيل الدخول"),
    "welcome_back": ("Welcome Back", "Bienvenue", "مرحباً بعودتك"),
    "missing_fields": ("Missing Fields", "Champs manquants", "حقول مفقودة"),
    "login_failed": ("Login Failed", "Échec de connexion", "فشل تسجيل الدخول"),
    "please_enter_credentials": ("Please enter username and password.", "Veuillez entrer vos identifiants.", "يرجى إدخال بيانات الدخول."),
    "invalid_credentials": ("Invalid username or password.", "Identifiants invalides.", "بيانات الدخول غير صحيحة."),
    "management_system": ("Management System", "Système de gestion", "نظام الإدارة"),
    "customer_debts": ("Customer Debts", "Dettes clients", "ديون العملاء"),
    "change_password_title": ("Change Password", "Changer le mot de passe", "تغيير كلمة المرور"),
    "logout": ("Logout", "Déconnexion", "تسجيل الخروج"),
    "confirm_logout": ("Are you sure you want to logout?", "Voulez-vous vraiment vous déconnecter ?", "هل أنت متأكد من تسجيل الخروج؟"),
    "too_short": ("Too Short", "Trop court", "قصيرة جداً"),
    "mismatch": ("Mismatch", "Ne correspond pas", "غير متطابق"),
    "error_title": ("Error", "Erreur", "خطأ"),
    "success_title": ("Success", "Succès", "نجاح"),
    "wrong_password": ("Wrong Password", "Mot de passe incorrect", "كلمة مرور خاطئة"),
    "user_not_identified": ("User not identified.", "Utilisateur non identifié.", "المستخدم غير معروف."),
    "fill_all_fields": ("Please fill all fields.", "Veuillez remplir tous les champs.", "يرجى ملء جميع الحقول."),
    "new_password_too_short": ("Password must be at least 4 characters.", "Le mot de passe doit contenir au moins 4 caractères.", "يجب أن تكون كلمة المرور 4 أحرف على الأقل."),
    "passwords_do_not_match": ("Passwords do not match.", "Les mots de passe ne correspondent pas.", "كلمتا المرور غير متطابقتين."),
    "password_changed": ("Password changed!", "Mot de passe modifié !", "تم تغيير كلمة المرور!"),
    "current_password_incorrect": ("Current password is incorrect.", "Le mot de passe actuel est incorrect.", "كلمة المرور الحالية غير صحيحة."),
    "created_col": ("Created", "Créé le", "تاريخ الإنشاء"),
    "not_allowed": ("Not Allowed", "Non autorisé", "غير مسموح"),
    "please_select_user": ("Please select a user first.", "Veuillez sélectionner un utilisateur.", "يرجى اختيار مستخدم أولاً."),
    "cannot_delete_self_users": ("You cannot delete your own account.", "Vous ne pouvez pas supprimer votre propre compte.", "لا يمكنك حذف حسابك الخاص."),
    "cannot_delete_last_admin": ("Cannot delete the last admin.", "Impossible de supprimer le dernier administrateur.", "لا يمكن حذف المدير الأخير."),
    "capacity": ("Capacity", "Capacité", "السعة"),
    "total_sales_col": ("Total Sales", "Total des ventes", "إجمالي المبيعات"),
    "today_section": ("Today", "Aujourd'hui", "اليوم"),
    "address_label": ("Address", "Adresse", "العنوان"),
    "city_label": ("City", "Ville", "المدينة"),
    "phone_label": ("Phone", "Téléphone", "الهاتف"),
    "email_label": ("Email", "Email", "البريد الإلكتروني"),
    "website_label": ("Website", "Site web", "الموقع"),
    "optional": ("(optional)", "(optionnel)", "(اختياري)"),
    "currency_display": ("MAD", "DH", "درهم"),
}


def main():
    path = Path(__file__).parent / "app" / "locales" / "translations.py"
    lines = path.read_text(encoding="utf-8").split("\n")

    en_idx = fr_idx = ar_idx = None
    for i, line in enumerate(lines):
        s = line.strip()
        if s == '"en": {': en_idx = i
        elif s == '"fr": {': fr_idx = i
        elif s == '"ar": {': ar_idx = i

    if None in (en_idx, fr_idx, ar_idx):
        print("ERROR: blocks not found")
        return

    def add_block(start, end, idx):
        pos = end - 1
        while pos > start and lines[pos].strip() != "},":
            pos -= 1
        n = 0
        for k, v in NEW_KEYS.items():
            marker = '"' + k + '":'
            if any(marker in lines[j] for j in range(start, end)):
                continue
            lines.insert(pos, '        "' + k + '": ' + repr(v[idx]) + ',')
            pos += 1
            n += 1
        return n

    ar_n = add_block(ar_idx, len(lines), 2)
    fr_n = add_block(fr_idx, ar_idx + ar_n, 1)
    en_n = add_block(en_idx, fr_idx + fr_n, 0)

    path.write_text("\n".join(lines), encoding="utf-8")
    print("Added EN=" + str(en_n) + " FR=" + str(fr_n) + " AR=" + str(ar_n))


if __name__ == "__main__":
    main()