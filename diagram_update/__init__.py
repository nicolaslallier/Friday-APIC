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
    Update an existing diagram in the PostgreSQL database.
    
    Query parameters:
    - diagram_id: Diagram ID to update (required)
    
    Expected JSON body (all fields optional):
    {
        "package_id": 1,
        "parentid": 0,
        "diagram_type": "Class",
        "name": "Updated Diagram Name",
        "version": "1.1",
        "author": "Updated Author",
        "showdetails": 1,
        "notes": "Updated notes",
        "stereotype": "updated_stereotype",
        "attpub": 1,
        "attpri": 1,
        "attpro": 1,
        "orientation": "L",
        "cx": 100,
        "cy": 100,
        "scale": 150,
        "htmlpath": "/updated/path/to/html",
        "showforeign": 0,
        "showborder": 0,
        "showpackagecontents": 0,
        "pdata": "updated_pdata",
        "locked": 1,
        "ea_guid": "updated_guid",
        "tpos": 1,
        "swimlanes": "updated_swimlanes",
        "styleex": "updated_styleex"
    }
    """
    print("🚀 [DIAGRAM UPDATE] Function started")
    logging.info('Diagram update function processed a request.')
    
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
        print(f"🆔 [DIAGRAM UPDATE] Diagram ID: {diagram_id}")
        
        if not diagram_id:
            print("❌ [DIAGRAM UPDATE] No diagram ID provided")
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
        
        # Parse request body
        print("📥 [DIAGRAM UPDATE] Parsing request body...")
        try:
            req_body = req.get_json()
            print(f"📄 [DIAGRAM UPDATE] Request body: {json.dumps(req_body, indent=2)}")
        except ValueError as e:
            print(f"❌ [DIAGRAM UPDATE] Invalid JSON: {str(e)}")
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
        
        # Update diagram
        print(f"🔄 [DIAGRAM UPDATE] Updating diagram with ID: {diagram_id}")
        db_manager = DiagramDBManager()
        updated_diagram = db_manager.update_diagram(diagram_id, req_body)
        
        if not updated_diagram:
            print(f"❌ [DIAGRAM UPDATE] Diagram with ID '{diagram_id}' not found")
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
        
        print(f"✅ [DIAGRAM UPDATE] Diagram updated successfully: {updated_diagram['name']}")
        
        # Return success response
        response_data = {
            "status": "success",
            "message": "Diagram updated successfully",
            "diagram": updated_diagram,
            "timestamp": updated_diagram['modifieddate']
        }
        
        print(f"📤 [DIAGRAM UPDATE] Returning success response: {json.dumps(response_data, indent=2)}")
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
        print(f"💥 [DIAGRAM UPDATE] Exception occurred: {str(e)}")
        logging.error(f'Error in diagram update: {str(e)}')
        
        error_response = {
            "status": "error",
            "message": "Failed to update diagram",
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