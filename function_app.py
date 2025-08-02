import azure.functions as func
import logging
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.keyvault.keys import KeyClient
from azure.core.exceptions import AzureError

app = func.FunctionApp()

@app.function_name(name="health-check")
@app.route(route="health")
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint that verifies:
    1. Function App is running
    2. Can connect to Azure Key Vault
    3. Can read secrets from Key Vault
    4. Can read keys from Key Vault
    """
    logging.info('Health check function triggered.')
    
    # Initialize response structure
    health_status = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "function_app": {
            "status": "healthy",
            "name": "func-frdyapic-prd-cac-ffgrbhfrfxatbqgy",
            "region": "canadacentral-01"
        },
        "key_vault": {
            "status": "unknown",
            "url": "https://kv-frdykvsc-prd-cac.vault.azure.net/",
            "secrets_readable": False,
            "keys_readable": False,
            "error": None
        },
        "overall_status": "unknown"
    }
    
    try:
        # Get Key Vault URL from environment or use default
        key_vault_url = os.getenv('KEY_VAULT_URL', 'https://kv-frdykvsc-prd-cac.vault.azure.net/')
        
        # Initialize Azure credentials
        credential = DefaultAzureCredential()
        
        # Test Key Vault connection and read operations
        try:
            # Test secrets client
            secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
            
            # Try to list secrets (this tests read access)
            secrets = list(secret_client.list_properties_of_secrets())
            health_status["key_vault"]["secrets_readable"] = True
            health_status["key_vault"]["secrets_count"] = len(secrets)
            
            logging.info(f"Successfully read {len(secrets)} secrets from Key Vault")
            
        except AzureError as e:
            health_status["key_vault"]["secrets_readable"] = False
            health_status["key_vault"]["error"] = f"Secrets read error: {str(e)}"
            logging.error(f"Failed to read secrets from Key Vault: {e}")
        
        try:
            # Test keys client
            key_client = KeyClient(vault_url=key_vault_url, credential=credential)
            
            # Try to list keys (this tests read access)
            keys = list(key_client.list_properties_of_keys())
            health_status["key_vault"]["keys_readable"] = True
            health_status["key_vault"]["keys_count"] = len(keys)
            
            logging.info(f"Successfully read {len(keys)} keys from Key Vault")
            
        except AzureError as e:
            health_status["key_vault"]["keys_readable"] = False
            if health_status["key_vault"]["error"]:
                health_status["key_vault"]["error"] += f"; Keys read error: {str(e)}"
            else:
                health_status["key_vault"]["error"] = f"Keys read error: {str(e)}"
            logging.error(f"Failed to read keys from Key Vault: {e}")
        
        # Determine Key Vault overall status
        if health_status["key_vault"]["secrets_readable"] and health_status["key_vault"]["keys_readable"]:
            health_status["key_vault"]["status"] = "healthy"
        elif health_status["key_vault"]["secrets_readable"] or health_status["key_vault"]["keys_readable"]:
            health_status["key_vault"]["status"] = "degraded"
        else:
            health_status["key_vault"]["status"] = "unhealthy"
            
    except Exception as e:
        health_status["key_vault"]["status"] = "unhealthy"
        health_status["key_vault"]["error"] = f"Connection error: {str(e)}"
        logging.error(f"Failed to connect to Key Vault: {e}")
    
    # Determine overall status
    if health_status["key_vault"]["status"] == "healthy":
        health_status["overall_status"] = "healthy"
    elif health_status["key_vault"]["status"] == "degraded":
        health_status["overall_status"] = "degraded"
    else:
        health_status["overall_status"] = "unhealthy"
    
    # Set HTTP status code based on overall health
    if health_status["overall_status"] == "healthy":
        status_code = 200
    elif health_status["overall_status"] == "degraded":
        status_code = 200  # Still return 200 for degraded, but indicate in response
    else:
        status_code = 503  # Service Unavailable for unhealthy
    
    # Add response headers
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Health-Status": health_status["overall_status"]
    }
    
    return func.HttpResponse(
        json.dumps(health_status, indent=2),
        status_code=status_code,
        headers=headers
    )

@app.function_name(name="health-check-detailed")
@app.route(route="health/detailed")
def health_check_detailed(req: func.HttpRequest) -> func.HttpResponse:
    """
    Detailed health check endpoint that provides more information about Key Vault contents
    """
    logging.info('Detailed health check function triggered.')
    
    # Initialize response structure
    health_status = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "function_app": {
            "status": "healthy",
            "name": "func-frdyapic-prd-cac-ffgrbhfrfxatbqgy",
            "region": "canadacentral-01"
        },
        "key_vault": {
            "status": "unknown",
            "url": "https://kv-frdykvsc-prd-cac.vault.azure.net/",
            "secrets": [],
            "keys": [],
            "error": None
        },
        "overall_status": "unknown"
    }
    
    try:
        # Get Key Vault URL from environment or use default
        key_vault_url = os.getenv('KEY_VAULT_URL', 'https://kv-frdykvsc-prd-cac.vault.azure.net/')
        
        # Initialize Azure credentials
        credential = DefaultAzureCredential()
        
        # Test secrets client
        try:
            secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
            secrets = list(secret_client.list_properties_of_secrets())
            
            # Get detailed info about secrets (names and enabled status only)
            for secret in secrets:
                health_status["key_vault"]["secrets"].append({
                    "name": secret.name,
                    "enabled": secret.enabled,
                    "created_on": secret.created_on.isoformat() if secret.created_on else None,
                    "updated_on": secret.updated_on.isoformat() if secret.updated_on else None
                })
            
            logging.info(f"Successfully read {len(secrets)} secrets from Key Vault")
            
        except AzureError as e:
            health_status["key_vault"]["error"] = f"Secrets read error: {str(e)}"
            logging.error(f"Failed to read secrets from Key Vault: {e}")
        
        # Test keys client
        try:
            key_client = KeyClient(vault_url=key_vault_url, credential=credential)
            keys = list(key_client.list_properties_of_keys())
            
            # Get detailed info about keys (names and enabled status only)
            for key in keys:
                health_status["key_vault"]["keys"].append({
                    "name": key.name,
                    "enabled": key.enabled,
                    "key_type": str(key.key_type) if key.key_type else None,
                    "created_on": key.created_on.isoformat() if key.created_on else None,
                    "updated_on": key.updated_on.isoformat() if key.updated_on else None
                })
            
            logging.info(f"Successfully read {len(keys)} keys from Key Vault")
            
        except AzureError as e:
            if health_status["key_vault"]["error"]:
                health_status["key_vault"]["error"] += f"; Keys read error: {str(e)}"
            else:
                health_status["key_vault"]["error"] = f"Keys read error: {str(e)}"
            logging.error(f"Failed to read keys from Key Vault: {e}")
        
        # Determine Key Vault overall status
        if not health_status["key_vault"]["error"]:
            health_status["key_vault"]["status"] = "healthy"
        else:
            health_status["key_vault"]["status"] = "unhealthy"
            
    except Exception as e:
        health_status["key_vault"]["status"] = "unhealthy"
        health_status["key_vault"]["error"] = f"Connection error: {str(e)}"
        logging.error(f"Failed to connect to Key Vault: {e}")
    
    # Determine overall status
    health_status["overall_status"] = health_status["key_vault"]["status"]
    
    # Set HTTP status code
    status_code = 200 if health_status["overall_status"] == "healthy" else 503
    
    # Add response headers
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "X-Health-Status": health_status["overall_status"]
    }
    
    return func.HttpResponse(
        json.dumps(health_status, indent=2),
        status_code=status_code,
        headers=headers
    ) 