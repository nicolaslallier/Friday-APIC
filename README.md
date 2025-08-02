# Friday-APIC - Azure Key Vault Operations & Health Check

This project provides Python scripts to interact with Azure Key Vault and includes a health check function for your Azure Function App. The health check verifies that your function can read keys and secrets from the Key Vault at `https://kv-frdykvsc-prd-cac.vault.azure.net/`.

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Azure CLI** installed and authenticated
3. **Proper permissions** to access the Azure Key Vault

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Authenticate with Azure:**
   ```bash
   az login
   ```

3. **Verify access to the Key Vault:**
   ```bash
   az keyvault show --name kv-frdykvsc-prd-cac --resource-group <your-resource-group>
   ```

## Usage

### Option 1: Use the main script (with examples)
```bash
python azure_keyvault_operations.py
```

### Option 2: Use the custom example script
1. Edit `example_usage.py` and customize the values:
   - `SECRET_NAME`: Name for your secret
   - `SECRET_VALUE`: The actual secret value
   - `KEY_NAME`: Name for your key
   - `KEY_TYPE`: Type of key (RSA, EC, oct)
   - `KEY_SIZE`: Size of the key in bits

2. Run the script:
   ```bash
   python example_usage.py
   ```

### Option 3: Use the class directly in your code
```python
from azure_keyvault_operations import AzureKeyVaultManager

# Initialize
kv_manager = AzureKeyVaultManager("https://kv-frdykvsc-prd-cac.vault.azure.net/")

# Write a secret
secret_info = kv_manager.write_secret(
    secret_name="my-secret",
    secret_value="my-secret-value",
    tags={"environment": "production"}
)

# Create a key
key_info = kv_manager.write_key(
    key_name="my-key",
    key_type="RSA",
    key_size=2048
)
```

## Authentication Methods

The script supports multiple authentication methods:

1. **Azure CLI** (default) - Run `az login` first
2. **Managed Identity** - If running on Azure resources
3. **Service Principal** - Provide tenant_id, client_id, and client_secret

For service principal authentication, modify the script:
```python
kv_manager = AzureKeyVaultManager(
    vault_url="https://kv-frdykvsc-prd-cac.vault.azure.net/",
    tenant_id="your-tenant-id",
    client_id="your-client-id",
    client_secret="your-client-secret"
)
```

## Features

- ✅ Write secrets to Key Vault
- ✅ Create cryptographic keys (RSA, EC, oct)
- ✅ Add tags and metadata
- ✅ List existing secrets and keys
- ✅ Error handling and logging
- ✅ Multiple authentication methods

## Troubleshooting

### Common Issues:

1. **Authentication Error**: Run `az login` or check your service principal credentials
2. **Permission Denied**: Ensure your account has Key Vault permissions (Key Vault Contributor or similar)
3. **Key Vault Not Found**: Verify the Key Vault URL and your subscription access
4. **Network Issues**: Check if you're behind a corporate firewall or VPN

### Required Permissions:
- `Microsoft.KeyVault/vaults/secrets/write`
- `Microsoft.KeyVault/vaults/keys/create`

## Security Notes

- Never commit actual secret values to version control
- Use environment variables for sensitive configuration
- Consider using Azure Key Vault's built-in rotation features
- Implement proper access controls and monitoring

## Health Check Function

The project includes a health check function for your Azure Function App (`func-frdyapic-prd-cac-ffgrbhfrfxatbqgy`) that verifies:

- ✅ Function App is running
- ✅ Can connect to Azure Key Vault
- ✅ Can read secrets from Key Vault
- ✅ Can read keys from Key Vault

### Health Check Endpoints

- **Basic Health Check**: `/api/health` - Quick status with read access verification
- **Detailed Health Check**: `/api/health/detailed` - Detailed status with Key Vault contents

### Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Files

- `azure_keyvault_operations.py` - Main library with AzureKeyVaultManager class
- `example_usage.py` - Example script for custom usage
- `function_app.py` - Azure Function App with health check endpoints
- `test_health_check.py` - Test script for health check logic
- `requirements.txt` - Python dependencies
- `host.json` - Azure Functions host configuration
- `local.settings.json` - Local development settings
- `DEPLOYMENT.md` - Deployment guide
- `README.md` - This documentation