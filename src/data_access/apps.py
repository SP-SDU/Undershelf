import logging
import os
import sys
import threading

from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command

logger = logging.getLogger(__name__)

FILE_PATH = os.path.join(settings.BASE_DIR, "data_access", "merged_dataframe.csv")


class DataAccessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_access"

    def ready(self):
        """Run migrations and seed data when in DEBUG mode."""
        # Skip if not in DEBUG mode and non-main processes in runserver to avoid duplicate runs
        if (
            not settings.DEBUG
            or "runserver" in sys.argv
            and os.environ.get("RUN_MAIN") != "true"
        ):
            return

        try:
            call_command("migrate", interactive=False)

            threading.Thread(
                target=self._seed_data_if_empty, daemon=True, name="data-seeding"
            ).start()

        except Exception as e:
            logger.error(f"Error in database setup: {e}")

    def _seed_data_if_empty(self):
        """Check if database needs seeding and run import_data if needed."""
        try:
            from data_access.models import Book

            if Book.objects.count() == 0 and os.path.exists(FILE_PATH):
                call_command("import_data", FILE_PATH)

        except Exception as e:
            logger.error(f"Error during data seeding: {e}")
