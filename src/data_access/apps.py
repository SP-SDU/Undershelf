import logging
import os
import sys
import threading

from django.apps import AppConfig
from django.conf import settings

logger = logging.getLogger(__name__)


class DataAccessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_access"

    def ready(self):
        """Handle database migrations and data seeding in the appropriate startup phases."""
        # Only proceed in main thread and debug mode
        if (
            not settings.DEBUG
            or threading.current_thread() is not threading.main_thread()
        ):
            return

        is_runserver = "runserver" in sys.argv
        run_main = os.environ.get("RUN_MAIN")

        if is_runserver and run_main is None:
            # Initial phase - Run migrations
            self._run_migrations()
        elif is_runserver and run_main == "true":
            # Server phase - Start data seeding in background
            threading.Thread(
                target=self._seed_data_if_empty, daemon=True, name="data-seeding"
            ).start()

    def _run_migrations(self):
        """Run migrations before the server starts."""
        try:
            from django.core.management import call_command

            call_command("migrate", interactive=False)
        except Exception as e:
            logger.error(f"Migration error: {e}")

    def _seed_data_if_empty(self):
        """Seed database if it's empty."""
        try:
            from django.contrib.auth.models import User
            from django.core.management import call_command

            from data_access.models import Book

            # Only seed a user if none exists
            if User.objects.count() == 0:
                logger.info("Creating default admin user")

                # Set env from settings
                os.environ["DJANGO_SUPERUSER_USERNAME"] = (
                    settings.DJANGO_SUPERUSER_USERNAME
                )
                os.environ["DJANGO_SUPERUSER_EMAIL"] = settings.DJANGO_SUPERUSER_EMAIL
                os.environ["DJANGO_SUPERUSER_PASSWORD"] = (
                    settings.DJANGO_SUPERUSER_PASSWORD
                )

                # Create the superuser using env
                call_command("createsuperuser", "--noinput")
                logger.info("Default admin user created successfully")

            # Only seed data if the database is empty
            if Book.objects.count() == 0 and os.path.exists(settings.CSV_FILE_PATH):
                call_command("import_data", settings.CSV_FILE_PATH)
        except Exception as e:
            logger.error(f"Data seeding error: {e}")
