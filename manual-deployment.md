# Manual Deployment Guide

Since the automated deployment is blocked by IP restrictions, here's how to manually deploy the health check function to your Azure Function App.

## Option 1: Azure Portal Deployment

### Step 1: Access Your Function App
1. Go to the [Azure Portal](https://portal.azure.com)
2. Navigate to your Function App: `func-frdyapic-prd-cac`
3. Go to **Development Tools** → **Advanced Tools (Kudu)**

### Step 2: Upload Files via Kudu
1. In Kudu, go to **Debug Console** → **PowerShell**
2. Navigate to `site/wwwroot/`
3. Upload these files:
   - `function_app.py`
   - `host.json`
   - `requirements.txt`

### Step 3: Set Environment Variable
1. In your Function App, go to **Configuration**
2. Add application setting:
   - **Name**: `KEY_VAULT_URL`
   - **Value**: `https://kv-frdykvsc-prd-cac.vault.azure.net/`
3. Click **Save**

## Option 2: Azure CLI with IP Allowlist

If you want to enable automated deployment, you need to:

### Step 1: Allow Your IP Address
```bash
# Get your current IP
curl ifconfig.me

# Add your IP to the function app's IP restrictions
az functionapp config access-restriction add \
  --resource-group rg-Friday-prd-cac \
  --name func-frdyapic-prd-cac \
  --ip-address YOUR_IP_ADDRESS \
  --rule-name "Allow My IP"
```

### Step 2: Deploy Using Azure CLI
```bash
# Deploy the function app
az functionapp deployment source config-zip \
  --resource-group rg-Friday-prd-cac \
  --name func-frdyapic-prd-cac \
  --src function-app.zip \
  --build-remote true
```

## Option 3: GitHub Actions Deployment

### Step 1: Push to GitHub
1. Create a GitHub repository
2. Push your code to the repository
3. Configure GitHub Actions deployment

### Step 2: Configure Deployment
```bash
az functionapp deployment source config \
  --resource-group rg-Friday-prd-cac \
  --name func-frdyapic-prd-cac \
  --repo-url https://github.com/YOUR_USERNAME/YOUR_REPO.git \
  --branch main \
  --manual-integration
```

## Files to Deploy

Make sure these files are deployed:

1. **`function_app.py`** - Main function app with health check endpoints
2. **`host.json`** - Azure Functions configuration
3. **`requirements.txt`** - Python dependencies

## Environment Variables

Set this environment variable in your Function App:

- **`KEY_VAULT_URL`**: `https://kv-frdykvsc-prd-cac.vault.azure.net/`

## Test the Deployment

Once deployed, test your health check endpoints:

1. **Basic Health Check**:
   ```
   https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/health
   ```

2. **Detailed Health Check**:
   ```
   https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/health/detailed
   ```

## Expected Response

You should see a JSON response like:
```json
{
  "timestamp": "2025-08-02T16:20:00.000000+00:00",
  "function_app": {
    "status": "healthy",
    "name": "func-frdyapic-prd-cac-ffgrbhfrfxatbqgy",
    "region": "canadacentral-01"
  },
  "key_vault": {
    "status": "healthy",
    "url": "https://kv-frdykvsc-prd-cac.vault.azure.net/",
    "secrets_readable": true,
    "keys_readable": true,
    "secrets_count": 1,
    "keys_count": 1,
    "error": null
  },
  "overall_status": "healthy"
}
```

## Troubleshooting

1. **403 Forbidden**: Check IP restrictions on the function app
2. **404 Not Found**: Verify the function app name and deployment
3. **500 Internal Server Error**: Check function app logs in Azure Portal
4. **Key Vault Access Issues**: Ensure Managed Identity is configured with proper permissions 