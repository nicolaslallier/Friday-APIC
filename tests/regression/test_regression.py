import pytest
import json
import sys
import os
from unittest.mock import patch, Mock
from datetime import datetime

# Import the functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'health_check'))
from health_check.__init__ import main as health_check_main

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hello_world'))
from hello_world.__init__ import main as hello_world_main

import azure.functions as func


class TestRegression:
    """Regression tests to ensure existing functionality continues to work."""
    
    @pytest.mark.regression
    def test_health_check_baseline_functionality(self, mock_http_request, mock_environment_variables):
        """Regression test: Health check should always return healthy status in normal conditions."""
        # Arrange
        request = mock_http_request(method="GET", url="/health")
        
        # Act
        response = health_check_main(request)
        
        # Assert - Baseline expectations that should never change
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        response_data = json.loads(response.get_body().decode())
        
        # These are core requirements that should never break
        assert response_data["status"] == "healthy"
        assert response_data["service"] == "Friday-APIC-Test"
        assert response_data["version"] == "1.0.0"
        assert response_data["environment"] == "Test"
        
        # Check structure remains the same
        assert "checks" in response_data
        assert "function_app" in response_data["checks"]
        assert "runtime" in response_data["checks"]
        assert "timestamp_check" in response_data["checks"]
        
        # All checks should be healthy
        for check_name, check_status in response_data["checks"].items():
            assert check_status == "healthy"
    
    @pytest.mark.regression
    def test_hello_world_baseline_functionality(self, mock_http_request):
        """Regression test: Hello world should always return basic greeting."""
        # Arrange
        request = mock_http_request(method="GET", url="/hello")
        
        # Act
        response = hello_world_main(request)
        
        # Assert - Baseline expectations that should never change
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        response_data = json.loads(response.get_body().decode())
        
        # Core functionality that should never break
        assert response_data["message"] == "Hello, World!"
        assert response_data["method"] == "GET"
        assert response_data["status"] == "success"
        assert "timestamp" in response_data
    
    @pytest.mark.regression
    def test_hello_world_personalization_regression(self, mock_http_request):
        """Regression test: Hello world personalization should always work."""
        # Arrange
        test_cases = [
            {"name": "John", "expected": "Hello, John!"},
            {"name": "Jane", "expected": "Hello, Jane!"},
            {"name": "Test User", "expected": "Hello, Test User!"},
            {"name": "123", "expected": "Hello, 123!"},
        ]
        
        for test_case in test_cases:
            request = mock_http_request(
                method="POST", 
                url="/hello", 
                body={"name": test_case["name"]},
                headers={"Content-Type": "application/json"}
            )
            
            # Act
            response = hello_world_main(request)
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.get_body().decode())
            assert response_data["message"] == test_case["expected"]
            assert response_data["received_name"] == test_case["name"]
            assert response_data["method"] == "POST"
            assert response_data["status"] == "success"
    
    @pytest.mark.regression
    def test_error_handling_regression(self, mock_http_request, mock_environment_variables):
        """Regression test: Error handling should always work consistently."""
        # Test health check error handling
        request = mock_http_request(method="GET", url="/health")
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.side_effect = Exception("Regression test error")
            
            response = health_check_main(request)
            
            assert response.status_code == 500
            response_data = json.loads(response.get_body().decode())
            assert response_data["status"] == "unhealthy"
            assert "error" in response_data
            assert "timestamp" in response_data
            assert "service" in response_data
        
        # Test hello world error handling
        request = mock_http_request(method="GET", url="/hello")
        
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.side_effect = Exception("Regression test error")
            
            response = hello_world_main(request)
            
            assert response.status_code == 500
            response_data = json.loads(response.get_body().decode())
            assert response_data["message"] == "Error occurred"
            assert response_data["status"] == "error"
            assert "error" in response_data
            assert "timestamp" in response_data
    
    @pytest.mark.regression
    def test_response_format_regression(self, mock_http_request, mock_environment_variables):
        """Regression test: Response format should remain consistent."""
        # Test health check response format
        request = mock_http_request(method="GET", url="/health")
        response = health_check_main(request)
        
        response_data = json.loads(response.get_body().decode())
        
        # Verify all required fields are present
        required_fields = ["status", "timestamp", "service", "version", "environment", "checks"]
        for field in required_fields:
            assert field in response_data, f"Required field '{field}' missing from health check response"
        
        # Verify data types
        assert isinstance(response_data["status"], str)
        assert isinstance(response_data["timestamp"], str)
        assert isinstance(response_data["service"], str)
        assert isinstance(response_data["version"], str)
        assert isinstance(response_data["environment"], str)
        assert isinstance(response_data["checks"], dict)
        
        # Test hello world response format
        request = mock_http_request(method="GET", url="/hello")
        response = hello_world_main(request)
        
        response_data = json.loads(response.get_body().decode())
        
        # Verify all required fields are present
        required_fields = ["message", "timestamp", "method", "status"]
        for field in required_fields:
            assert field in response_data, f"Required field '{field}' missing from hello world response"
        
        # Verify data types
        assert isinstance(response_data["message"], str)
        assert isinstance(response_data["timestamp"], str)
        assert isinstance(response_data["method"], str)
        assert isinstance(response_data["status"], str)
    
    @pytest.mark.regression
    def test_timestamp_format_regression(self, mock_http_request, mock_environment_variables):
        """Regression test: Timestamp format should remain consistent."""
        # Test health check timestamp
        request = mock_http_request(method="GET", url="/health")
        response = health_check_main(request)
        
        response_data = json.loads(response.get_body().decode())
        timestamp = response_data["timestamp"]
        
        # Verify timestamp format (ISO 8601 with Z suffix)
        assert timestamp.endswith("Z"), "Timestamp should end with 'Z'"
        assert len(timestamp) > 20, "Timestamp should be reasonably long"
        
        # Should be parseable as ISO format
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Timestamp should be valid ISO format")
        
        # Test hello world timestamp
        request = mock_http_request(method="GET", url="/hello")
        response = hello_world_main(request)
        
        response_data = json.loads(response.get_body().decode())
        timestamp = response_data["timestamp"]
        
        # Verify timestamp format
        assert timestamp.endswith("Z"), "Timestamp should end with 'Z'"
        assert len(timestamp) > 20, "Timestamp should be reasonably long"
        
        # Should be parseable as ISO format
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Timestamp should be valid ISO format")
    
    @pytest.mark.regression
    def test_http_methods_regression(self, mock_http_request):
        """Regression test: HTTP methods should work as expected."""
        # Test hello world with different methods
        methods = ["GET", "POST"]
        
        for method in methods:
            request = mock_http_request(method=method, url="/hello")
            response = hello_world_main(request)
            
            assert response.status_code == 200
            response_data = json.loads(response.get_body().decode())
            assert response_data["method"] == method
            assert response_data["status"] == "success"
    
    @pytest.mark.regression
    def test_environment_variables_regression(self, mock_http_request):
        """Regression test: Environment variable handling should remain consistent."""
        # Test with different environment configurations
        test_configs = [
            {"WEBSITE_SITE_NAME": "Test-App", "AZURE_FUNCTIONS_ENVIRONMENT": "Development"},
            {"WEBSITE_SITE_NAME": "Prod-App", "AZURE_FUNCTIONS_ENVIRONMENT": "Production"},
            {"WEBSITE_SITE_NAME": "Staging-App", "AZURE_FUNCTIONS_ENVIRONMENT": "Staging"},
        ]
        
        for config in test_configs:
            with patch.dict(os.environ, config):
                request = mock_http_request(method="GET", url="/health")
                response = health_check_main(request)
                
                assert response.status_code == 200
                response_data = json.loads(response.get_body().decode())
                assert response_data["service"] == config["WEBSITE_SITE_NAME"]
                assert response_data["environment"] == config["AZURE_FUNCTIONS_ENVIRONMENT"] 