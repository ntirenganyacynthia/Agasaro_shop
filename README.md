# Agasaro Shop Backend

The **Agasaro Shop Backend** is the server-side API for the Agasaro retail  platform. It provides the backend services required by the Agasaro frontend and manages authentication, authorization, products, categories, suppliers, customers, sales, sale items, payments, receipts, checkout operations, and user management.

The backend is implemented with **FastAPI** and communicates with a relational database through SQLAlchemy. It exposes RESTful API endpoints that are consumed by the Agasaro frontend and other authorized clients.

The production backend is deployed on Render.

## Application Structure

The Agasaro backend is organized into API routers, database models, configuration, infrastructure utilities, migrations, and supporting scripts.

```text
Agasaro_shop
│
├── app/
│   ├── core/
│   │   └── Configuration and application settings
│   │
│   ├── infrastructure/
│   │   ├── Runtime configuration
│   │   ├── Rate limiting
│   │   └── Startup validation
│   │
│   ├── routers/
│   │   ├── auth
│   │   ├── checkout
│   │   ├── product
│   │   ├── user
│   │   ├── customer
│   │   ├── category
│   │   ├── supplier
│   │   ├── sale
│   │   ├── sale_item
│   │   ├── payment
│   │   └── receipt
│   │
│   ├── models
│   ├── database
│   └── main.py
│
├── migrations/
├── add_products.sql
├── add_suppliers.sql
├── generate_momo_credentials.py
├── init_remote_db.py
├── run_sql.py
├── seed_admin.py
├── requirements.txt
└── .gitignore
```

The project separates API routing, database functionality, configuration, and supporting infrastructure so that individual areas of the application can be maintained independently.

## Technology Stack

| Technology | Purpose |
| ---------- | ------- |
| Python | Backend application development |
| FastAPI | REST API framework |
| Uvicorn | ASGI server used to run the FastAPI application |
| SQLAlchemy | Database ORM and database model management |
| PostgreSQL | Relational database |
| Pydantic | Data validation and configuration |
| SlowAPI | API rate limiting |
| Alembic / migrations | Database schema migration support |
| Render | Production backend deployment |
| GitHub | Source code management |

## Backend Architecture

The backend follows a modular FastAPI architecture.

The main application is created in `app/main.py`. API functionality is separated into routers, while database models and infrastructure utilities are maintained in their respective modules.

The application includes routers for:

* Authentication
* Checkout
* Products
* Users
* Customers
* Categories
* Suppliers
* Sales
* Sale items
* Payments
* Receipts

This structure keeps API responsibilities separated and allows the backend to provide a consistent RESTful interface to the frontend.

## FastAPI Application

The main FastAPI application is created in:

```text
app/main.py
```

The application:

* Creates the FastAPI application
* Configures CORS
* Configures rate limiting
* Registers API routers
* Performs startup configuration validation
* Provides system health endpoints

The API application is configured with the title:

```text
Agasaro API
```

and version:

```text
2.0.0
```

## API Routers

The backend registers the following API routers:

```text
Authentication
Checkout
Products
Users
Customers
Categories
Suppliers
Sales
Sale Items
Payments
Receipts
```

Each router is responsible for the endpoints and operations associated with its domain.

### Authentication

The authentication router provides backend authentication functionality.

Authentication is responsible for validating users and supporting access to protected API operations.

### Products

The product router provides product-related API functionality.

Product information includes fields such as:

* Product ID
* Category
* Supplier
* Product name
* Unit price
* Stock quantity
* Reserved quantity
* Available quantity

The production products endpoint is:

```text
https://agasaro-shop.onrender.com/products/
```

### Categories

The category router manages product category-related operations.

Categories allow products to be organized according to their product classification.

### Suppliers

The supplier router provides supplier-related operations and supports the relationship between products and their suppliers.

### Customers

The customer router provides customer-related backend functionality.

Customer information can be used by sales and checkout processes supported by the system.

### Users

The user router provides user-management functionality.

User operations are protected according to the authentication and authorization rules implemented by the backend.

### Sales

The sales router provides functionality related to sales transactions.

Sales are associated with products, customers, and sale items as appropriate.

### Sale Items

The sale-item router manages the individual products associated with sales transactions.

This allows a sale to contain multiple products and quantities.

