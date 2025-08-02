import azure.functions as func
import logging
import json
from datetime import datetime


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Hello world endpoint that returns a greeting message.
    
    Returns:
        func.HttpResponse: JSON response with greeting message
    """
    logging.info('Hello world function processed a request.')
    
    try:
        # Get the request method
        method = req.method
        
        # Get current timestamp
        current_time = datetime.utcnow().isoformat() + "Z"
        
        # Create response data
        response_data = {
            "message": "Hello, World!",
            "timestamp": current_time,
            "method": method,
            "status": "success"
        }
        
        # If it's a POST request, try to get the request body
        if method == "POST":
            try:
                req_body = req.get_json()
                if req_body and "name" in req_body:
                    response_data["message"] = f"Hello, {req_body['name']}!"
                    response_data["received_name"] = req_body["name"]
            except ValueError:
                response_data["message"] = "Hello, World! (No valid JSON body provided)"
        
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=200,
            mimetype="application/json"
        )
        
    except Exception as e:
        logging.error(f'Error in hello world function: {str(e)}')
        
        error_response = {
            "message": "Error occurred",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "error": str(e),
            "status": "error"
        }
        
        return func.HttpResponse(
            json.dumps(error_response, indent=2),
            status_code=500,
            mimetype="application/json"
        ) 