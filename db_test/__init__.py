import azure.functions as func
import logging
import json
import sys
import os
from datetime import datetime

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Test environment variables and basic setup.
    """
    print("🚀 [DB TEST] Function started")
    logging.info('Database test function processed a request.')
    
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
        print("🔍 [DB TEST] Testing environment setup...")
        
        # Test 1: Check environment variables
        postgres_password = os.environ.get("POSTGRES_PASSWORD")
        print(f"🔑 [DB TEST] POSTGRES_PASSWORD set: {postgres_password is not None}")
        print(f"🔑 [DB TEST] POSTGRES_PASSWORD value: {postgres_password}")
        
        # Test 2: Check if we can import required packages
        import_status = {}
        
        try:
            import pg8000
            print("✅ [DB TEST] pg8000 imported successfully")
            import_status["pg8000"] = "success"
        except ImportError as e:
            print(f"❌ [DB TEST] Failed to import pg8000: {str(e)}")
            import_status["pg8000"] = f"failed: {str(e)}"
        
        try:
            import psycopg2
            print("✅ [DB TEST] psycopg2 imported successfully")
            import_status["psycopg2"] = "success"
        except ImportError as e:
            print(f"❌ [DB TEST] Failed to import psycopg2: {str(e)}")
            import_status["psycopg2"] = f"failed: {str(e)}"
        
        # Test 3: Check Python version and environment
        import sys
        python_version = sys.version
        print(f"🐍 [DB TEST] Python version: {python_version}")
        
        # Test 4: List all environment variables (without sensitive data)
        env_vars = {}
        for key, value in os.environ.items():
            if 'PASSWORD' in key.upper() or 'SECRET' in key.upper() or 'KEY' in key.upper():
                env_vars[key] = "***HIDDEN***"
            else:
                env_vars[key] = value
        
        print(f"🔧 [DB TEST] Environment variables count: {len(env_vars)}")
        
        # Return success response
        response_data = {
            "status": "success",
            "message": "Environment test completed",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "tests": {
                "environment_variables": {
                    "postgres_password_set": postgres_password is not None,
                    "postgres_password_value": "***" if postgres_password else None,
                    "total_env_vars": len(env_vars)
                },
                "import_status": import_status,
                "python_version": python_version,
                "environment_variables": env_vars
            }
        }
        
        print(f"📤 [DB TEST] Returning success response: {json.dumps(response_data, indent=2)}")
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
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
        print(f"💥 [DB TEST] Exception occurred: {str(e)}")
        logging.error(f'Error in database test: {str(e)}')
        
        error_response = {
            "status": "error",
            "message": "Environment test failed",
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