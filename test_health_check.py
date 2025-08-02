#!/usr/bin/env python3
"""
Test script for the health check function
"""

import os
import json
from datetime import datetime
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.keyvault.keys import KeyClient
from azure.core.exceptions import AzureError

def test_health_check_logic():
    """Test the health check logic without the Azure Functions framework."""
    
    print("🔍 Testing Health Check Logic...")
    print("=" * 50)
    
    # Initialize response structure (same as in function)
    health_status = {
        "timestamp": datetime.utcnow().isoformat(),
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
        print(f"Testing Key Vault: {key_vault_url}")
        
        # Initialize Azure credentials
        credential = DefaultAzureCredential()
        print("✅ Azure credentials initialized")
        
        # Test Key Vault connection and read operations
        try:
            # Test secrets client
            print("\n1. Testing secrets read access...")
            secret_client = SecretClient(vault_url=key_vault_url, credential=credential)
            
            # Try to list secrets (this tests read access)
            secrets = list(secret_client.list_properties_of_secrets())
            health_status["key_vault"]["secrets_readable"] = True
            health_status["key_vault"]["secrets_count"] = len(secrets)
            
            print(f"✅ Successfully read {len(secrets)} secrets from Key Vault")
            
        except AzureError as e:
            health_status["key_vault"]["secrets_readable"] = False
            health_status["key_vault"]["error"] = f"Secrets read error: {str(e)}"
            print(f"❌ Failed to read secrets from Key Vault: {e}")
        
        try:
            # Test keys client
            print("\n2. Testing keys read access...")
            key_client = KeyClient(vault_url=key_vault_url, credential=credential)
            
            # Try to list keys (this tests read access)
            keys = list(key_client.list_properties_of_keys())
            health_status["key_vault"]["keys_readable"] = True
            health_status["key_vault"]["keys_count"] = len(keys)
            
            print(f"✅ Successfully read {len(keys)} keys from Key Vault")
            
        except AzureError as e:
            health_status["key_vault"]["keys_readable"] = False
            if health_status["key_vault"]["error"]:
                health_status["key_vault"]["error"] += f"; Keys read error: {str(e)}"
            else:
                health_status["key_vault"]["error"] = f"Keys read error: {str(e)}"
            print(f"❌ Failed to read keys from Key Vault: {e}")
        
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
        print(f"❌ Failed to connect to Key Vault: {e}")
    
    # Determine overall status
    if health_status["key_vault"]["status"] == "healthy":
        health_status["overall_status"] = "healthy"
    elif health_status["key_vault"]["status"] == "degraded":
        health_status["overall_status"] = "degraded"
    else:
        health_status["overall_status"] = "unhealthy"
    
    # Display results
    print("\n" + "=" * 50)
    print("📊 Health Check Results:")
    print(json.dumps(health_status, indent=2))
    
    # Determine HTTP status code
    if health_status["overall_status"] == "healthy":
        status_code = 200
        print(f"\n✅ Overall Status: {health_status['overall_status']} (HTTP {status_code})")
    elif health_status["overall_status"] == "degraded":
        status_code = 200
        print(f"\n⚠️  Overall Status: {health_status['overall_status']} (HTTP {status_code})")
    else:
        status_code = 503
        print(f"\n❌ Overall Status: {health_status['overall_status']} (HTTP {status_code})")
    
    return health_status

if __name__ == "__main__":
    test_health_check_logic() 