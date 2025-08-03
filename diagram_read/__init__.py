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
    Read diagrams from the PostgreSQL database.
    
    Query parameters:
    - id: Get specific diagram by ID
    """
    print("🚀 [DIAGRAM READ] Function started")
    logging.info('Diagram read function processed a request.')
    
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
        # Get query parameters
        diagram_id = req.params.get('id')
        
        print(f"🔍 [DIAGRAM READ] Query parameters - ID: {diagram_id}")
        
        db_manager = DiagramDBManager()
        
        # If specific ID is requested
        if diagram_id:
            print(f"🎯 [DIAGRAM READ] Looking for specific diagram with ID: {diagram_id}")
            diagram = db_manager.read_diagrams(diagram_id=diagram_id)
            if not diagram:
                print(f"❌ [DIAGRAM READ] Diagram with ID '{diagram_id}' not found")
                return func.HttpResponse(
                    json.dumps({
                        "status": "error",
                        "message": f"Diagram with ID '{diagram_id}' not found"
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
            
            print(f"✅ [DIAGRAM READ] Found diagram: {diagram['name']}")
            response_data = {
                "status": "success",
                "diagram": diagram,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
            
            print(f"📤 [DIAGRAM READ] Returning diagram: {json.dumps(response_data, indent=2)}")
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
        
        # Get all diagrams
        print("📋 [DIAGRAM READ] Reading all diagrams...")
        diagrams = db_manager.read_diagrams()
        print(f"📊 [DIAGRAM READ] Found {len(diagrams)} total diagrams")
        
        response_data = {
            "status": "success",
            "count": len(diagrams),
            "diagrams": diagrams,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        print(f"📤 [DIAGRAM READ] Returning {len(diagrams)} diagrams")
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
        print(f"💥 [DIAGRAM READ] Exception occurred: {str(e)}")
        logging.error(f'Error in diagram read: {str(e)}')
        
        error_response = {
            "status": "error",
            "message": "Failed to read diagrams",
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