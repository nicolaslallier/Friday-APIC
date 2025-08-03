# PowerShell script to test the enhanced health check
param(
    [string]$BaseUrl = "https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net"
)

Write-Host "🏥 Testing Enhanced Health Check" -ForegroundColor Green
Write-Host "📍 Base URL: $BaseUrl" -ForegroundColor Cyan
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/health" -Method GET
    Write-Host "✅ Health Check successful!" -ForegroundColor Green
    Write-Host "   Status: $($response.status)" -ForegroundColor White
    Write-Host "   Service: $($response.service)" -ForegroundColor White
    Write-Host "   Version: $($response.version)" -ForegroundColor White
    Write-Host "   Timestamp: $($response.timestamp)" -ForegroundColor White
    
    Write-Host ""
    Write-Host "🔍 Database Information:" -ForegroundColor Yellow
    if ($response.checks.database.status -eq "connected") {
        Write-Host "   ✅ Database Status: $($response.checks.database.status)" -ForegroundColor Green
        Write-Host "   📊 Current Database: $($response.checks.database.database_info.current_database)" -ForegroundColor White
        Write-Host "   🔢 PostgreSQL Version: $($response.checks.database.database_info.version)" -ForegroundColor White
        Write-Host "   📋 Available Databases: $($response.checks.database.database_info.available_databases -join ', ')" -ForegroundColor White
        Write-Host "   📁 Schemas: $($response.checks.database.database_info.schemas -join ', ')" -ForegroundColor White
        
        Write-Host ""
        Write-Host "📋 Tables in Public Schema:" -ForegroundColor Yellow
        foreach ($table in $response.checks.database.tables_info.public_schema_tables) {
            Write-Host "   • $($table.name) ($($table.type))" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "📊 t_diagram Table Details:" -ForegroundColor Yellow
        Write-Host "   📈 Row Count: $($response.checks.database.table_count)" -ForegroundColor White
        if ($response.checks.database.tables_info.t_diagram_size) {
            Write-Host "   💾 Total Size: $($response.checks.database.tables_info.t_diagram_size.total_size)" -ForegroundColor White
            Write-Host "   📄 Table Size: $($response.checks.database.tables_info.t_diagram_size.table_size)" -ForegroundColor White
            Write-Host "   🔍 Index Size: $($response.checks.database.tables_info.t_diagram_size.index_size)" -ForegroundColor White
        }
        
        Write-Host ""
        Write-Host "🏗️  t_diagram Table Structure:" -ForegroundColor Yellow
        foreach ($column in $response.checks.database.tables_info.t_diagram_structure) {
            $nullable = if ($column.is_nullable -eq "YES") { "NULL" } else { "NOT NULL" }
            $default = if ($column.default_value) { " DEFAULT $($column.default_value)" } else { "" }
            Write-Host "   • $($column.column_name): $($column.data_type) $nullable$default" -ForegroundColor White
        }
        
        if ($response.checks.database.sample_data) {
            Write-Host ""
            Write-Host "📝 Sample Data:" -ForegroundColor Yellow
            Write-Host "   • Diagram ID: $($response.checks.database.sample_data.diagram_id)" -ForegroundColor White
            Write-Host "   • Name: $($response.checks.database.sample_data.name)" -ForegroundColor White
        }
        
    } else {
        Write-Host "   ❌ Database Status: $($response.checks.database.status)" -ForegroundColor Red
        Write-Host "   🚨 Error: $($response.checks.database.error)" -ForegroundColor Red
        
        if ($response.checks.database.detailed_errors) {
            Write-Host ""
            Write-Host "🔍 Detailed Error Information:" -ForegroundColor Yellow
            foreach ($errorDetail in $response.checks.database.detailed_errors) {
                Write-Host "   • Type: $($errorDetail.type)" -ForegroundColor White
                Write-Host "   • Message: $($errorDetail.message)" -ForegroundColor White
                Write-Host "   • Timestamp: $($errorDetail.timestamp)" -ForegroundColor White
                if ($errorDetail.suggestion) {
                    Write-Host "   • Suggestion: $($errorDetail.suggestion)" -ForegroundColor Cyan
                }
                Write-Host ""
            }
        }
    }
    
    Write-Host ""
    Write-Host "💻 System Metrics:" -ForegroundColor Yellow
    Write-Host "   🧠 Memory Usage: $($response.system_metrics.memory.percent)%" -ForegroundColor White
    Write-Host "   💾 Memory Available: $([math]::Round($response.system_metrics.memory.available / 1MB, 2)) MB" -ForegroundColor White
    Write-Host "   🔥 CPU Usage: $($response.system_metrics.cpu.percent)%" -ForegroundColor White
    
    Write-Host ""
    Write-Host "📁 File System:" -ForegroundColor Yellow
    Write-Host "   📄 Health File Exists: $($response.checks.file_system.exists)" -ForegroundColor White
    Write-Host "   📍 Health File Path: $($response.checks.file_system.path)" -ForegroundColor White
    
} catch {
    Write-Host "❌ Health Check failed!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $errorContent = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($errorContent)
        $errorBody = $reader.ReadToEnd()
        Write-Host "   Response: $errorBody" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "🎉 Health Check Test Completed!" -ForegroundColor Green 