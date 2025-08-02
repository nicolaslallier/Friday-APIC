import azure.functions as func
import logging
import json
from datetime import datetime
import os


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint that returns the status of the function app.
    
    Returns:
        func.HttpResponse: JSON response with health status and metadata
    """
    logging.info('Health check function processed a request.')
    
    try:
        # Get current timestamp
        current_time = datetime.utcnow().isoformat() + "Z"
        
        # Get function app name from environment variable or use default
        function_app_name = os.environ.get('WEBSITE_SITE_NAME', 'Friday-APIC')
        
        # Create health check response
        health_data = {
            "status": "healthy",
            "timestamp": current_time,
            "service": function_app_name,
            "version": "1.0.0",
            "environment": os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT', 'Development'),
            "checks": {
                "function_app": "healthy",
                "runtime": "healthy",
                "timestamp_check": "healthy"
            }
        }
        
        return func.HttpResponse(
            json.dumps(health_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f'Error in health check: {str(e)}')
        
        error_response = {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
            "service": os.environ.get('WEBSITE_SITE_NAME', 'Friday-APIC')
        }
        
        return func.HttpResponse(
            json.dumps(error_response, indent=2),
            status_code=500,
            mimetype="application/json"
        ) 