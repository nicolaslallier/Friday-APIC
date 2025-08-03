import azure.functions as func
import logging
import json
import os
import psutil
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint that returns system status and metrics.
    """
    print("🚀 [HEALTH CHECK] Function started")
    logging.info('Health check function processed a request.')
    
    # Handle CORS preflight requests
    if req.method == "OPTIONS":
        return func.HttpResponse(
            status_code=200,
            headers={
                "Access-Control-Allow-Origin": "https://stfrdywpuiprdcac.z9.web.core.windows.net",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Access-Control-Allow-Credentials": "true"
            }
        )
    
    try:
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Check if health.txt exists in /func1 mount path
        health_file_path = "/func1/health.txt"
        file_check = {
            "exists": os.path.exists(health_file_path),
            "path": health_file_path
        }
        
        # Create health.txt if it doesn't exist
        if not file_check["exists"]:
            print(f"📄 [HEALTH CHECK] Creating health file: {health_file_path}")
            try:
                with open(health_file_path, 'w') as f:
                    f.write("# Health Check Log\n")
                file_check["created"] = True
                file_check["exists"] = True
            except Exception as e:
                print(f"❌ [HEALTH CHECK] Failed to create health file: {str(e)}")
                file_check["error"] = str(e)
        
        # Prepare health data
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "Friday APIC",
            "version": "1.0.0",
            "checks": {
                "runtime": "healthy",
                "file_system": file_check
            },
            "system_metrics": {
                "memory": {
                    "total": memory.total,
                    "available": memory.available,
                    "percent": memory.percent,
                    "used": memory.used
                },
                "cpu": {
                    "percent": cpu_percent
                }
            }
        }
        
        # Append health data to health.txt for MongoDB import
        try:
            print(f"📝 [HEALTH CHECK] Appending health data to: {health_file_path}")
            import uuid
            health_data["_id"] = str(uuid.uuid4())  # Add MongoDB _id field
            
            with open(health_file_path, 'a') as f:
                f.write(json.dumps(health_data) + "\n")
            
            health_data["file_operation"] = "success"
        except Exception as e:
            print(f"❌ [HEALTH CHECK] Failed to append to health file: {str(e)}")
            health_data["file_operation"] = f"error: {str(e)}"
        
        print(f"📤 [HEALTH CHECK] Returning health data: {json.dumps(health_data, indent=2)}")
        return func.HttpResponse(
            json.dumps(health_data, indent=2),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "https://stfrdywpuiprdcac.z9.web.core.windows.net",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Access-Control-Allow-Credentials": "true"
            }
        )
        
    except Exception as e:
        print(f"💥 [HEALTH CHECK] Exception occurred: {str(e)}")
        logging.error(f'Error in health check: {str(e)}')
        
        error_response = {
            "status": "error",
            "message": "Health check failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        return func.HttpResponse(
            json.dumps(error_response, indent=2),
            status_code=500,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "https://stfrdywpuiprdcac.z9.web.core.windows.net",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Access-Control-Allow-Credentials": "true"
            }
        ) 