### Payments

The payment router provides payment-related backend functionality.

The backend contains payment integration support as part of the Agasaro POS system.

### Receipts

The receipt router provides receipt-related functionality associated with completed transactions.

### Checkout

The checkout router provides the backend operations required to process checkout workflows.

Checkout operations are handled on the backend so that validation and business rules are not dependent on the frontend.

## Database

The backend uses a relational database and SQLAlchemy for database access.

The application contains database models under the `app` package and database configuration through the backend configuration system.

The repository also contains database-related scripts and SQL files, including:

```text
add_products.sql
add_suppliers.sql
init_remote_db.py
run_sql.py
seed_admin.py
```

These files support database initialization, data insertion, SQL execution, and administrative seeding tasks.

## Database Migrations

Database migration files are maintained in:

```text
migrations/
```

Migrations allow database schema changes to be tracked and applied in a controlled manner.

Database changes should be handled through the project's migration workflow rather than manually modifying production database structures.

## Startup Configuration

The backend performs startup configuration validation.

The application uses a lifespan function to validate startup configuration before serving requests.

In development and test environments, database tables can be created automatically through SQLAlchemy metadata.

Production environments should use the configured production database and migration process.

## Environment Configuration

The backend uses environment variables for configuration.

A production environment should use:

```env
APP_ENV=production
```

Environment variables should be configured in the deployment platform rather than committing sensitive values to GitHub.

Typical configuration may include values for:

* Application environment
* Database connection
* Authentication configuration
* CORS configuration
* Rate limiting
* Payment configuration
* Other application settings

The exact environment variable names should match the configuration implemented in `app/core/config.py`.

## CORS Configuration

The Agasaro frontend and backend are deployed separately.

Production frontend:

```text
https://agasaro-frontend.vercel.app
```

Production backend:

```text
https://agasaro-shop.onrender.com
```

Because the applications use different domains, the backend uses FastAPI's `CORSMiddleware` to control which frontend origins can communicate with the API.

The production frontend origin should be allowed by the backend CORS configuration:

```text
https://agasaro-frontend.vercel.app
```

CORS configuration is important for allowing browser-based requests from the production frontend to the backend API.

## Rate Limiting

The backend uses **SlowAPI** for API rate limiting.

Rate limiting is configured through the application infrastructure and an exception handler is registered for requests that exceed the configured limit.

This helps protect API endpoints from excessive request traffic.

## Authentication and Authorization

Authentication and authorization are handled by the backend rather than being trusted solely to the frontend.

Protected operations require appropriate authentication credentials.

The backend is responsible for:

* Validating authentication
* Identifying authenticated users
* Checking authorization
* Protecting restricted operations
* Enforcing server-side access rules

The frontend acts as the client application and sends the required authentication information when accessing protected endpoints.

## Health Check

The backend provides a health-check endpoint:

```text
https://agasaro-shop.onrender.com/healthz
```

A successful response is:

```json
{
  "status": "ok"
}
```

The health endpoint can be used to confirm that the deployed API is running.

## Root Endpoint

The API also provides a root system endpoint:

```text
https://agasaro-shop.onrender.com/
```

The response identifies the API as the Agasaro Backend API and provides the current API version.

## Local Development

### Prerequisites

The following software is required:

* Python 3.12 or a compatible Python version supported by the project
* uv
* Git
* PostgreSQL or access to a configured development database

Check Python:

```bash
python3 --version
```

Check uv:

```bash
uv --version
```

## Creating the Virtual Environment

From the backend project directory:

```bash
cd Agasaro_shop
```

Create the virtual environment:

```bash
uv venv env
```

If the `env` virtual environment already exists, it does not need to be recreated.

Activate it:

```bash
source env/bin/activate
```

## Installing Dependencies

Install the project dependencies using the project's dependency configuration.

If using `requirements.txt`:

```bash
uv pip install -r requirements.txt
```

## Running the Backend Locally

The FastAPI application can be started with Uvicorn.

If the main application is located at `app/main.py`:

```bash
uv run uvicorn app.main:app --reload
```

The local API will normally be available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive API documentation is normally available at:

```text
http://127.0.0.1:8000/docs
```

The alternative ReDoc documentation is normally available at:

```text
http://127.0.0.1:8000/redoc
```

