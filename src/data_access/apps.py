from django.apps import AppConfig


class DataAccessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "data_access"

    def ready(self):
        """
        Method called when Django has loaded all apps and is ready.
        We use this to initialize our database with seed data.
        """
        # Import here to avoid AppRegistryNotReady exception
        import sys

        from data_access.seeds import seed

        if "runserver" in sys.argv:
            # Only run the seeder in the main process to avoid double-seeding
            if not any("reload" in arg for arg in sys.argv):
                seed()
