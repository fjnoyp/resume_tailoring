## Running Instructions

### 1. Setup & Installation:

This project uses Poetry for dependency management and packaging.

1.  **Install Poetry:** If you don't have Poetry installed, follow the instructions on the [official Poetry website](https://python-poetry.org/docs/#installation).
2.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <your-repository-url>
    cd resume_tailoring
    ```
3.  **Install dependencies:** This will create a virtual environment (if `virtualenvs.in-project` is true, it will be in a `.venv` directory in the project root) and install all necessary packages from `pyproject.toml` and `poetry.lock`.
    ```bash
    poetry install
    ```

### 2. Running the app locally:

To run commands or scripts, you can either activate Poetry's virtual environment or use `poetry run`.

*   **Activate the virtual environment (recommended for interactive sessions):**
    Since Poetry version 2.0.0, `poetry shell` is an optional plugin. The direct way to activate the environment (created in the `.venv` directory by `poetry install` when `virtualenvs.in-project` is true) is:

    *   **Linux/macOS:**
        ```bash
        source .venv/bin/activate
        ```
    *   **Windows (CMD):**
        ```cmd
        .venv\\Scripts\\activate.bat
        ```
    *   **Windows (PowerShell):**
        ```powershell
        .venv\\Scripts\\Activate.ps1
        ```
    Once activated, your terminal prompt will usually change, and you can run Python scripts or other commands directly (e.g., `python your_script.py`, `langgraph dev`). To deactivate, type `deactivate`.

*   **Using `poetry run` (for single commands):** This command runs a specified command within the Poetry-managed environment without needing to activate it first.

