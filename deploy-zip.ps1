# PowerShell script to create a zip file and deploy to Azure Functions
param(
    [string]$FunctionAppName = "func-frdyapic-prd-cac",
    [string]$ResourceGroup = "rg-Friday-prd-cac"
)

Write-Host "🚀 Starting deployment process..." -ForegroundColor Green

# List available resource groups and function apps for verification
Write-Host "📋 Available Resource Groups:" -ForegroundColor Yellow
az group list --query "[].name" -o table

Write-Host "📋 Available Function Apps:" -ForegroundColor Yellow
az functionapp list --resource-group $ResourceGroup --query "[].name" -o table

# Create a clean deployment directory
$deployDir = "deployment-temp"
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}
New-Item -ItemType Directory -Path $deployDir | Out-Null

# Define files and folders to include in the zip
$filesToZip = @(
    "health_check",
    "diagram_create",
    "diagram_read",
    "diagram_update",
    "diagram_delete",
    "shared",
    "test_simple",
    "host.json",
    "requirements.txt"
)

Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow

# Copy files to deployment directory
foreach ($item in $filesToZip) {
    if (Test-Path $item) {
        if (Test-Path $item -PathType Container) {
            # Copy directory
            Copy-Item -Path $item -Destination $deployDir -Recurse -Force
            Write-Host "  ✅ Copied directory: $item" -ForegroundColor Green
        } else {
            # Copy file
            Copy-Item -Path $item -Destination $deployDir -Force
            Write-Host "  ✅ Copied file: $item" -ForegroundColor Green
        }
    } else {
        Write-Host "  ⚠️  Warning: $item not found" -ForegroundColor Yellow
    }
}

# Create zip file
$zipFileName = "friday-apic-deployment.zip"
if (Test-Path $zipFileName) {
    Remove-Item $zipFileName -Force
}

Write-Host "🗜️  Creating zip file: $zipFileName" -ForegroundColor Yellow
Compress-Archive -Path "$deployDir\*" -DestinationPath $zipFileName -Force

# Verify zip contents
Write-Host "📋 Zip file contents:" -ForegroundColor Yellow
Expand-Archive -Path $zipFileName -DestinationPath "zip-contents-temp" -Force
Get-ChildItem -Path "zip-contents-temp" -Recurse | ForEach-Object { Write-Host "  📄 $($_.FullName.Replace('zip-contents-temp\', ''))" }
Remove-Item "zip-contents-temp" -Recurse -Force

# Deploy to Azure Functions
Write-Host "🚀 Deploying to Azure Functions..." -ForegroundColor Green
Write-Host "  📍 Function App: $FunctionAppName" -ForegroundColor Cyan
Write-Host "  📍 Resource Group: $ResourceGroup" -ForegroundColor Cyan

try {
    $deployResult = az functionapp deployment source config-zip --resource-group $ResourceGroup --name $FunctionAppName --src $zipFileName
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Deployment successful!" -ForegroundColor Green
        Write-Host ""
        Write-Host "🌐 Available endpoints:" -ForegroundColor Cyan
        Write-Host "  • Health Check: https://$FunctionAppName-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/health" -ForegroundColor White
        Write-Host "  • Create Diagram: https://$FunctionAppName-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/diagram/create" -ForegroundColor White
        Write-Host "  • Read Diagrams: https://$FunctionAppName-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/diagram/read" -ForegroundColor White
        Write-Host "  • Update Diagram: https://$FunctionAppName-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/diagram/update" -ForegroundColor White
        Write-Host "  • Delete Diagram: https://$FunctionAppName-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/diagram/delete" -ForegroundColor White
        Write-Host "  • Test Simple: https://$FunctionAppName-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/test-simple" -ForegroundColor White
        Write-Host ""
        Write-Host "🔧 Database: PostgreSQL connected to pg-frdypgdb-prd-cac.postgres.database.azure.com" -ForegroundColor Cyan
        Write-Host "📝 Note: Make sure to set the POSTGRES_PASSWORD environment variable in Azure Functions" -ForegroundColor Yellow
        Write-Host ""

    } else {
        Write-Host "❌ Deployment failed!" -ForegroundColor Red
        Write-Host "Error: $deployResult" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Deployment failed with exception: $($_.Exception.Message)" -ForegroundColor Red
}

# Cleanup
Write-Host "🧹 Cleaning up temporary files..." -ForegroundColor Yellow
if (Test-Path $deployDir) {
    Remove-Item $deployDir -Recurse -Force
}

Write-Host "🏁 Deployment process completed!" -ForegroundColor Green 