import pg8000
import json
from datetime import datetime
import os

class DiagramDBManager:
    def __init__(self):
        self.connection_string = {
            "user": "nlallier",
            "password": os.environ.get("POSTGRES_PASSWORD", "{your_password}"),
            "host": "pg-frdypgdb-prd-cac.postgres.database.azure.com",
            "port": 5432,
            "database": "postgres"
        }
    
    def _get_connection(self):
        """Get a database connection"""
        try:
            conn = pg8000.connect(**self.connection_string)
            print(f"Database connection established successfully")
            return conn
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise
    
    def create_diagram(self, diagram_data):
        """Create a new diagram"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Generate ID
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            diagram_id = f"diag_{timestamp}"
            
            insert_sql = """
            INSERT INTO public.t_diagram (id, name, description, content, created_at, updated_at)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            RETURNING id, name, description, content, created_at, updated_at
            """
            
            cursor.execute(insert_sql, (
                diagram_id,
                diagram_data.get('name'),
                diagram_data.get('description'),
                diagram_data.get('content')
            ))
            
            result = cursor.fetchone()
            conn.commit()
            
            diagram = {
                'id': result[0],
                'name': result[1],
                'description': result[2],
                'content': result[3],
                'created_at': result[4].isoformat() if result[4] else None,
                'updated_at': result[5].isoformat() if result[5] else None
            }
            
            print(f"Diagram created successfully with ID: {diagram_id}")
            return diagram
            
        except Exception as e:
            print(f"Error creating diagram: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def read_diagrams(self, diagram_id=None):
        """Read diagrams with optional filtering"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if diagram_id:
                # Read specific diagram by ID
                select_sql = """
                SELECT id, name, description, content, created_at, updated_at
                FROM public.t_diagram WHERE id = %s
                """
                cursor.execute(select_sql, (diagram_id,))
                result = cursor.fetchone()
                
                if result:
                    diagram = {
                        'id': result[0],
                        'name': result[1],
                        'description': result[2],
                        'content': result[3],
                        'created_at': result[4].isoformat() if result[4] else None,
                        'updated_at': result[5].isoformat() if result[5] else None
                    }
                    print(f"Diagram found: {diagram_id}")
                    return diagram
                else:
                    print(f"Diagram not found: {diagram_id}")
                    return None
            else:
                # Read all diagrams
                select_sql = """
                SELECT id, name, description, content, created_at, updated_at
                FROM public.t_diagram
                ORDER BY created_at DESC
                """
                
                cursor.execute(select_sql)
                results = cursor.fetchall()
                
                diagrams = []
                for result in results:
                    diagram = {
                        'id': result[0],
                        'name': result[1],
                        'description': result[2],
                        'content': result[3],
                        'created_at': result[4].isoformat() if result[4] else None,
                        'updated_at': result[5].isoformat() if result[5] else None
                    }
                    diagrams.append(diagram)
                
                print(f"Found {len(diagrams)} diagrams")
                return diagrams
                
        except Exception as e:
            print(f"Error reading diagrams: {str(e)}")
            raise
        finally:
            if conn:
                conn.close()
    
    def update_diagram(self, diagram_id, update_data):
        """Update an existing diagram"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if diagram exists
            check_sql = "SELECT id FROM public.t_diagram WHERE id = %s"
            cursor.execute(check_sql, (diagram_id,))
            if not cursor.fetchone():
                print(f"Diagram not found: {diagram_id}")
                return None
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            for field in ['name', 'description', 'content']:
                if field in update_data and update_data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(update_data[field])
            
            if not update_fields:
                print("No valid fields to update")
                return None
            
            # Add updated_at timestamp
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            params.append(diagram_id)
            
            update_sql = f"""
            UPDATE public.t_diagram 
            SET {', '.join(update_fields)}
            WHERE id = %s
            RETURNING id, name, description, content, created_at, updated_at
            """
            
            cursor.execute(update_sql, params)
            result = cursor.fetchone()
            conn.commit()
            
            diagram = {
                'id': result[0],
                'name': result[1],
                'description': result[2],
                'content': result[3],
                'created_at': result[4].isoformat() if result[4] else None,
                'updated_at': result[5].isoformat() if result[5] else None
            }
            
            print(f"Diagram updated successfully: {diagram_id}")
            return diagram
            
        except Exception as e:
            print(f"Error updating diagram: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def delete_diagram(self, diagram_id):
        """Delete a diagram"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Check if diagram exists
            check_sql = "SELECT id FROM public.t_diagram WHERE id = %s"
            cursor.execute(check_sql, (diagram_id,))
            if not cursor.fetchone():
                print(f"Diagram not found: {diagram_id}")
                return False
            
            # Delete the diagram
            delete_sql = "DELETE FROM public.t_diagram WHERE id = %s"
            cursor.execute(delete_sql, (diagram_id,))
            conn.commit()
            
            print(f"Diagram deleted successfully: {diagram_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting diagram: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close() 