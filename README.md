# Mantis Integration Service

This service provides an API endpoint for creating Mantis spaces from uploaded data. It's built using Flask and the Mantis SDK.

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/KellisLab/MantisExtensionsBackend.git
    cd MantisExtensionsBackend
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    venv\Scripts\activate  # On Windows
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r src/requirements.txt
    ```

4. **Install Playwright**

    ```bash
    python -m playwright install
    ```

    **Note:** If the Playwright installation fails, try running:

    ```bash
    python -m playwright install-deps
    ```

    before proceeding.

## Getting Started

1.  **Set environment variables:**

    *   You may need to set environment variables for Mantis SDK configuration, depending on your setup. To do this, you can edit the .env file for production, or create a `.env.development` file (in the same directory as `.env`), which won't be included in git pushes.
    * To use a local frontend in the backend, create a `.env.development` file and assign `MANTIS_HOST=http://localhost:3000`, and `MANTIS_DOMAIN=localhost`.

    ***Note***: If you are using a local backend, you must run it with docker, or the space creation will NOT work. To do so, `cd docker` from the backend root (MantisAPI), then `docker compose up -d --build`. After you run the build once, you can re-run it simply with `docker compose up`. If things dno't work, check the logs and make sure they are not empty.

2.  **Run the Flask application:**

    ```bash
    python src/app.py
    ```

    The application will start on port 5111 (by default) in debug mode.

## API Information

### `POST /create-space`

Creates a new Mantis space from the provided data.

**Request Body:**

```json
{
  "cookie": "your_mantis_cookie",
  "data": [
    {"col1": "value1", "col2": "value2"},
    {"col1": "value3", "col2": "value4"}
  ],
  "name": "Connection Name (Optional, defaults to a UUIDv4)",
  "data_types": {
    "col1": "semantic",
    "col2": "numeric"
  },
  "reducer": "UMAP (Optional, defaults to UMAP)",
  "privacy_level": "PRIVATE (Optional, defaults to PRIVATE)"
}