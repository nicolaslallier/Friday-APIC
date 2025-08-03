# Friday-APIC Azure Function App

A Python-based Azure Function App with multiple functions. Each function is organized in its own folder for better maintainability.

## Functions

### 1. Health Check (`/health`)
- **Route**: `/health`
- **Method**: GET
- **Description**: Returns the health status of the function app
- **Response**: JSON with status, timestamp, service info, and health checks





## Prerequisites

- Python 3.8 or higher
- Azure Functions Core Tools
- Azure CLI (for deployment)


## Local Development Setup

1. **Install Azure Functions Core Tools**:
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment**:
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the function app locally**:
   ```bash
   func start
   ```

## Testing

The project includes comprehensive testing with unit, functional, and regression tests.

### Running Tests

**Run all tests:**
```bash
python run_tests.py
```

**Run specific test types:**
```bash
# Unit tests only
python run_tests.py --type unit

# Functional tests only
python run_tests.py --type functional

# Regression tests only
python run_tests.py --type regression
```

**Run tests with coverage:**
```bash
python run_tests.py --coverage
```

**Run tests with HTML coverage report:**
```bash
python run_tests.py --coverage --html
```

**Run tests with verbose output:**
```bash
python run_tests.py --verbose
```

### Test Types

1. **Unit Tests** (`tests/unit/`)
   - Test individual function components
   - Mock external dependencies
   - Fast execution
   - High code coverage

2. **Functional Tests** (`tests/functional/`)
   - Test API contracts and integration
   - Verify end-to-end functionality
   - Test performance characteristics
   - Validate business logic

3. **Regression Tests** (`tests/regression/`)
   - Ensure existing functionality continues to work
   - Test baseline expectations
   - Verify response format consistency
   - Prevent breaking changes

### Test Coverage

The project aims for 80% code coverage. Coverage reports are generated in HTML format and can be viewed in the `htmlcov/` directory after running tests with coverage.

## Testing the Functions

Once the function app is running locally, you can test the endpoints:

### Health Check
```bash
curl http://localhost:7071/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000000Z",
  "service": "Friday-APIC",
  "version": "1.0.0",
  "environment": "Development",
  "checks": {
    "function_app": "healthy",
    "runtime": "python",
    "timestamp_check": "healthy"
  }
}
```





## Deployment to Azure

1. **Login to Azure**:
   ```bash
   az login
   ```

2. **Create a resource group** (if not exists):
   ```bash
   az group create --name myResourceGroup --location eastus
   ```

3. **Create a storage account**:
   ```bash
   az storage account create --name mystorageaccount --location eastus --resource-group myResourceGroup --sku Standard_LRS
   ```

4. **Create a function app**:
   ```bash
   az functionapp create --resource-group myResourceGroup --consumption-plan-location eastus --runtime python --runtime-version 3.9 --functions-version 4 --name my-function-app --storage-account mystorageaccount --os-type linux
   ```

5. **Deploy the function app**:
   ```bash
   func azure functionapp publish my-function-app
   ```

## Project Structure

```
Friday-APIC/
├── health_check/           # Health check function
│   ├── function.json      # Function configuration
│   └── __init__.py        # Function implementation
├── shared/                 # Shared utilities
│   ├── __init__.py        # Package marker
│   └── file_utils.py      # File utilities
├── test_simple/           # Simple test function
│   ├── function.json      # Function configuration
│   └── __init__.py        # Function implementation
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── functional/       # Functional tests
│   ├── regression/       # Regression tests
│   └── conftest.py       # Test configuration and fixtures
├── requirements.txt       # Python dependencies
├── host.json             # Azure Functions host configuration
├── local.settings.json   # Local development settings
├── pytest.ini           # Pytest configuration
├── run_tests.py         # Test runner script
├── deploy-zip.ps1       # PowerShell deployment script
├── .gitignore           # Git ignore file
└── README.md            # This file
```

## Adding New Functions

To add new functions to the app, create a new folder with the function name and add the required files:

1. **Create a new folder** with your function name (e.g., `my_function/`)
2. **Add `function.json`** with the function configuration:

```json
{
  "scriptFile": "__init__.py",
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "methods": ["get"],
      "route": "my-route"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
```

3. **Add `__init__.py`** with your function implementation:

```python
import azure.functions as func
import logging
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('My function processed a request.')
    
    # Your function logic here
    
    return func.HttpResponse(
        json.dumps({"message": "Hello from my function!"}),
        status_code=200,
        mimetype="application/json"
    )
```

## Environment Variables

The following environment variables can be configured:

- `WEBSITE_SITE_NAME`: The name of your function app (defaults to "Friday-APIC")
- `AZURE_FUNCTIONS_ENVIRONMENT`: The environment (Development, Production, etc.)


## Contributing

1. Create a new branch for your feature
2. Add your new functions to `function_app.py`
3. Update this README if needed
4. Submit a pull request

## License

This project is licensed under the MIT License. 