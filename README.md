# 💎 CALIF: Cross-Asset Luxury Investment Feed

CALIF is a containerized, cloud-native monorepo for ingesting, analyzing, and delivering investment signals on luxury assets like watches, fine wine, and private jets. It leverages a modern data stack on Google Cloud Platform, with Infrastructure-as-Code managed by Terraform.

## 🏛️ Architecture

The system is composed of several microservices, all containerized with Docker and orchestrated on GCP.

```mermaid
graph TD
    subgraph "Data Acquisition"
        A[Browse AI Robots] -->|REST API Call| B(data_ingest);
    end

    subgraph "Storage"
        B --> C[BigQuery: calif_raw];
        D[Postgres: signals]
    end

    subgraph "Analytics"
        C -->|Loads data| E(Analytics Cloud Function);
        E -->|Calculates signals| D;
    end
    
    subgraph "Delivery & Presentation"
        D --> F[API on Cloud Run];
        D --> G[Streamlit Dashboard];
        D -- Pub/Sub --> H[Slack Bot Cloud Function];
        F --> I{End User};
        G --> I;
        H --> J[Slack Channel];
    end

    subgraph "Triggers"
        K[Cloud Scheduler] -->|Nightly| E;
    end

    subgraph "CI/CD"
        L[GitHub] -->|Push to main| M[Cloud Build];
        M --> N[Artifact Registry];
        N --> F;
        N --> E;
        N --> H;
    end
```

## 🚀 Quick Start (Local Development)

This project uses `docker-compose` to spin up a complete local development environment.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/perice-pope/CALIF.git
    cd CALIF
    ```

2.  **Create your environment file:**
    Copy the example environment file and fill in the required values.
    ```bash
    cp .env.example .env
    ```
    You will need to populate `your-gcp-project-id`, `your-browse-ai-api-key`, and your slack token. The `POSTGRES_DB_URL` is already configured for the local docker network.

3.  **Create a `.env.example` file with the following content:**
    ```
    # --- GCP Configuration ---
    GCP_PROJECT_ID="your-gcp-project-id"

    # --- Browse AI Configuration ---
    BROWSE_AI_API_KEY="your-browse-ai-api-key"
    WATCHCHARTS_ROBOT_ID="your-watchcharts-robot-id"
    LIV_EX_ROBOT_ID="your-liv-ex-robot-id"
    CHARTERAPI_ROBOT_ID="your-charterapi-robot-id"

    # --- Local Postgres (for docker-compose) ---
    POSTGRES_USER="calif_user"
    POSTGRES_PASSWORD="a_strong_password"
    POSTGRES_DB="calif"
    # This is the connection URL your services will use to connect to the docker-compose Postgres instance
    POSTGRES_DB_URL="postgresql+psycopg2://calif_user:a_strong_password@postgres:5432/calif"

    # --- Local pgAdmin (for docker-compose) ---
    PGADMIN_DEFAULT_EMAIL="admin@example.com"
    PGADMIN_DEFAULT_PASSWORD="admin"

    # --- Slack Configuration ---
    SLACK_BOT_TOKEN="your-slack-bot-token"
    SLACK_CHANNEL="#your-channel"
    ```

4.  **Launch the services:**
    A `Makefile` is provided for convenience.
    ```bash
    make dev
    ```
    This command will build and run all the services defined in `docker-compose.yml`.

    Your services will be available at:
    *   **API**: `http://localhost:8000`
    *   **API Docs**: `http://localhost:8000/docs`
    *   **Dashboard**: `http://localhost:8501`
    *   **pgAdmin**: `http://localhost:5050`

## ☁️ CI/CD Flow

This project uses Google Cloud Build for continuous integration and deployment. The pipeline is defined in `cloudbuild.yaml`.

*   **Trigger**: A push to the `main` branch on GitHub.
*   **Pipeline**:
    1.  **Build**: Docker images for the `api`, `analytics`, and `slack_bot` services are built.
    2.  **Push**: The newly built images are pushed to Google Artifact Registry.
    3.  **Deploy**:
        *   The `calif-api` Cloud Run service is updated with the latest API image.
        *   The `calif-analytics` and `calif-slack-bot` Cloud Functions are updated with their respective new images.

##  Terraform Deployment

The entire GCP infrastructure for this project is managed with Terraform.

1.  **Install Terraform**: Ensure you have Terraform (>=1.7) installed.

2.  **Authenticate with GCP**:
    ```bash
    gcloud auth application-default login
    ```

3.  **Create a `terraform.tfvars` file**:
    In the `terraform/` directory, create a file named `terraform.tfvars` and populate it with your sensitive variables.
    ```tf
    gcp_project_id    = "your-gcp-project-id"
    slack_bot_token   = "your-slack-bot-token"
    browse_ai_api_key = "your-browse-ai-api-key"
    postgres_db_url   = "your-production-postgres-url"
    ```

4.  **Initialize and Apply**:
    Navigate to the Terraform directory and run the following commands:
    ```bash
    cd terraform
    terraform init
    terraform plan
    terraform apply
    ```

##  API Reference

### GET `/signals`

Returns a list of all active deal signals.

*   **Response `200 OK`**
    ```json
    [
      {
        "asset_type": "watch",
        "last_price": 8000,
        "rolling_mean_30d": 125.86,
        "z_score": -2.5,
        "is_deal": true,
        "updated_at": "2023-10-27T10:00:00Z"
      }
    ]
    ```

### GET `/index`

Returns a list of computed market indices. (Placeholder)

*   **Response `200 OK`**
    ```json
    [
      {
        "name": "WatchIndex",
        "value": 1234.56,
        "updated_at": "2023-10-27T10:00:00Z"
      }
    ]
    ```

##  slack Alert Payload

When a new deal is identified, a notification is sent to the configured Slack channel with the following format:

> **New Deal Signal: Watch**
> *Asset Type*: Watch
> *Current Price*: $8,000.00
> *30-Day Avg Price*: $125.86
> *Z-Score*: -2.50
