# Deploy Azure Function App using Kudu API
param(
    [string]$ResourceGroup = "rg-Friday-prd-cac",
    [string]$FunctionAppName = "func-frdyapic-prd-cac"
)

Write-Host "🚀 Deploying to Azure Function App: $FunctionAppName" -ForegroundColor Green

# Get publishing credentials
Write-Host "📋 Getting publishing credentials..." -ForegroundColor Yellow
$credentials = az functionapp deployment list-publishing-credentials --resource-group $ResourceGroup --name $FunctionAppName | ConvertFrom-Json

$username = $credentials.publishingUserName
$password = $credentials.publishingPassword
$scmUri = $credentials.scmUri

Write-Host "✅ Publishing credentials obtained" -ForegroundColor Green

# Create base64 credentials for Basic Auth
$base64AuthInfo = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes(("$username`:$password")))

# Kudu API base URL
$kuduApiUrl = "https://$FunctionAppName-ffgrbhfrfxatbqgy.scm.canadacentral-01.azurewebsites.net/api"

# Function to upload file to Kudu
function Upload-FileToKudu {
    param(
        [string]$FilePath,
        [string]$RemotePath
    )
    
    Write-Host "📤 Uploading $FilePath to $RemotePath..." -ForegroundColor Yellow
    
    $fileContent = [System.IO.File]::ReadAllBytes($FilePath)
    $headers = @{
        "Authorization" = "Basic $base64AuthInfo"
        "Content-Type" = "application/octet-stream"
    }
    
    $uploadUrl = "$kuduApiUrl/vfs/$RemotePath"
    
    try {
        $response = Invoke-RestMethod -Uri $uploadUrl -Method PUT -Headers $headers -Body $fileContent
        Write-Host "✅ Successfully uploaded $FilePath" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Failed to upload $FilePath : $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Upload function app files
Write-Host "📁 Uploading function app files..." -ForegroundColor Yellow

# Upload main function app file
Upload-FileToKudu -FilePath "function_app.py" -RemotePath "site/wwwroot/function_app.py"

# Upload host.json
Upload-FileToKudu -FilePath "host.json" -RemotePath "site/wwwroot/host.json"

# Upload requirements.txt
Upload-FileToKudu -FilePath "requirements.txt" -RemotePath "site/wwwroot/requirements.txt"

# Upload local.settings.json (for reference)
Upload-FileToKudu -FilePath "local.settings.json" -RemotePath "site/wwwroot/local.settings.json"

Write-Host "🎉 Deployment completed!" -ForegroundColor Green
Write-Host "🌐 Your function app should be available at: https://$FunctionAppName-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net" -ForegroundColor Cyan
Write-Host "🔍 Health check endpoints:" -ForegroundColor Cyan
Write-Host "   - Basic: https://$FunctionAppName-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/health" -ForegroundColor White
Write-Host "   - Detailed: https://$FunctionAppName-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api/health/detailed" -ForegroundColor White 