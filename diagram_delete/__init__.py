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
    Delete a diagram from the PostgreSQL database.
    
    Query parameters:
    - diagram_id: Diagram ID to delete (required)
    """
    print("🚀 [DIAGRAM DELETE] Function started")
    logging.info('Diagram delete function processed a request.')
    
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
        # Get diagram ID from query parameters
        diagram_id = req.params.get('diagram_id')
        print(f"🆔 [DIAGRAM DELETE] Diagram ID: {diagram_id}")
        
        if not diagram_id:
            print("❌ [DIAGRAM DELETE] No diagram ID provided")
            return func.HttpResponse(
                json.dumps({
                    "error": "diagram_id is required as a query parameter"
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
        
        # Convert diagram_id to integer
        try:
            diagram_id = int(diagram_id)
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "diagram_id must be a valid integer"}),
                status_code=400,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "https://stfrdywpuiprdcac.z9.web.core.windows.net",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                    "Access-Control-Allow-Credentials": "true"
                }
            )
        
        # Delete diagram
        print(f"🗑️ [DIAGRAM DELETE] Deleting diagram with ID: {diagram_id}")
        db_manager = DiagramDBManager()
        success = db_manager.delete_diagram(diagram_id)
        
        if not success:
            print(f"❌ [DIAGRAM DELETE] Diagram with ID '{diagram_id}' not found")
            return func.HttpResponse(
                json.dumps({
                    "error": f"Diagram with ID '{diagram_id}' not found"
                }),
                status_code=404,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Origin": "https://stfrdywpuiprdcac.z9.web.core.windows.net",
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                    "Access-Control-Allow-Credentials": "true"
                }
            )
        
        print(f"✅ [DIAGRAM DELETE] Diagram deleted successfully: {diagram_id}")
        
        # Return success response
        response_data = {
            "status": "success",
            "message": "Diagram deleted successfully",
            "deleted_diagram_id": diagram_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        print(f"📤 [DIAGRAM DELETE] Returning success response: {json.dumps(response_data, indent=2)}")
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
        print(f"💥 [DIAGRAM DELETE] Exception occurred: {str(e)}")
        logging.error(f'Error in diagram delete: {str(e)}')
        
        error_response = {
            "status": "error",
            "message": "Failed to delete diagram",
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