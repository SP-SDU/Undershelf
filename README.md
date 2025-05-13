<!-- PROJECT LOGO -->
<div align="center">
  <img src="images/logo.svg" alt="Logo" width="256" height="256">
  <h3 align="center">Undershelf</h3>
  <p align="center">
    Book Searching program using the Amazon API and ML.
    <br />
    <a href="https://github.com/SP-SDU/Undershelf"><strong>View Project »</strong></a>
    <br />
    <br />
    <a href="https://github.com/SP-SDU/Undershelf/issues">Issues</a>
    ·
    <a href="https://github.com/orgs/SP-SDU/projects/8">Board</a>
  </p>
</div>

## Getting Started 🚀

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)
- Download [merged_dataframe.csv](https://drive.google.com/file/d/1MVRHs_CwKTBR2Rpakx920f277IcJ0q6X/view) and place it in the `src/data_access` directory.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/SP-SDU/Undershelf.git
   cd Undershelf
   ```

### Setup and Running the Application

#### Option 1: Using the Terminal

```bash
python run.py
```

#### Option 2: Using VS Code

Press `F5` to start debugging (this will set up the project and launch the server)

### Available Commands 🔧

The following commands are available in addition to those explained above:

| Command | Description |
|---------|-------------|
| `python -m pytest -v` | Run all tests |
| `python src/manage.py makemigrations` | Create new database migrations |
| `python src/manage.py migrate` | Apply database migrations |
| `python src/manage.py import_data src/data_access/merged_dataframe.csv` | Import data from the CSV file |
| `python src/manage.py createsuperuser` | Create an admin user |
| `python src/manage.py shell` | Open Django's interactive shell |
| `python src/manage.py collectstatic --no-input` | Collect static files |

## Contributing 🤝

1. **Clone** Open [GitHub Desktop](https://desktop.github.com/), go to `File > Clone Repository`, and enter:

     ```
     https://github.com/SP-SDU/Undershelf
     ```

2. **Branch**: In GitHub Desktop, switch to `main` and create a new branch (e.g., `add-login-feature`).
3. **Commit & Push**: Commit changes in GitHub Desktop, then click `Push origin`.
4. **Pull Request**: Open a pull request on GitHub, choosing `main` as the base branch, and tag a teammate for review.

For more details, see [GitHub Flow](https://githubflow.github.io/).

## Communication 🗂️

Join the [Discord server](https://discord.gg/a2ARm52WwE) for discussions and updates.

## License 📝

Distributed under the Apache 2.0 License. See [LICENSE](LICENSE) for details.
