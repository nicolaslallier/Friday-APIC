import os
import logging
from typing import List, Dict, Optional
from datetime import datetime

class ApplicationFileManager:
    """Manages tab-delimited application files"""
    
    def __init__(self, mount_path: str = "/func1"):
        print(f"📁 [FILE MANAGER] Initializing with mount path: {mount_path}")
        self.mount_path = mount_path
        self.applications_file = os.path.join(mount_path, "applications.txt")
        print(f"📄 [FILE MANAGER] Applications file path: {self.applications_file}")
        self.ensure_directory_exists()
        self.ensure_file_exists()
    
    def ensure_directory_exists(self):
        """Ensure the mount directory exists"""
        print(f"📁 [FILE MANAGER] Checking if directory exists: {self.mount_path}")
        if not os.path.exists(self.mount_path):
            print(f"📁 [FILE MANAGER] Creating directory: {self.mount_path}")
            os.makedirs(self.mount_path, exist_ok=True)
            logging.info(f'Created mount path: {self.mount_path}')
        else:
            print(f"✅ [FILE MANAGER] Directory already exists: {self.mount_path}")
    
    def ensure_file_exists(self):
        """Ensure the applications file exists with headers"""
        print(f"📄 [FILE MANAGER] Checking if file exists: {self.applications_file}")
        if not os.path.exists(self.applications_file):
            print(f"📄 [FILE MANAGER] Creating applications file with headers")
            headers = [
                "id",
                "name", 
                "description",
                "version",
                "status",
                "created_at",
                "updated_at",
                "owner",
                "category"
            ]
            with open(self.applications_file, 'w', encoding='utf-8') as f:
                f.write('\t'.join(headers) + '\n')
            logging.info(f'Created applications file: {self.applications_file}')
            print(f"✅ [FILE MANAGER] Created applications file: {self.applications_file}")
        else:
            print(f"✅ [FILE MANAGER] Applications file already exists: {self.applications_file}")
    
    def read_all_applications(self) -> List[Dict]:
        """Read all applications from the file"""
        print(f"📖 [FILE MANAGER] Reading all applications from: {self.applications_file}")
        applications = []
        try:
            with open(self.applications_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                print(f"📊 [FILE MANAGER] Found {len(lines)} lines in file")
                if len(lines) <= 1:  # Only headers or empty file
                    print("📊 [FILE MANAGER] File is empty or has only headers")
                    return applications
                
                headers = lines[0].strip().split('\t')
                print(f"📋 [FILE MANAGER] Headers: {headers}")
                for line in lines[1:]:
                    if line.strip():
                        values = line.strip().split('\t')
                        app_dict = dict(zip(headers, values))
                        applications.append(app_dict)
                
                print(f"📊 [FILE MANAGER] Read {len(applications)} applications")
            
            return applications
        except Exception as e:
            print(f"💥 [FILE MANAGER] Error reading applications: {str(e)}")
            logging.error(f'Error reading applications: {str(e)}')
            return []
    
    def find_application_by_id(self, app_id: str) -> Optional[Dict]:
        """Find an application by ID"""
        applications = self.read_all_applications()
        for app in applications:
            if app.get('id') == app_id:
                return app
        return None
    
    def create_application(self, app_data: Dict) -> Dict:
        """Create a new application"""
        print(f"➕ [FILE MANAGER] Creating new application with data: {app_data}")
        try:
            # Generate unique ID
            app_id = f"app_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
            current_time = datetime.utcnow().isoformat() + "Z"
            print(f"🆔 [FILE MANAGER] Generated ID: {app_id}")
            
            # Prepare application data
            new_app = {
                'id': app_id,
                'name': app_data.get('name', ''),
                'description': app_data.get('description', ''),
                'version': app_data.get('version', '1.0.0'),
                'status': app_data.get('status', 'active'),
                'created_at': current_time,
                'updated_at': current_time,
                'owner': app_data.get('owner', ''),
                'category': app_data.get('category', '')
            }
            print(f"📝 [FILE MANAGER] Prepared application data: {new_app}")
            
            # Append to file
            print(f"💾 [FILE MANAGER] Appending to file: {self.applications_file}")
            with open(self.applications_file, 'a', encoding='utf-8') as f:
                line = '\t'.join(str(new_app.get(key, '')) for key in [
                    'id', 'name', 'description', 'version', 'status', 
                    'created_at', 'updated_at', 'owner', 'category'
                ])
                f.write(line + '\n')
            
            print(f"✅ [FILE MANAGER] Successfully created application with ID: {app_id}")
            logging.info(f'Created application with ID: {app_id}')
            return new_app
            
        except Exception as e:
            print(f"💥 [FILE MANAGER] Error creating application: {str(e)}")
            logging.error(f'Error creating application: {str(e)}')
            raise
    
    def update_application(self, app_id: str, app_data: Dict) -> Optional[Dict]:
        """Update an existing application"""
        try:
            applications = self.read_all_applications()
            updated = False
            current_time = datetime.utcnow().isoformat() + "Z"
            
            # Find and update the application
            for app in applications:
                if app.get('id') == app_id:
                    app.update(app_data)
                    app['updated_at'] = current_time
                    updated = True
                    break
            
            if not updated:
                return None
            
            # Rewrite the entire file
            with open(self.applications_file, 'w', encoding='utf-8') as f:
                # Write headers
                headers = [
                    "id", "name", "description", "version", "status",
                    "created_at", "updated_at", "owner", "category"
                ]
                f.write('\t'.join(headers) + '\n')
                
                # Write all applications
                for app in applications:
                    line = '\t'.join(str(app.get(key, '')) for key in headers)
                    f.write(line + '\n')
            
            logging.info(f'Updated application with ID: {app_id}')
            return self.find_application_by_id(app_id)
            
        except Exception as e:
            logging.error(f'Error updating application: {str(e)}')
            raise
    
    def delete_application(self, app_id: str) -> bool:
        """Delete an application by ID"""
        try:
            applications = self.read_all_applications()
            original_count = len(applications)
            
            # Filter out the application to delete
            applications = [app for app in applications if app.get('id') != app_id]
            
            if len(applications) == original_count:
                return False  # Application not found
            
            # Rewrite the file without the deleted application
            with open(self.applications_file, 'w', encoding='utf-8') as f:
                # Write headers
                headers = [
                    "id", "name", "description", "version", "status",
                    "created_at", "updated_at", "owner", "category"
                ]
                f.write('\t'.join(headers) + '\n')
                
                # Write remaining applications
                for app in applications:
                    line = '\t'.join(str(app.get(key, '')) for key in headers)
                    f.write(line + '\n')
            
            logging.info(f'Deleted application with ID: {app_id}')
            return True
            
        except Exception as e:
            logging.error(f'Error deleting application: {str(e)}')
            raise 