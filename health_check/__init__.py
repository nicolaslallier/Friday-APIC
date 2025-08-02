import azure.functions as func
import logging
import json
from datetime import datetime
import os
import psutil


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
        
        # Check and create health.txt file in mount path
        mount_path = "/func1"
        health_file_path = f"{mount_path}/health.txt"
        file_check_status = "healthy"
        
        try:
            # Check if the mount path exists
            if not os.path.exists(mount_path):
                os.makedirs(mount_path, exist_ok=True)
                logging.info(f'Created mount path: {mount_path}')
            
            # Check if health.txt exists
            if not os.path.exists(health_file_path):
                # Create the health.txt file with current timestamp
                with open(health_file_path, 'w') as f:
                    f.write(f"Health check file created at: {current_time}\n")
                    f.write(f"Service: {function_app_name}\n")
                    f.write(f"Environment: {os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT', 'Development')}\n")
                logging.info(f'Created health.txt file at: {health_file_path}')
                file_check_status = "created"
            else:
                # Update the health.txt file with current timestamp
                with open(health_file_path, 'w') as f:
                    f.write(f"Health check file updated at: {current_time}\n")
                    f.write(f"Service: {function_app_name}\n")
                    f.write(f"Environment: {os.environ.get('AZURE_FUNCTIONS_ENVIRONMENT', 'Development')}\n")
                logging.info(f'Updated health.txt file at: {health_file_path}')
                file_check_status = "updated"
                
        except Exception as e:
            logging.error(f'Error with file operations: {str(e)}')
            file_check_status = "error"
        
        # Get system metrics
        try:
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            system_metrics = {
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "used": memory.used,
                    "percent": memory.percent
                },
                "cpu": {
                    "percent": cpu_percent
                }
            }
        except Exception as e:
            logging.warning(f'Could not get system metrics: {str(e)}')
            system_metrics = {
                "memory": {"error": "Unable to retrieve memory metrics"},
                "cpu": {"error": "Unable to retrieve CPU metrics"}
            }
        
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
                "timestamp_check": "healthy",
                "file_check": file_check_status
            },
            "system_metrics": system_metrics,
            "file_operations": {
                "mount_path": mount_path,
                "health_file": health_file_path,
                "status": file_check_status
            }
        }
        
        # Append health check data to file in JSON format for MongoDB import
        try:
            # Create MongoDB-ready document with _id for unique identification
            mongo_document = {
                "_id": f"health_check_{current_time.replace(':', '-').replace('.', '-')}",
                "health_check_data": health_data,
                "created_at": current_time,
                "service_name": function_app_name
            }
            
            # Append the JSON document to the file
            with open(health_file_path, 'a') as f:
                f.write(json.dumps(mongo_document, indent=2) + "\n")
            
            logging.info(f'Appended health check data to {health_file_path} for MongoDB import')
            
        except Exception as e:
            logging.error(f'Error appending health check data to file: {str(e)}')
        
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