## Testing the API

After starting the backend locally, the health endpoint can be tested with:

```text
http://127.0.0.1:8000/healthz
```

The products endpoint can be tested with:

```text
http://127.0.0.1:8000/products/
```

The production equivalents are:

```text
https://agasaro-shop.onrender.com/healthz
```

and:

```text
https://agasaro-shop.onrender.com/products/
```

## Production Deployment

The Agasaro backend is deployed using Render.

Production backend:

```text
https://agasaro-shop.onrender.com
```

The backend source code is maintained in GitHub.

A typical deployment workflow is:

```text
GitHub
   │
   ▼
Render
   │
   ▼
Agasaro FastAPI API
```

When the configured production branch is updated, Render can build and deploy the updated backend.

## Deployment Environment

The production environment should use:

```text
APP_ENV=production
```

Production environment variables should be configured in Render's Environment settings.

Sensitive values should not be committed to the repository.

## Development Workflow

The recommended development workflow is:

```bash
# Enter the backend project
cd Agasaro_shop

# Activate the virtual environment
source env/bin/activate

# Install dependencies when required
uv pip install -r requirements.txt

# Start the API locally
uv run uvicorn app.main:app --reload
```

After making changes:

```bash
git status
git add .
git commit -m "Describe your changes"
git push
```

Changes pushed to the configured production branch can trigger a new Render deployment.

## Security

Sensitive information should never be committed to GitHub.

Do not commit:

* Database passwords
* Database connection strings containing credentials
* API keys
* JWT secrets
* Authentication secrets
* Payment credentials
* Private credentials
* Production environment files

Use deployment environment variables for sensitive configuration.

The `.gitignore` file should prevent local secret files and generated files from being committed.

## Error Handling

The backend provides HTTP API responses for successful operations and errors.

FastAPI handles request validation and API errors, while application-specific routers handle business and database-related failures.

The frontend can display an error when the API cannot be reached. For example:

```text
Could not load products: Failed to fetch
```

For production troubleshooting, the backend health endpoint and Render deployment logs should be checked first.

## Production Architecture

The Agasaro system uses a separated frontend and backend architecture:

```text
                         User
                          │
                          ▼
              ┌───────────────────────┐
              │   Agasaro Frontend    │
              │       Next.js         │
              │        Vercel         │
              └───────────┬───────────┘
                          │
                          │ HTTPS / REST API
                          ▼
              ┌───────────────────────┐
              │    Agasaro Backend    │
              │       FastAPI         │
              │        Render         │
              └───────────┬───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │      PostgreSQL       │
              │       Database        │
              └───────────────────────┘
```

The frontend provides the user interface while the backend provides API services, authentication, business logic, data validation, and database access.

## Repository Files

Important files and directories include:

| File / Directory | Purpose |
| ---------------- | ------- |
| `app/` | Main FastAPI application package |
| `app/main.py` | FastAPI application entry point |
| `migrations/` | Database migration files |
| `add_products.sql` | Product-related SQL data/setup |
| `add_suppliers.sql` | Supplier-related SQL data/setup |
| `init_remote_db.py` | Remote database initialization support |
| `run_sql.py` | SQL execution utility |
| `seed_admin.py` | Administrative user/data seeding support |
| `generate_momo_credentials.py` | Mobile-money credential generation support |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Files excluded from version control |
| `README.md` | Backend documentation |

## Project Status

The Agasaro Shop Backend is deployed as a production FastAPI application and provides RESTful API services to the Agasaro frontend.

### Production Backend

```text
https://agasaro-shop.onrender.com
```

### Health Check

```text
https://agasaro-shop.onrender.com/healthz
```

### Products API

```text
https://agasaro-shop.onrender.com/products/
```

## Summary

The Agasaro Shop Backend provides the server-side foundation for the Agasaro retail and POS platform.

Built with FastAPI, Python, SQLAlchemy, and a relational database, the backend provides APIs for authentication, users, products, categories, suppliers, customers, sales, sale items, checkout, payments, and receipts.

The backend is separated from the frontend and is responsible for enforcing application logic, authentication, authorization, data validation, and database operations.

The production API is hosted on Render and is consumed by the Agasaro Next.js frontend hosted on Vercel.

## Author

Cynthia Ntirenganya
