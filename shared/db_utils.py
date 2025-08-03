try:
    import psycopg
    print("✅ psycopg is installed")
except ImportError:
    print("❌ psycopg is NOT installed")
import json
from datetime import datetime
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".python_packages/lib/site-packages"))

class DiagramDBManager:
    def __init__(self):
        # Build connection string in the format recommended by Microsoft
        password = os.environ.get("POSTGRES_PASSWORD", "Moine101")
        self.connection_string = f"host=pg-frdypgdb-prd-cac.postgres.database.azure.com port=5432 dbname=Architecture user=nlallier password={password} sslmode=require"
    
    def _get_connection(self):
        """Get a database connection"""
        try:
            conn = psycopg.connect(**self.connection_string)
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
            
            # Build insert query with all fields
            insert_sql = """
            INSERT INTO public.t_diagram (
                package_id, parentid, diagram_type, name, version, author, 
                showdetails, notes, stereotype, attpub, attpri, attpro, 
                orientation, cx, cy, scale, htmlpath, showforeign, showborder, 
                showpackagecontents, pdata, locked, ea_guid, tpos, swimlanes, styleex
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING diagram_id, package_id, parentid, diagram_type, name, version, 
                author, showdetails, notes, stereotype, attpub, attpri, attpro, 
                orientation, cx, cy, scale, createddate, modifieddate, htmlpath, 
                showforeign, showborder, showpackagecontents, pdata, locked, ea_guid, 
                tpos, swimlanes, styleex
            """
            
            # Prepare values with defaults
            values = (
                diagram_data.get('package_id', 1),
                diagram_data.get('parentid', 0),
                diagram_data.get('diagram_type'),
                diagram_data.get('name'),
                diagram_data.get('version', '1.0'),
                diagram_data.get('author'),
                diagram_data.get('showdetails', 0),
                diagram_data.get('notes'),
                diagram_data.get('stereotype'),
                diagram_data.get('attpub', 1),
                diagram_data.get('attpri', 1),
                diagram_data.get('attpro', 1),
                diagram_data.get('orientation', 'P'),
                diagram_data.get('cx', 0),
                diagram_data.get('cy', 0),
                diagram_data.get('scale', 100),
                diagram_data.get('htmlpath'),
                diagram_data.get('showforeign', 1),
                diagram_data.get('showborder', 1),
                diagram_data.get('showpackagecontents', 1),
                diagram_data.get('pdata'),
                diagram_data.get('locked', 0),
                diagram_data.get('ea_guid'),
                diagram_data.get('tpos'),
                diagram_data.get('swimlanes'),
                diagram_data.get('styleex')
            )
            
            cursor.execute(insert_sql, values)
            result = cursor.fetchone()
            conn.commit()
            
            # Build response dictionary
            diagram = {
                'diagram_id': result[0],
                'package_id': result[1],
                'parentid': result[2],
                'diagram_type': result[3],
                'name': result[4],
                'version': result[5],
                'author': result[6],
                'showdetails': result[7],
                'notes': result[8],
                'stereotype': result[9],
                'attpub': result[10],
                'attpri': result[11],
                'attpro': result[12],
                'orientation': result[13],
                'cx': result[14],
                'cy': result[15],
                'scale': result[16],
                'createddate': result[17].isoformat() if result[17] else None,
                'modifieddate': result[18].isoformat() if result[18] else None,
                'htmlpath': result[19],
                'showforeign': result[20],
                'showborder': result[21],
                'showpackagecontents': result[22],
                'pdata': result[23],
                'locked': result[24],
                'ea_guid': result[25],
                'tpos': result[26],
                'swimlanes': result[27],
                'styleex': result[28]
            }
            
            print(f"Diagram created successfully with ID: {diagram['diagram_id']}")
            return diagram
            
        except Exception as e:
            print(f"Error creating diagram: {str(e)}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()
    
    def read_diagrams(self, diagram_id=None, package_id=None, diagram_type=None):
        """Read diagrams with optional filtering"""
        conn = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            if diagram_id:
                # Read specific diagram by ID
                select_sql = """
                SELECT diagram_id, package_id, parentid, diagram_type, name, version, 
                    author, showdetails, notes, stereotype, attpub, attpri, attpro, 
                    orientation, cx, cy, scale, createddate, modifieddate, htmlpath, 
                    showforeign, showborder, showpackagecontents, pdata, locked, ea_guid, 
                    tpos, swimlanes, styleex
                FROM public.t_diagram WHERE diagram_id = %s
                """
                cursor.execute(select_sql, (diagram_id,))
                result = cursor.fetchone()
                
                if result:
                    diagram = self._build_diagram_dict(result)
                    print(f"Diagram found: {diagram_id}")
                    return diagram
                else:
                    print(f"Diagram not found: {diagram_id}")
                    return None
            else:
                # Read diagrams with optional filters
                where_conditions = []
                params = []
                
                if package_id is not None:
                    where_conditions.append("package_id = %s")
                    params.append(package_id)
                
                if diagram_type:
                    where_conditions.append("diagram_type = %s")
                    params.append(diagram_type)
                
                where_clause = ""
                if where_conditions:
                    where_clause = "WHERE " + " AND ".join(where_conditions)
                
                select_sql = f"""
                SELECT diagram_id, package_id, parentid, diagram_type, name, version, 
                    author, showdetails, notes, stereotype, attpub, attpri, attpro, 
                    orientation, cx, cy, scale, createddate, modifieddate, htmlpath, 
                    showforeign, showborder, showpackagecontents, pdata, locked, ea_guid, 
                    tpos, swimlanes, styleex
                FROM public.t_diagram
                {where_clause}
                ORDER BY createddate DESC
                """
                
                cursor.execute(select_sql, params)
                results = cursor.fetchall()
                
                diagrams = []
                for result in results:
                    diagram = self._build_diagram_dict(result)
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
            check_sql = "SELECT diagram_id FROM public.t_diagram WHERE diagram_id = %s"
            cursor.execute(check_sql, (diagram_id,))
            if not cursor.fetchone():
                print(f"Diagram not found: {diagram_id}")
                return None
            
            # Build update query dynamically
            update_fields = []
            params = []
            
            # Define all updatable fields
            updatable_fields = [
                'package_id', 'parentid', 'diagram_type', 'name', 'version', 'author',
                'showdetails', 'notes', 'stereotype', 'attpub', 'attpri', 'attpro',
                'orientation', 'cx', 'cy', 'scale', 'htmlpath', 'showforeign', 'showborder',
                'showpackagecontents', 'pdata', 'locked', 'ea_guid', 'tpos', 'swimlanes', 'styleex'
            ]
            
            for field in updatable_fields:
                if field in update_data and update_data[field] is not None:
                    update_fields.append(f"{field} = %s")
                    params.append(update_data[field])
            
            if not update_fields:
                print("No valid fields to update")
                return None
            
            # Add modifieddate timestamp
            update_fields.append("modifieddate = CURRENT_TIMESTAMP")
            params.append(diagram_id)
            
            update_sql = f"""
            UPDATE public.t_diagram 
            SET {', '.join(update_fields)}
            WHERE diagram_id = %s
            RETURNING diagram_id, package_id, parentid, diagram_type, name, version, 
                author, showdetails, notes, stereotype, attpub, attpri, attpro, 
                orientation, cx, cy, scale, createddate, modifieddate, htmlpath, 
                showforeign, showborder, showpackagecontents, pdata, locked, ea_guid, 
                tpos, swimlanes, styleex
            """
            
            cursor.execute(update_sql, params)
            result = cursor.fetchone()
            conn.commit()
            
            diagram = self._build_diagram_dict(result)
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
            check_sql = "SELECT diagram_id FROM public.t_diagram WHERE diagram_id = %s"
            cursor.execute(check_sql, (diagram_id,))
            if not cursor.fetchone():
                print(f"Diagram not found: {diagram_id}")
                return False
            
            # Delete the diagram
            delete_sql = "DELETE FROM public.t_diagram WHERE diagram_id = %s"
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
    
    def _build_diagram_dict(self, result):
        """Helper method to build diagram dictionary from database result"""
        return {
            'diagram_id': result[0],
            'package_id': result[1],
            'parentid': result[2],
            'diagram_type': result[3],
            'name': result[4],
            'version': result[5],
            'author': result[6],
            'showdetails': result[7],
            'notes': result[8],
            'stereotype': result[9],
            'attpub': result[10],
            'attpri': result[11],
            'attpro': result[12],
            'orientation': result[13],
            'cx': result[14],
            'cy': result[15],
            'scale': result[16],
            'createddate': result[17].isoformat() if result[17] else None,
            'modifieddate': result[18].isoformat() if result[18] else None,
            'htmlpath': result[19],
            'showforeign': result[20],
            'showborder': result[21],
            'showpackagecontents': result[22],
            'pdata': result[23],
            'locked': result[24],
            'ea_guid': result[25],
            'tpos': result[26],
            'swimlanes': result[27],
            'styleex': result[28]
        } 