import pytest
import json
import sys
import os
from unittest.mock import patch, Mock
from datetime import datetime

# Import the health check function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'health_check'))
from __init__ import main
import azure.functions as func


class TestHealthCheckUnit:
    """Unit tests for the health check function."""
    
    @pytest.mark.unit
    def test_health_check_success(self, mock_http_request, mock_environment_variables):
        """Test successful health check response."""
        # Arrange
        request = mock_http_request(method="GET", url="/health")
        
        # Act
        response = main(request)
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        response_data = json.loads(response.get_body().decode())
        assert response_data["status"] == "healthy"
        assert response_data["service"] == "Friday-APIC-Test"
        assert response_data["version"] == "1.0.0"
        assert response_data["environment"] == "Test"
        assert "timestamp" in response_data
        assert "checks" in response_data
        assert response_data["checks"]["function_app"] == "healthy"
        assert response_data["checks"]["runtime"] == "python"
        assert response_data["checks"]["timestamp_check"] == "healthy"
    
    @pytest.mark.unit
    def test_health_check_timestamp_format(self, mock_http_request, mock_environment_variables):
        """Test that timestamp is in correct ISO format."""
        # Arrange
        request = mock_http_request(method="GET", url="/health")
        
        # Act
        response = main(request)
        
        # Assert
        response_data = json.loads(response.get_body().decode())
        timestamp = response_data["timestamp"]
        
        # Check if timestamp is valid ISO format ending with Z
        assert timestamp.endswith("Z")
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    
    @pytest.mark.unit
    def test_health_check_environment_variables(self, mock_http_request):
        """Test health check with different environment variables."""
        # Arrange
        request = mock_http_request(method="GET", url="/health")
        
        with patch.dict(os.environ, {
            'WEBSITE_SITE_NAME': 'Custom-App-Name',
            'AZURE_FUNCTIONS_ENVIRONMENT': 'Production'
        }):
            # Act
            response = main(request)
            
            # Assert
            response_data = json.loads(response.get_body().decode())
            assert response_data["service"] == "Custom-App-Name"
            assert response_data["environment"] == "Production"
    
    @pytest.mark.unit
    def test_health_check_missing_environment_variables(self, mock_http_request):
        """Test health check with missing environment variables."""
        # Arrange
        request = mock_http_request(method="GET", url="/health")
        
        with patch.dict(os.environ, {}, clear=True):
            # Act
            response = main(request)
            
            # Assert
            response_data = json.loads(response.get_body().decode())
            assert response_data["service"] == "Friday-APIC"  # Default value
            assert response_data["environment"] == "Development"  # Default value
    
    @pytest.mark.unit
    def test_health_check_error_handling(self, mock_http_request, mock_environment_variables):
        """Test health check error handling."""
        # Arrange
        request = mock_http_request(method="GET", url="/health")
        
        # Mock datetime to raise an exception
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.side_effect = Exception("Test error")
            
            # Act
            response = main(request)
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.get_body().decode())
            assert response_data["status"] == "unhealthy"
            assert "error" in response_data
            assert "Test error" in response_data["error"]
    
    @pytest.mark.unit
    def test_health_check_response_structure(self, mock_http_request, mock_environment_variables):
        """Test that health check response has the correct structure."""
        # Arrange
        request = mock_http_request(method="GET", url="/health")
        
        # Act
        response = main(request)
        
        # Assert
        response_data = json.loads(response.get_body().decode())
        
        # Check required fields
        required_fields = ["status", "timestamp", "service", "version", "environment", "checks"]
        for field in required_fields:
            assert field in response_data
        
        # Check checks structure
        required_checks = ["function_app", "runtime", "timestamp_check"]
        for check in required_checks:
            assert check in response_data["checks"]
            assert response_data["checks"][check] == "healthy" 