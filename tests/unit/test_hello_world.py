import pytest
import json
import sys
import os
from unittest.mock import patch, Mock
from datetime import datetime

# Import the hello world function
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from hello_world.__init__ import main
import azure.functions as func


class TestHelloWorldUnit:
    """Unit tests for the hello world function."""
    
    @pytest.mark.unit
    def test_hello_world_get_success(self, mock_http_request):
        """Test successful GET request to hello world."""
        # Arrange
        request = mock_http_request(method="GET", url="/hello")
        
        # Act
        response = main(request)
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == "application/json"
        
        response_data = json.loads(response.get_body().decode())
        assert response_data["message"] == "Hello, World!"
        assert response_data["method"] == "GET"
        assert response_data["status"] == "success"
        assert "timestamp" in response_data
    
    @pytest.mark.unit
    def test_hello_world_post_with_name(self, mock_http_request):
        """Test POST request with name in body."""
        # Arrange
        request = mock_http_request(
            method="POST", 
            url="/hello", 
            body={"name": "John"},
            headers={"Content-Type": "application/json"}
        )
        
        # Act
        response = main(request)
        
        # Assert
        assert response.status_code == 200
        response_data = json.loads(response.get_body().decode())
        assert response_data["message"] == "Hello, John!"
        assert response_data["method"] == "POST"
        assert response_data["status"] == "success"
        assert response_data["received_name"] == "John"
        assert "timestamp" in response_data
    
    @pytest.mark.unit
    def test_hello_world_post_without_name(self, mock_http_request):
        """Test POST request without name in body."""
        # Arrange
        request = mock_http_request(
            method="POST", 
            url="/hello", 
            body={},
            headers={"Content-Type": "application/json"}
        )
        
        # Act
        response = main(request)
        
        # Assert
        assert response.status_code == 200
        response_data = json.loads(response.get_body().decode())
        assert response_data["message"] == "Hello, World!"
        assert response_data["method"] == "POST"
        assert response_data["status"] == "success"
        assert "received_name" not in response_data
    
    @pytest.mark.unit
    def test_hello_world_post_invalid_json(self, mock_http_request):
        """Test POST request with invalid JSON."""
        # Arrange
        request = mock_http_request(
            method="POST", 
            url="/hello", 
            body="invalid json",
            headers={"Content-Type": "application/json"}
        )
        request.get_json.side_effect = ValueError("Invalid JSON")
        
        # Act
        response = main(request)
        
        # Assert
        assert response.status_code == 200
        response_data = json.loads(response.get_body().decode())
        assert "No valid JSON body provided" in response_data["message"]
        assert response_data["method"] == "POST"
        assert response_data["status"] == "success"
    
    @pytest.mark.unit
    def test_hello_world_timestamp_format(self, mock_http_request):
        """Test that timestamp is in correct ISO format."""
        # Arrange
        request = mock_http_request(method="GET", url="/hello")
        
        # Act
        response = main(request)
        
        # Assert
        response_data = json.loads(response.get_body().decode())
        timestamp = response_data["timestamp"]
        
        # Check if timestamp is valid ISO format ending with Z
        assert timestamp.endswith("Z")
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    
    @pytest.mark.unit
    def test_hello_world_error_handling(self, mock_http_request):
        """Test hello world error handling."""
        # Arrange
        request = mock_http_request(method="GET", url="/hello")
        
        # Mock datetime to raise an exception
        with patch('datetime.datetime') as mock_datetime:
            mock_datetime.utcnow.side_effect = Exception("Test error")
            
            # Act
            response = main(request)
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.get_body().decode())
            assert response_data["message"] == "Error occurred"
            assert response_data["status"] == "error"
            assert "error" in response_data
            assert "Test error" in response_data["error"]
    
    @pytest.mark.unit
    def test_hello_world_response_structure(self, mock_http_request):
        """Test that hello world response has the correct structure."""
        # Arrange
        request = mock_http_request(method="GET", url="/hello")
        
        # Act
        response = main(request)
        
        # Assert
        response_data = json.loads(response.get_body().decode())
        
        # Check required fields
        required_fields = ["message", "timestamp", "method", "status"]
        for field in required_fields:
            assert field in response_data
    
    @pytest.mark.unit
    def test_hello_world_different_methods(self, mock_http_request):
        """Test hello world with different HTTP methods."""
        methods = ["GET", "POST", "PUT", "DELETE"]
        
        for method in methods:
            # Arrange
            request = mock_http_request(method=method, url="/hello")
            
            # Act
            response = main(request)
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.get_body().decode())
            assert response_data["method"] == method
            assert response_data["status"] == "success" 