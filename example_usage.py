#!/usr/bin/env python3
"""
Example usage of Azure Key Vault operations
Customize this script with your specific key and secret values.
"""

from azure_keyvault_operations import AzureKeyVaultManager

def write_custom_secret_and_key():
    """Write a custom secret and key to your Azure Key Vault."""
    
    # Your Key Vault URL
    VAULT_URL = "https://kv-frdykvsc-prd-cac.vault.azure.net/"
    
    # Initialize the Key Vault manager
    kv_manager = AzureKeyVaultManager(VAULT_URL)
    
    # Customize these values for your specific use case
    SECRET_NAME = "my-custom-secret"
    SECRET_VALUE = "your-actual-secret-value-here"
    
    KEY_NAME = "my-custom-key"
    KEY_TYPE = "RSA"  # Options: RSA, EC, oct
    KEY_SIZE = 2048   # For RSA keys: 2048, 3072, 4096
    
    try:
        # Write your custom secret
        print(f"🔐 Writing secret '{SECRET_NAME}' to Key Vault...")
        secret_info = kv_manager.write_secret(
            secret_name=SECRET_NAME,
            secret_value=SECRET_VALUE,
            content_type="text/plain",
            tags={
                "environment": "production",
                "purpose": "custom-secret",
                "created_by": "script"
            }
        )
        print(f"✅ Secret created: {secret_info}")
        
        # Create your custom key
        print(f"\n🔑 Creating key '{KEY_NAME}' in Key Vault...")
        key_info = kv_manager.write_key(
            key_name=KEY_NAME,
            key_type=KEY_TYPE,
            key_size=KEY_SIZE,
            tags={
                "environment": "production",
                "purpose": "custom-key",
                "created_by": "script"
            }
        )
        print(f"✅ Key created: {key_info}")
        
        print("\n🎉 Successfully wrote both secret and key to Azure Key Vault!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Troubleshooting tips:")
        print("  1. Make sure you're authenticated to Azure (run 'az login')")
        print("  2. Ensure you have permissions to write to the Key Vault")
        print("  3. Check that the Key Vault URL is correct")
        print("  4. Verify your Azure subscription has access to this Key Vault")

if __name__ == "__main__":
    write_custom_secret_and_key() 