# Mantis Integration Service

This service provides an API endpoint for creating Mantis spaces from uploaded data. It's built using Flask and the Mantis SDK, leveraging Celery for asynchronous task processing.

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

## Running the Application with Docker Compose

This project is designed to be run using Docker Compose. This simplifies the setup and ensures consistency across different environments.

1.  **Navigate to the `docker` directory:**

    ```bash
    cd docker
    ```

2.  **Start the application using Docker Compose:**

    ```bash
    docker-compose up -d --build
    ```

    *   `-d` runs the containers in detached mode (in the background).
    *   `--build` builds the Docker images if they don't exist or if there are changes to the Dockerfiles.

    To simply start the application after the initial build, you can use:

    ```bash
    docker-compose up
    ```

3.  **Accessing the application:**

    The application will be accessible at `http://localhost:8111`.

4.  **Stopping the application:**

    ```bash
    docker-compose down
    ```

## Configuration

Configuration is primarily managed through environment variables. These can be set directly in your shell or, more conveniently, in `.env` files.

*   `.env`:  For production settings.  This file should contain your production-specific configurations.
*   `.env.development`: For local development overrides. This file is not tracked by Git.

To use a local frontend in the backend, create a `.env.development` file and assign `MANTIS_HOST=http://host.docker.internal:3000`, and `MANTIS_DOMAIN=localhost`.

***Note***: When using a local frontend with the backend inside Docker, you must use `host.docker.internal` as the `MANTIS_HOST`. This is because the backend runs inside a Docker container and needs a way to access services running on your host machine (i.e., your local frontend). `host.docker.internal` resolves to the internal IP address used by Docker to reach the host.

### Key Environment Variables:

*   `FLASK_ENV`:  Set to `development` or `production`.
*   `CELERY_BROKER_URL`:  The URL for the Celery broker (e.g., Redis).
*   `CELERY_RESULT_BACKEND`: The URL for the Celery result backend (e.g., Redis).
*   `MANTIS_HOST`: The hostname or IP address of the Mantis service.
*   `MANTIS_DOMAIN`: The domain of the Mantis service.

## Celery: Asynchronous Task Processing

This service uses Celery to handle long-running or background tasks, such as creating Mantis spaces. Celery allows the API to respond quickly to requests while the actual space creation happens asynchronously.

*   **Tasks:** The `src/tasks/space_tasks.py` file contains Celery tasks, such as `process_space_creation`.
*   **Worker:** The Celery worker is a separate process that executes these tasks.  It's defined as the `celery_worker` service in `docker-compose.yml`.
*   **Broker:**  Celery uses a message broker (Redis in this case) to send tasks to the worker and receive results.
*   **Result Backend:** Celery stores the results of tasks in a result backend (also Redis).

When you call the `/create-space` API endpoint:

1.  The API enqueues a `process_space_creation` task with Celery.
2.  Celery adds the task to the Redis queue.
3.  The Celery worker picks up the task from the queue and executes it.
4.  The worker stores the result (success, failure, or progress) in the Redis result backend.
5.  The API can then query the status of the task using the task ID.

## API Information

### `POST /api/create-space`

Creates a new Mantis space from the provided data.

### `GET /api/space-task-status/<task_id>`

Retrieves the status of a space creation task given its task ID.  Returns the state of the task, and if completed, the result or error information.

### `GET /api/get-space-id/<job>`

Retrieves the space ID and layer ID associated with a given job. This endpoint queries the Redis cache to find the corresponding space and layer IDs.

### `GET /api/get_proxy/<path:url>`

Acts as a proxy to fetch content from the specified URL. This can be useful for bypassing CORS restrictions or accessing resources that require authentication. The URL should be properly encoded.
