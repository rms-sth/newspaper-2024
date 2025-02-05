import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from translations import TRANSLATIONS


class Command(BaseCommand):
    help = "Update translations from Python dictionary and compile messages."

    def handle(self, *args, **kwargs):
        # Define base locale directory
        locale_base_dir = os.path.join(settings.BASE_DIR, "locale")

        for lang, translations in TRANSLATIONS.items():
            # Define language-specific directory
            locale_dir = os.path.join(locale_base_dir, lang, "LC_MESSAGES")
            po_file_path = os.path.join(locale_dir, "django.po")

            # Ensure the locale directory exists
            os.makedirs(locale_dir, exist_ok=True)

            # Write translations to .po file
            with open(po_file_path, "w", encoding="utf-8") as po_file:
                po_file.write(
                    'msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
                )

                for key, msgstr in translations.items():
                    po_file.write(f'msgid "{key}"\n')
                    po_file.write(f'msgstr "{msgstr}"\n\n')

            self.stdout.write(
                self.style.SUCCESS(
                    f"Successfully updated translations for {lang}: {po_file_path}"
                )
            )

        # Compile messages using call_command
        call_command("compilemessages")

        self.stdout.write(self.style.SUCCESS("Successfully compiled translations."))
