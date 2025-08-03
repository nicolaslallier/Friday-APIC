#!/usr/bin/env python3
"""
Basic PostgreSQL Database Query Script
Connects to the Architecture database and performs basic queries
"""

import psycopg
import sys
from datetime import datetime

# Database connection details
DB_CONFIG = {
    "host": "pg-frdypgdb-prd-cac.postgres.database.azure.com",
    "port": 5432,
    "dbname": "Architecture",
    "user": "nlallier",
    "password": "Moine101"
}

def test_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        # Create connection
        conn = psycopg.connect(**DB_CONFIG)
        print("✅ Database connection successful!")
        
        # Get database info
        cursor = conn.cursor()
        cursor.execute("SELECT current_database(), version()")
        db_info = cursor.fetchone()
        print(f"📊 Connected to database: {db_info[0]}")
        print(f"📊 PostgreSQL version: {db_info[1]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def list_databases():
    """List all available databases"""
    print("\n📋 Listing all databases...")
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false")
        databases = cursor.fetchall()
        
        print("Available databases:")
        for db in databases:
            print(f"  • {db[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error listing databases: {str(e)}")

def list_schemas():
    """List all schemas in the current database"""
    print("\n📋 Listing all schemas...")
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("SELECT schema_name FROM information_schema.schemata")
        schemas = cursor.fetchall()
        
        print("Available schemas:")
        for schema in schemas:
            print(f"  • {schema[0]}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error listing schemas: {str(e)}")

def list_tables():
    """List all tables in the public schema"""
    print("\n📋 Listing all tables in public schema...")
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        
        if tables:
            print("Tables in public schema:")
            for table in tables:
                print(f"  • {table[0]} ({table[1]})")
        else:
            print("No tables found in public schema")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error listing tables: {str(e)}")

def get_table_info(table_name):
    """Get detailed information about a specific table"""
    print(f"\n📋 Getting information for table: {table_name}")
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Get table structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_schema = 'public' AND table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        if columns:
            print(f"Table structure for '{table_name}':")
            print(f"{'Column Name':<20} {'Data Type':<15} {'Nullable':<10} {'Default'}")
            print("-" * 60)
            for col in columns:
                nullable = "YES" if col[2] == "YES" else "NO"
                default = col[3] if col[3] else "NULL"
                print(f"{col[0]:<20} {col[1]:<15} {nullable:<10} {default}")
        else:
            print(f"Table '{table_name}' not found or no columns")
        
        # Get row count
        cursor.execute(f"SELECT COUNT(*) FROM public.{table_name}")
        count = cursor.fetchone()[0]
        print(f"\nTotal rows in {table_name}: {count}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error getting table info: {str(e)}")

def sample_query(table_name, limit=5):
    """Run a sample SELECT query on a table"""
    print(f"\n🔍 Running sample query on table: {table_name}")
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute(f"SELECT * FROM public.{table_name} LIMIT %s", (limit,))
        rows = cursor.fetchall()
        
        if rows:
            # Get column names
            column_names = [desc[0] for desc in cursor.description]
            print(f"Columns: {', '.join(column_names)}")
            print(f"Sample data (first {len(rows)} rows):")
            print("-" * 80)
            
            for i, row in enumerate(rows, 1):
                print(f"Row {i}: {row}")
        else:
            print(f"No data found in table '{table_name}'")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error running sample query: {str(e)}")

def main():
    """Main function to run all database operations"""
    print("🚀 PostgreSQL Database Query Script")
    print("=" * 50)
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Connecting to: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}")
    print()
    
    # Test connection first
    if not test_connection():
        print("❌ Cannot proceed without database connection")
        sys.exit(1)
    
    # List databases
    list_databases()
    
    # List schemas
    list_schemas()
    
    # List tables
    list_tables()
    
    # If there are tables, get info for the first one
    try:
        conn = psycopg.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name 
            LIMIT 1
        """)
        first_table = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if first_table:
            table_name = first_table[0]
            get_table_info(table_name)
            sample_query(table_name)
        
    except Exception as e:
        print(f"❌ Error getting first table: {str(e)}")
    
    print("\n✅ Database query script completed!")

if __name__ == "__main__":
    main() 