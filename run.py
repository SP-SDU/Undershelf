import argparse
import os
import platform
import subprocess
import urllib.request
import venv
import zipfile


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


def check_if_data_exists(python_exe):
    check_script = """
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()
from data_access.models import Book
book_count = Book.objects.count()
print(1 if book_count > 0 else 0)
"""

    try:
        result = subprocess.run(
            f"{python_exe} -c '{check_script}'",
            shell=True,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0 and result.stdout.strip() == "1":
            return True
        return False
    except Exception as e:
        print(f"\033[93mWarning: Could not check database: {e}\033[0m")
        return False


def download_or_get_csv():
    csv_path = os.path.join("src", "data_access", "merged_dataframe.csv")

    if os.path.exists(csv_path):
        print("\033[92mCSV file found.\033[0m")
        return csv_path

    print("\033[93mCSV file not found. Downloading...\033[0m")
    url = "https://drive.usercontent.google.com/download?id=1MVRHs_CwKTBR2Rpakx920f277IcJ0q6X&authuser=0&confirm=t"
    zip_path = os.path.join("src", "data_access", "merged_dataframe.zip")

    try:
        os.makedirs(os.path.dirname(csv_path), exist_ok=True)

        # Download the ZIP file
        print("\033[92mDownloading ZIP file...\033[0m")
        with urllib.request.urlopen(url) as response:
            if response.getcode() != 200:
                raise Exception(f"HTTP error: {response.getcode()}")

            with open(zip_path, "wb") as file:
                chunk_size = 8192
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    file.write(chunk)

        # Extract the ZIP file
        print("\033[92mExtracting ZIP file...\033[0m")
        data_access_dir = os.path.join("src", "data_access")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(data_access_dir)

        # Remove the ZIP file after extraction
        os.remove(zip_path)

        if os.path.exists(csv_path):
            print("\033[92mCSV file extracted successfully.\033[0m")
            return csv_path
        else:
            print("\033[91mNo CSV file found in the extracted ZIP.\033[0m")
            return None

    except Exception as e:
        print(f"\033[91mError processing file: {e}\033[0m")
        return None


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
    if not check_if_data_exists(python_exe):
        csv_path = download_or_get_csv()
        if not csv_path:
            print("\033[91mFailed to get CSV file. Exiting.\033[0m")
            exit(1)
        run_command(
            f"{python_exe} src/manage.py import_data {csv_path}",
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
