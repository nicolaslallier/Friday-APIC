import azure.functions as func
import logging
import json
import sys
import os
from datetime import datetime

# Add the shared directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))
from db_utils import DiagramDBManager

def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Create a new diagram in the PostgreSQL database.
    
    Expected JSON body:
    {
        "name": "Diagram Name",
        "description": "Diagram Description",
        "content": "Diagram content/data"
    }
    """
    print("🚀 [DIAGRAM CREATE] Function started")
    logging.info('Diagram create function processed a request.')
    
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
        # Parse request body
        print("📥 [DIAGRAM CREATE] Parsing request body...")
        try:
            req_body = req.get_json()
            print(f"📄 [DIAGRAM CREATE] Request body: {json.dumps(req_body, indent=2)}")
        except ValueError as e:
            print(f"❌ [DIAGRAM CREATE] Invalid JSON: {str(e)}")
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON in request body"}),
                status_code=400,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "https://stfrdywpuiprdcac.z9.web.core.windows.net",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                    "Access-Control-Allow-Credentials": "true"
                }
            )
        
        # Validate required fields
        print("✅ [DIAGRAM CREATE] Validating required fields...")
        required_fields = ['name']
        missing_fields = [field for field in required_fields if not req_body.get(field)]
        
        if missing_fields:
            print(f"❌ [DIAGRAM CREATE] Missing fields: {missing_fields}")
            return func.HttpResponse(
                json.dumps({
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }),
                status_code=400,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "https://stfrdywpuiprdcac.z9.web.core.windows.net",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                    "Access-Control-Allow-Credentials": "true"
                }
            )
        
        # Create diagram
        print("➕ [DIAGRAM CREATE] Creating diagram...")
        db_manager = DiagramDBManager()
        new_diagram = db_manager.create_diagram(req_body)
        print(f"✅ [DIAGRAM CREATE] Diagram created with ID: {new_diagram['id']}")
        
        # Return success response
        response_data = {
            "status": "success",
            "message": "Diagram created successfully",
            "diagram": new_diagram,
            "timestamp": new_diagram['created_at']
        }
        
        print(f"📤 [DIAGRAM CREATE] Returning success response: {json.dumps(response_data, indent=2)}")
        return func.HttpResponse(
            json.dumps(response_data, indent=2),
            status_code=201,
            mimetype="application/json",
            headers={
                "Access-Control-Allow-Origin": "https://stfrdywpuiprdcac.z9.web.core.windows.net",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                "Access-Control-Allow-Credentials": "true"
            }
        )
        
    except Exception as e:
        print(f"💥 [DIAGRAM CREATE] Exception occurred: {str(e)}")
        logging.error(f'Error in diagram create: {str(e)}')
        
        error_response = {
            "status": "error",
            "message": "Failed to create diagram",
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