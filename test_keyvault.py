#!/usr/bin/env python3
"""
Test script for Azure Key Vault connectivity and operations
"""

from azure_keyvault_operations import AzureKeyVaultManager
import time

def test_keyvault_connection():
    """Test the connection to Azure Key Vault and basic operations."""
    
    # Your Key Vault URL
    VAULT_URL = "https://kv-frdykvsc-prd-cac.vault.azure.net/"
    
    print("🔍 Testing Azure Key Vault Connection...")
    print(f"Key Vault URL: {VAULT_URL}")
    print("=" * 50)
    
    try:
        # Initialize the Key Vault manager
        print("1. Initializing Azure Key Vault Manager...")
        kv_manager = AzureKeyVaultManager(VAULT_URL)
        print("✅ Successfully initialized Key Vault Manager")
        
        # Test listing existing secrets
        print("\n2. Testing list secrets operation...")
        try:
            secrets = kv_manager.list_secrets()
            print(f"✅ Successfully listed {len(secrets)} existing secrets")
            for secret in secrets[:5]:  # Show first 5 secrets
                print(f"   - {secret['name']} (enabled: {secret['enabled']})")
            if len(secrets) > 5:
                print(f"   ... and {len(secrets) - 5} more secrets")
        except Exception as e:
            print(f"⚠️  Warning: Could not list secrets: {e}")
        
        # Test listing existing keys
        print("\n3. Testing list keys operation...")
        try:
            keys = kv_manager.list_keys()
            print(f"✅ Successfully listed {len(keys)} existing keys")
            for key in keys[:5]:  # Show first 5 keys
                print(f"   - {key['name']} (enabled: {key['enabled']})")
            if len(keys) > 5:
                print(f"   ... and {len(keys) - 5} more keys")
        except Exception as e:
            print(f"⚠️  Warning: Could not list keys: {e}")
        
        # Test writing a secret (with timestamp to avoid conflicts)
        print("\n4. Testing write secret operation...")
        timestamp = int(time.time())
        test_secret_name = f"test-secret-{timestamp}"
        test_secret_value = f"test-value-{timestamp}"
        
        try:
            secret_info = kv_manager.write_secret(
                secret_name=test_secret_name,
                secret_value=test_secret_value,
                content_type="text/plain",
                tags={
                    "environment": "test",
                    "purpose": "connection-test",
                    "created_by": "test-script",
                    "timestamp": str(timestamp)
                }
            )
            print(f"✅ Successfully created test secret: {secret_info['name']}")
            print(f"   Version: {secret_info['version']}")
            print(f"   Created: {secret_info['created_on']}")
        except Exception as e:
            print(f"❌ Error creating test secret: {e}")
            return False
        
        # Test creating a key (with timestamp to avoid conflicts)
        print("\n5. Testing create key operation...")
        test_key_name = f"test-key-{timestamp}"
        
        try:
            key_info = kv_manager.write_key(
                key_name=test_key_name,
                key_type="RSA",
                key_size=2048,
                tags={
                    "environment": "test",
                    "purpose": "connection-test",
                    "created_by": "test-script",
                    "timestamp": str(timestamp)
                }
            )
            print(f"✅ Successfully created test key: {key_info['name']}")
            print(f"   Version: {key_info['version']}")
            print(f"   Type: {key_info['key_type']}")
            print(f"   Created: {key_info['created_on']}")
        except Exception as e:
            print(f"❌ Error creating test key: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Your Azure Key Vault is working correctly.")
        print(f"📝 Test secret created: {test_secret_name}")
        print(f"🔑 Test key created: {test_key_name}")
        print("\n💡 You can now use the Key Vault for your actual secrets and keys.")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Connection test failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("  1. Make sure you're authenticated: az login")
        print("  2. Check if you have permissions to access this Key Vault")
        print("  3. Verify the Key Vault URL is correct")
        print("  4. Ensure your subscription has access to this Key Vault")
        return False

if __name__ == "__main__":
    success = test_keyvault_connection()
    if not success:
        exit(1) 