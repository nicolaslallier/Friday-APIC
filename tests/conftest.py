import pytest
import sys
import os
from unittest.mock import Mock, patch
import azure.functions as func
import json

# Add the parent directory to the path so we can import our functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def mock_http_request():
    """Create a mock HTTP request for testing."""
    def _create_request(method="GET", url="/", body=None, headers=None):
        request = Mock(spec=func.HttpRequest)
        request.method = method
        request.url = url
        request.headers = headers or {}
        
        if body:
            if isinstance(body, dict):
                request.get_json.return_value = body
                request.get_body.return_value = json.dumps(body).encode('utf-8')
            else:
                request.get_body.return_value = body.encode('utf-8') if isinstance(body, str) else body
        else:
            request.get_json.return_value = {}
            request.get_body.return_value = b""
        
        return request
    
    return _create_request

@pytest.fixture
def mock_environment_variables():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'WEBSITE_SITE_NAME': 'Friday-APIC-Test',
        'AZURE_FUNCTIONS_ENVIRONMENT': 'Test'
    }):
        yield

@pytest.fixture
def sample_health_data():
    """Sample health check response data."""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T12:00:00.000000Z",
        "service": "Friday-APIC-Test",
        "version": "1.0.0",
        "environment": "Test",
        "checks": {
            "function_app": "healthy",
            "runtime": "python",
            "timestamp_check": "healthy"
        }
    }

@pytest.fixture
def sample_hello_response():
    """Sample hello world response data."""
    return {
        "message": "Hello, World!",
        "timestamp": "2024-01-01T12:00:00.000000Z",
        "method": "GET",
        "status": "success"
    } 