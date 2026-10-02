"""
Add FR translation keys only.
Finds the FR block and inserts missing keys.
"""
from pathlib import Path


# Same keys as before (only FR is needed)
FR_KEYS = {
    "missing_fields": "Champs manquants",
    "login_failed": "Échec de connexion",
    "please_enter_credentials": "Veuillez entrer nom d'utilisateur et mot de passe.",
    "invalid_credentials": "Nom d'utilisateur ou mot de passe invalide.",
    "welcome_back": "Bienvenue",
    "sign_in_to_continue": "Connectez-vous pour continuer",
    "username_label": "NOM D'UTILISATEUR",
    "password_label": "MOT DE PASSE",
    "enter_username": "Entrez votre nom d'utilisateur",
    "enter_password": "Entrez votre mot de passe",
    "sign_in": "Se connecter",
    "too_short": "Trop court",
    "mismatch": "Ne correspond pas",
    "error_title": "Erreur",
    "success_title": "Succès",
    "wrong_password": "Mot de passe incorrect",
    "user_not_identified": "Utilisateur non identifié.",
    "fill_all_fields": "Veuillez remplir tous les champs.",
    "new_password_too_short": "Le nouveau mot de passe doit contenir au moins 4 caractères.",
    "passwords_do_not_match": "Le nouveau mot de passe et la confirmation ne correspondent pas.",
    "password_changed": "✅ Mot de passe modifié avec succès !",
    "current_password_incorrect": "Le mot de passe actuel est incorrect.",
    "change_password_title": "Changer le mot de passe",
    "logout": "Déconnexion",
    "confirm_logout": "Voulez-vous vraiment vous déconnecter ?",
    "please_select_user": "Veuillez sélectionner un utilisateur.",
    "not_allowed": "Non autorisé",
    "cannot_delete_self_users": "Vous ne pouvez pas supprimer votre propre compte.",
    "cannot_delete_last_admin": "Impossible de supprimer le dernier administrateur.",
    "image_copy_failed": "Impossible de copier l'image :",
    "sale_complete_title": "Vente terminée !",
    "receipt_saved_title": "Reçu enregistré",
    "receipt_saved_msg": "✅ Reçu enregistré au format PDF :",
    "cannot_open_pdf": "Impossible d'ouvrir le PDF",
    "save_pdf": "💾  Enregistrer PDF",
    "open_receipt": "🖨  Ouvrir le reçu",
    "close": "Fermer",
    "click_to_save_print": (
        "💡 Cliquez sur un bouton ci-dessous pour enregistrer ou imprimer le reçu PDF.\n"
        "Le reçu s'ouvrira dans votre visionneuse PDF par défaut."
    ),
    "total_label_receipt": "Total :",
    "sale_number_short": "Vente",
}


def main():
    file_path = Path(__file__).parent / "app" / "locales" / "translations.py"
    lines = file_path.read_text(encoding="utf-8").split("\n")

    # Find FR block boundaries
    fr_start = None
    ar_start = None

    for i, line in enumerate(lines):
        if line.strip() == '"fr": {':
            fr_start = i
        elif line.strip() == '"ar": {':
            ar_start = i
            break

    if fr_start is None or ar_start is None:
        print("❌ Could not find FR or AR block")
        return

    print(f"📍 FR block: lines {fr_start + 1} to {ar_start}")
    print(f"📍 AR block starts at line {ar_start + 1}")

    # Get the FR block
    fr_block = lines[fr_start:ar_start]

    # Check which keys already exist
    existing_keys = set()
    for line in fr_block:
        stripped = line.strip()
        if stripped.startswith('"') and '":' in stripped:
            key = stripped.split('":')[0].strip('"')
            existing_keys.add(key)

    # Add missing keys right before the closing `},` of FR block
    added = 0
    for key, text in FR_KEYS.items():
        if key not in existing_keys:
            # Find last non-empty line in fr_block (before the closing `},`)
            insert_at = len(fr_block) - 1
            while insert_at > 0 and fr_block[insert_at].strip() == "":
                insert_at -= 1

            # Insert before the closing `},`
            new_line = f'        "{key}": {repr(text)},'
            fr_block.insert(insert_at, new_line)
            added += 1

    # Replace the FR block
    new_lines = lines[:fr_start] + fr_block + lines[ar_start:]
    file_path.write_text("\n".join(new_lines), encoding="utf-8")

    print(f"\n✅ FR keys added: {added}")


if __name__ == "__main__":
    main()