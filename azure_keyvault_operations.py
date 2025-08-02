#!/usr/bin/env python3
"""
Azure Key Vault Operations Script
This script provides functions to write keys and secrets to Azure Key Vault.
"""

import os
from typing import Optional
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.keyvault.secrets import SecretClient
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient
from azure.core.exceptions import AzureError


class AzureKeyVaultManager:
    def __init__(self, vault_url: str, tenant_id: Optional[str] = None, 
                 client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """
        Initialize the Azure Key Vault Manager.
        
        Args:
            vault_url: The URL of the Azure Key Vault
            tenant_id: Azure AD tenant ID (optional, for service principal auth)
            client_id: Azure AD client ID (optional, for service principal auth)
            client_secret: Azure AD client secret (optional, for service principal auth)
        """
        self.vault_url = vault_url
        
        # Initialize credentials
        if all([tenant_id, client_id, client_secret]):
            # Use service principal authentication
            self.credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
        else:
            # Use default credential (managed identity, Azure CLI, etc.)
            self.credential = DefaultAzureCredential()
        
        # Initialize clients
        self.secret_client = SecretClient(vault_url=vault_url, credential=self.credential)
        self.key_client = KeyClient(vault_url=vault_url, credential=self.credential)
    
    def write_secret(self, secret_name: str, secret_value: str, 
                    content_type: Optional[str] = None, tags: Optional[dict] = None) -> dict:
        """
        Write a secret to the Key Vault.
        
        Args:
            secret_name: Name of the secret
            secret_value: Value of the secret
            content_type: Content type of the secret (optional)
            tags: Tags to associate with the secret (optional)
            
        Returns:
            dict: Information about the created secret
        """
        try:
            secret = self.secret_client.set_secret(
                secret_name, 
                secret_value,
                content_type=content_type,
                tags=tags
            )
            print(f"✅ Secret '{secret_name}' created successfully")
            return {
                "name": secret.name,
                "version": secret.properties.version,
                "created_on": secret.properties.created_on,
                "updated_on": secret.properties.updated_on
            }
        except AzureError as e:
            print(f"❌ Error creating secret '{secret_name}': {e}")
            raise
    
    def write_key(self, key_name: str, key_type: str = "RSA", 
                  key_size: int = 2048, tags: Optional[dict] = None) -> dict:
        """
        Create a key in the Key Vault.
        
        Args:
            key_name: Name of the key
            key_type: Type of key (RSA, EC, etc.)
            key_size: Size of the key in bits
            tags: Tags to associate with the key (optional)
            
        Returns:
            dict: Information about the created key
        """
        try:
            key = self.key_client.create_key(
                key_name,
                key_type,
                size=key_size,
                tags=tags
            )
            print(f"✅ Key '{key_name}' created successfully")
            return {
                "name": key.name,
                "version": key.properties.version,
                "key_type": key.key_type,
                "created_on": key.properties.created_on,
                "updated_on": key.properties.updated_on
            }
        except AzureError as e:
            print(f"❌ Error creating key '{key_name}': {e}")
            raise
    
    def list_secrets(self) -> list:
        """List all secrets in the Key Vault."""
        try:
            secrets = list(self.secret_client.list_properties_of_secrets())
            return [{"name": secret.name, "enabled": secret.enabled} for secret in secrets]
        except AzureError as e:
            print(f"❌ Error listing secrets: {e}")
            raise
    
    def list_keys(self) -> list:
        """List all keys in the Key Vault."""
        try:
            keys = list(self.key_client.list_properties_of_keys())
            return [{"name": key.name, "enabled": key.enabled} for key in keys]
        except AzureError as e:
            print(f"❌ Error listing keys: {e}")
            raise


def main():
    """Example usage of the Azure Key Vault Manager."""
    
    # Your Key Vault URL
    VAULT_URL = "https://kv-frdykvsc-prd-cac.vault.azure.net/"
    
    # Optional: Service principal credentials (if not using managed identity or Azure CLI)
    # TENANT_ID = "your-tenant-id"
    # CLIENT_ID = "your-client-id"
    # CLIENT_SECRET = "your-client-secret"
    
    try:
        # Initialize the Key Vault manager
        kv_manager = AzureKeyVaultManager(VAULT_URL)
        
        # Example: Write a secret
        print("🔐 Writing secret to Key Vault...")
        secret_info = kv_manager.write_secret(
            secret_name="my-api-key",
            secret_value="your-secret-value-here",
            content_type="text/plain",
            tags={"environment": "production", "purpose": "api-authentication"}
        )
        print(f"Secret info: {secret_info}")
        
        # Example: Create a key
        print("\n🔑 Creating key in Key Vault...")
        key_info = kv_manager.write_key(
            key_name="my-encryption-key",
            key_type="RSA",
            key_size=2048,
            tags={"environment": "production", "purpose": "data-encryption"}
        )
        print(f"Key info: {key_info}")
        
        # List existing secrets and keys
        print("\n📋 Listing existing secrets...")
        secrets = kv_manager.list_secrets()
        for secret in secrets:
            print(f"  - {secret['name']} (enabled: {secret['enabled']})")
        
        print("\n📋 Listing existing keys...")
        keys = kv_manager.list_keys()
        for key in keys:
            print(f"  - {key['name']} (enabled: {key['enabled']})")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have proper authentication set up:")
        print("  1. Azure CLI: Run 'az login'")
        print("  2. Managed Identity: Ensure your environment supports it")
        print("  3. Service Principal: Set environment variables or use the constructor parameters")


if __name__ == "__main__":
    main() 