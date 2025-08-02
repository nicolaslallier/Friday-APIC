import pytest
import json
import sys
import os
from unittest.mock import patch, Mock
import httpx
import asyncio

# Import the functions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'health_check'))
from health_check.__init__ import main as health_check_main

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hello_world'))
from hello_world.__init__ import main as hello_world_main

import azure.functions as func


class TestAPIIntegration:
    """Functional tests for API integration."""
    
    @pytest.mark.functional
    def test_health_check_api_contract(self, mock_http_request, mock_environment_variables):
        """Test that health check API follows the expected contract."""
        # Arrange
        request = mock_http_request(method="GET", url="/health")
        
        # Act
        response = health_check_main(request)
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        response_data = json.loads(response.get_body().decode())
        
        # Verify API contract
        assert "status" in response_data
        assert response_data["status"] in ["healthy", "unhealthy"]
        assert "timestamp" in response_data
        assert "service" in response_data
        assert "version" in response_data
        assert "environment" in response_data
        assert "checks" in response_data
        assert isinstance(response_data["checks"], dict)
    
    @pytest.mark.functional
    def test_hello_world_api_contract(self, mock_http_request):
        """Test that hello world API follows the expected contract."""
        # Arrange
        request = mock_http_request(method="GET", url="/hello")
        
        # Act
        response = hello_world_main(request)
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        response_data = json.loads(response.get_body().decode())
        
        # Verify API contract
        assert "message" in response_data
        assert "timestamp" in response_data
        assert "method" in response_data
        assert "status" in response_data
        assert response_data["status"] in ["success", "error"]
    
    @pytest.mark.functional
    def test_health_check_consistency(self, mock_http_request, mock_environment_variables):
        """Test that health check returns consistent data across multiple calls."""
        # Arrange
        request = mock_http_request(method="GET", url="/health")
        
        # Act - Make multiple calls
        responses = []
        for _ in range(3):
            response = health_check_main(request)
            responses.append(json.loads(response.get_body().decode()))
        
        # Assert - Check consistency (excluding timestamp)
        for i in range(1, len(responses)):
            current = responses[i]
            previous = responses[i-1]
            
            # These should be consistent
            assert current["status"] == previous["status"]
            assert current["service"] == previous["service"]
            assert current["version"] == previous["version"]
            assert current["environment"] == previous["environment"]
            assert current["checks"] == previous["checks"]
            
            # Timestamps should be different
            assert current["timestamp"] != previous["timestamp"]
    
    @pytest.mark.functional
    def test_hello_world_personalization(self, mock_http_request):
        """Test hello world personalization feature."""
        # Arrange
        names = ["Alice", "Bob", "Charlie", "Diana"]
        
        for name in names:
            request = mock_http_request(
                method="POST", 
                url="/hello", 
                body={"name": name},
                headers={"Content-Type": "application/json"}
            )
            
            # Act
            response = hello_world_main(request)
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.get_body().decode())
            assert response_data["message"] == f"Hello, {name}!"
            assert response_data["received_name"] == name
            assert response_data["method"] == "POST"
    
    @pytest.mark.functional
    def test_error_response_format(self, mock_http_request):
        """Test that error responses follow a consistent format."""
        # Arrange
        request = mock_http_request(method="GET", url="/hello")
        
        # Mock an error
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.side_effect = Exception("Test functional error")
            
            # Act
            response = hello_world_main(request)
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.get_body().decode())
            
            # Verify error response format
            assert "message" in response_data
            assert "timestamp" in response_data
            assert "error" in response_data
            assert "status" in response_data
            assert response_data["status"] == "error"
    
    @pytest.mark.functional
    def test_health_check_environment_awareness(self, mock_http_request):
        """Test that health check is aware of different environments."""
        environments = ["Development", "Staging", "Production"]
        
        for env in environments:
            with patch.dict(os.environ, {
                'WEBSITE_SITE_NAME': 'Friday-APIC-Test',
                'AZURE_FUNCTIONS_ENVIRONMENT': env
            }):
                # Arrange
                request = mock_http_request(method="GET", url="/health")
                
                # Act
                response = health_check_main(request)
                
                # Assert
                assert response.status_code == 200
                response_data = json.loads(response.get_body().decode())
                assert response_data["environment"] == env
                assert response_data["status"] == "healthy"
    
    @pytest.mark.functional
    def test_api_response_performance(self, mock_http_request, mock_environment_variables):
        """Test that API responses are reasonably fast."""
        import time
        
        # Test health check performance
        request = mock_http_request(method="GET", url="/health")
        
        start_time = time.time()
        response = health_check_main(request)
        end_time = time.time()
        
        # Assert response time is under 1 second (reasonable for a simple function)
        assert end_time - start_time < 1.0
        assert response.status_code == 200
        
        # Test hello world performance
        request = mock_http_request(method="GET", url="/hello")
        
        start_time = time.time()
        response = hello_world_main(request)
        end_time = time.time()
        
        # Assert response time is under 1 second
        assert end_time - start_time < 1.0
        assert response.status_code == 200 