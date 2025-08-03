import azure.functions as func
import logging
import json
import os
import psutil
import sys
from datetime import datetime

# Add the shared directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

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
        
        # Database connectivity check
        db_check = {
            "status": "unknown",
            "connection": False,
            "table_readable": False,
            "error": None,
            "connection_details": {},
            "database_info": {},
            "tables_info": {},
            "detailed_errors": []
        }
        
        try:
            print("🔍 [HEALTH CHECK] Testing database connectivity...")
            from db_utils import DiagramDBManager
            
            # Test database connection
            db_manager = DiagramDBManager()
            conn = db_manager._get_connection()
            db_check["connection"] = True
            db_check["status"] = "connected"
            print("✅ [HEALTH CHECK] Database connection successful")
            
            # Get connection details
            db_check["connection_details"] = {
                "host": db_manager.connection_string["host"],
                "port": db_manager.connection_string["port"],
                "database": db_manager.connection_string["database"],
                "user": db_manager.connection_string["user"],
                "connected_at": datetime.utcnow().isoformat() + "Z"
            }
            
            cursor = conn.cursor()
            
            # Get database information
            print("📊 [HEALTH CHECK] Getting database information...")
            cursor.execute("SELECT current_database(), version()")
            db_info = cursor.fetchone()
            db_check["database_info"] = {
                "current_database": db_info[0] if db_info else "unknown",
                "version": db_info[1] if db_info else "unknown"
            }
            
            # List all databases
            cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
            databases = cursor.fetchall()
            db_check["database_info"]["available_databases"] = [db[0] for db in databases]
            
            # List all schemas in current database
            cursor.execute("SELECT schema_name FROM information_schema.schemata")
            schemas = cursor.fetchall()
            db_check["database_info"]["schemas"] = [schema[0] for schema in schemas]
            
            # List all tables in public schema
            cursor.execute("""
                SELECT table_name, table_type 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name
            """)
            tables = cursor.fetchall()
            db_check["tables_info"]["public_schema_tables"] = [
                {"name": table[0], "type": table[1]} for table in tables
            ]
            
            # Get detailed information about t_diagram table
            print("📋 [HEALTH CHECK] Getting t_diagram table details...")
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public' AND table_name = 't_diagram'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            db_check["tables_info"]["t_diagram_structure"] = [
                {
                    "column_name": col[0],
                    "data_type": col[1],
                    "is_nullable": col[2],
                    "default_value": col[3]
                } for col in columns
            ]
            
            # Test table readability
            cursor.execute("SELECT COUNT(*) FROM public.t_diagram")
            result = cursor.fetchone()
            db_check["table_readable"] = True
            db_check["table_count"] = result[0] if result else 0
            print(f"✅ [HEALTH CHECK] Table readable, count: {db_check['table_count']}")
            
            # Test a simple query to verify table structure
            cursor.execute("SELECT diagram_id, name FROM public.t_diagram LIMIT 1")
            sample_result = cursor.fetchone()
            if sample_result:
                db_check["sample_data"] = {
                    "diagram_id": sample_result[0],
                    "name": sample_result[1]
                }
            
            # Get table size information
            cursor.execute("""
                SELECT 
                    pg_size_pretty(pg_total_relation_size('public.t_diagram')) as total_size,
                    pg_size_pretty(pg_relation_size('public.t_diagram')) as table_size,
                    pg_size_pretty(pg_total_relation_size('public.t_diagram') - pg_relation_size('public.t_diagram')) as index_size
            """)
            size_info = cursor.fetchone()
            if size_info:
                db_check["tables_info"]["t_diagram_size"] = {
                    "total_size": size_info[0],
                    "table_size": size_info[1],
                    "index_size": size_info[2]
                }
            
            conn.close()
            print("✅ [HEALTH CHECK] Database check completed successfully")
            
        except ImportError as import_error:
            error_msg = f"Failed to import database utilities: {str(import_error)}"
            print(f"❌ [HEALTH CHECK] {error_msg}")
            db_check["status"] = "error"
            db_check["error"] = error_msg
            db_check["detailed_errors"].append({
                "type": "ImportError",
                "message": str(import_error),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            
        except Exception as db_error:
            error_msg = f"Database check failed: {str(db_error)}"
            print(f"❌ [HEALTH CHECK] {error_msg}")
            db_check["status"] = "error"
            db_check["error"] = error_msg
            db_check["detailed_errors"].append({
                "type": type(db_error).__name__,
                "message": str(db_error),
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "connection_details": {
                    "host": "pg-frdypgdb-prd-cac.postgres.database.azure.com",
                    "port": 5432,
                    "database": "Architecture",
                    "user": "nlallier"
                }
            })
            
            # Try to get more specific error information
            if "password" in str(db_error).lower():
                db_check["detailed_errors"][-1]["suggestion"] = "Check POSTGRES_PASSWORD environment variable"
            elif "connection" in str(db_error).lower():
                db_check["detailed_errors"][-1]["suggestion"] = "Check network connectivity and firewall rules"
            elif "database" in str(db_error).lower():
                db_check["detailed_errors"][-1]["suggestion"] = "Check if database 'Architecture' exists"
            elif "table" in str(db_error).lower():
                db_check["detailed_errors"][-1]["suggestion"] = "Check if table 'public.t_diagram' exists"
        
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
        
        # Determine overall health status
        overall_status = "healthy"
        if db_check["status"] == "error":
            overall_status = "degraded"
        
        # Prepare health data
        health_data = {
            "status": overall_status,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "Friday APIC",
            "version": "1.0.0",
            "checks": {
                "runtime": "healthy",
                "database": db_check,
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