import argparse
import os
import platform
import subprocess
import sys
import venv


def run_command(command, description=None):
    if description:
        print(f"\033[92m{description}...\033[0m")

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
    )

    if process.stdout:
        for line in process.stdout:
            print(line, end="")

    process.wait()
    if process.returncode != 0:
        print(f"\033[91mCommand failed with return code {process.returncode}\033[0m")
        return False
    return True


def get_venv_python_path():
    if platform.system() == "Windows":
        python_exe = os.path.join(os.getcwd(), ".venv", "Scripts", "python.exe")
    else:
        python_exe = os.path.join(os.getcwd(), ".venv", "bin", "python")
    return python_exe


def create_venv_if_not_exists():
    if not os.path.exists(".venv"):
        print("\033[92mCreating virtual environment...\033[0m")
        venv.create(".venv", with_pip=True)
        return True
    return False


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--setup-only",
        action="store_true",
    )
    return parser.parse_args()


def create_superuser(python_exe):
    print("\033[92mCreating superuser if needed...\033[0m")

    os.environ.setdefault("DJANGO_SUPERUSER_USERNAME", "root")
    os.environ.setdefault("DJANGO_SUPERUSER_PASSWORD", "root")
    os.environ.setdefault("DJANGO_SUPERUSER_EMAIL", "root@undershelf.com")

    run_command(
        f"{python_exe} src/manage.py createsuperuser --noinput", "Creating superuser"
    )


def check_if_data_exists():
    try:
        # Set Python path to include the src directory
        src_path = os.path.join(os.getcwd(), "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
        import django

        django.setup()

        from data_access.models import Book

        book_count = Book.objects.count()
        return book_count > 0
    except Exception as e:
        print(f"\033[93mWarning: Could not check database: {e}\033[0m")
        return False


def main():
    create_venv_if_not_exists()
    python_exe = get_venv_python_path()

    run_command(
        f"{python_exe} -m pip install -r requirements.txt",
        "Installing requirements",
    )
    run_command(
        f"{python_exe} src/manage.py makemigrations",
        "Making migrations",
    )
    run_command(f"{python_exe} src/manage.py migrate", "Running migrations")

    create_superuser(python_exe)

    print("\033[92mChecking if data needs to be imported...\033[0m")
    if not check_if_data_exists():
        run_command(
            f"{python_exe} src/manage.py import_data src/data_access/merged_dataframe.csv",
            "Importing data from CSV",
        )
    else:
        print("\033[92mData already exists in the database. Skipping import.\033[0m")

    args = parse_arguments()
    if args.setup_only:
        print("\033[92mSetup complete.\033[0m")
    else:
        print("\033[92mStarting development server...\033[0m")
        print("\033[93mPress Ctrl+C to stop the server\033[0m")
        subprocess.call([python_exe, "src/manage.py", "runserver"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\033[93mInterrupted. Exiting.\033[0m")
    except Exception as e:
        print(f"\n\033[91mAn error occurred: {e}\033[0m")
        exit(1)
