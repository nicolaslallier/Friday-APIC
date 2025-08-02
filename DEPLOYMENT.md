# Azure Function App Deployment Guide

This guide explains how to deploy the health check function to your Azure Function App.

## Prerequisites

1. **Azure CLI** installed and authenticated
2. **Azure Functions Core Tools** installed
3. **Python 3.7+** installed
4. **Access to your Azure Function App**: `func-frdyapic-prd-cac-ffgrbhfrfxatbqgy`

## Local Development Setup

1. **Install Azure Functions Core Tools** (if not already installed):
   ```bash
   npm install -g azure-functions-core-tools@4 --unsafe-perm true
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Test locally**:
   ```bash
   func start
   ```

## Deployment Steps

### Option 1: Deploy using Azure CLI

1. **Login to Azure**:
   ```bash
   az login
   ```

2. **Deploy the function app**:
   ```bash
   az functionapp deployment source config-zip \
     --resource-group <your-resource-group> \
     --name func-frdyapic-prd-cac-ffgrbhfrfxatbqgy \
     --src . \
     --build-remote true
   ```

### Option 2: Deploy using Azure Functions Core Tools

1. **Build and deploy**:
   ```bash
   func azure functionapp publish func-frdyapic-prd-cac-ffgrbhfrfxatbqgy
   ```

## Configuration

### Environment Variables

Set these in your Azure Function App Configuration:

- `KEY_VAULT_URL`: `https://kv-frdykvsc-prd-cac.vault.azure.net/`

### Managed Identity Setup

1. **Enable Managed Identity** on your Function App:
   ```bash
   az functionapp identity assign \
     --resource-group <your-resource-group> \
     --name func-frdyapic-prd-cac-ffgrbhfrfxatbqgy
   ```

2. **Grant Key Vault permissions** to the Managed Identity:
   ```bash
   # Get the principal ID
   PRINCIPAL_ID=$(az functionapp identity show \
     --resource-group <your-resource-group> \
     --name func-frdyapic-prd-cac-ffgrbhfrfxatbqgy \
     --query principalId --output tsv)

   # Grant secrets read permission
   az keyvault set-policy \
     --name kv-frdykvsc-prd-cac \
     --secret-permissions get list \
     --object-id $PRINCIPAL_ID

   # Grant keys read permission
   az keyvault set-policy \
     --name kv-frdykvsc-prd-cac \
     --key-permissions get list \
     --object-id $PRINCIPAL_ID
   ```

## Health Check Endpoints

Once deployed, your function app will have these endpoints:

### Basic Health Check
- **URL**: `https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/health`
- **Method**: GET
- **Purpose**: Quick health status with Key Vault read access verification

### Detailed Health Check
- **URL**: `https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/health/detailed`
- **Method**: GET
- **Purpose**: Detailed health status with Key Vault contents listing

## Response Format

### Basic Health Check Response
```json
{
  "timestamp": "2025-08-02T16:09:54.315590+00:00",
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

### HTTP Status Codes
- **200**: Healthy or Degraded (function is working)
- **503**: Unhealthy (function cannot access Key Vault)

## Testing

1. **Test the basic health check**:
   ```bash
   curl https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/health
   ```

2. **Test the detailed health check**:
   ```bash
   curl https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/health/detailed
   ```

## Monitoring

- **Application Insights**: Monitor function execution and Key Vault access
- **Azure Monitor**: Set up alerts for health check failures
- **Log Analytics**: Query function logs for Key Vault access patterns

## Troubleshooting

### Common Issues

1. **403 Forbidden**: Check Managed Identity permissions on Key Vault
2. **404 Not Found**: Verify function app name and deployment
3. **500 Internal Server Error**: Check function app logs in Azure Portal

### Debug Commands

```bash
# Check function app status
az functionapp show \
  --resource-group <your-resource-group> \
  --name func-frdyapic-prd-cac-ffgrbhfrfxatbqgy

# View function app logs
az functionapp logs tail \
  --resource-group <your-resource-group> \
  --name func-frdyapic-prd-cac-ffgrbhfrfxatbqgy
``` 