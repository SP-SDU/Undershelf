import threading
import os
import logging
from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)

FILE_PATH = os.path.join(settings.BASE_DIR, 'data_access', 'merged_dataframe.csv')

class DataAccessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_access"

    def ready(self):
        if settings.DEBUG:
            post_migrate.connect(init_seed_data, sender=self)


def init_seed_data(sender, **kwargs):
    from data_access.models import Book

    if Book.objects.exists():
        logger.info("Database already seeded. Skipping.")
        return

    def run():
        try:
            call_command("import_data", file_path=FILE_PATH)
            logger.info("Seeding complete.")
        except Exception as e:
            logger.error("Seeding failed: %s", e)

    threading.Thread(target=run, daemon=True).start()
