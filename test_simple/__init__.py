import azure.functions as func
import logging
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Simple test function to verify basic functionality
    """
    print("🚀 [TEST SIMPLE] Function started")
    logging.info('Test simple function processed a request.')
    
    try:
        response_data = {
            "status": "success",
            "message": "Test function is working",
            "timestamp": "2025-08-02T19:10:00Z"
        }
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            }
        )
        
    except Exception as e:
        print(f"💥 [TEST SIMPLE] Exception occurred: {str(e)}")
        logging.error(f'Error in test simple: {str(e)}')
        
        error_response = {
            "status": "error",
            "message": "Test function failed",
            "error": str(e)
        }
        
        return func.HttpResponse(
            json.dumps(error_response, indent=2),
            status_code=500,
            mimetype="application/json"
        ) 