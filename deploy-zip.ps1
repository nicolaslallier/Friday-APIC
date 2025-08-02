# Azure Functions Zip Deployment Script
# This script creates a zip file and deploys it to Azure Functions

param(
    [string]$FunctionAppName = "func-frdyapic-prd-cac",
    [string]$ResourceGroup = "rg-Friday-prd-cac",
    [string]$ZipFileName = "friday-apic-deployment.zip"
)

Write-Host "🚀 Starting Azure Functions Zip Deployment..." -ForegroundColor Green
Write-Host "Function App: $FunctionAppName" -ForegroundColor Yellow
Write-Host "Resource Group: $ResourceGroup" -ForegroundColor Yellow
Write-Host "Zip File: $ZipFileName" -ForegroundColor Yellow

# Check if Azure CLI is installed
try {
    $azVersion = az --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Azure CLI is installed" -ForegroundColor Green
    } else {
        Write-Host "❌ Azure CLI not found. Please install it first:" -ForegroundColor Red
        Write-Host "   winget install Microsoft.AzureCLI" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Azure CLI not found. Please install it first:" -ForegroundColor Red
    Write-Host "   winget install Microsoft.AzureCLI" -ForegroundColor Yellow
    exit 1
}

# Login to Azure
Write-Host "🔐 Logging into Azure..." -ForegroundColor Yellow
az login

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to login to Azure" -ForegroundColor Red
    exit 1
}

# List available resources
Write-Host "📋 Checking available resources..." -ForegroundColor Yellow
Write-Host "Resource Groups:" -ForegroundColor Cyan
az group list --output table

Write-Host "Function Apps:" -ForegroundColor Cyan
az functionapp list --output table

# Create deployment zip file
Write-Host "📦 Creating deployment zip file..." -ForegroundColor Yellow

# Remove existing zip file if it exists
if (Test-Path $ZipFileName) {
    Remove-Item $ZipFileName -Force
    Write-Host "   Removed existing zip file" -ForegroundColor Gray
}

# Create zip file with required files
$filesToZip = @(
    "health_check",
    "hello_world", 
    "host.json",
    "local.settings.json",
    "requirements.txt"
)

Write-Host "   Adding files to zip:" -ForegroundColor Gray
foreach ($file in $filesToZip) {
    if (Test-Path $file) {
        Write-Host "     ✅ $file" -ForegroundColor Gray
    } else {
        Write-Host "     ❌ $file (not found)" -ForegroundColor Red
    }
}

# Create the zip file
try {
    Compress-Archive -Path $filesToZip -DestinationPath $ZipFileName -Force
    Write-Host "✅ Zip file created successfully: $ZipFileName" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to create zip file: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Deploy using Azure CLI
Write-Host "📤 Deploying to Azure Functions..." -ForegroundColor Yellow
az functionapp deployment source config-zip --resource-group $ResourceGroup --name $FunctionAppName --src $ZipFileName --build-remote true

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host "🌐 Your function app is available at:" -ForegroundColor Cyan
    Write-Host "   https://$FunctionAppName.azurewebsites.net" -ForegroundColor White
    
    Write-Host "📋 Available endpoints:" -ForegroundColor Cyan
    Write-Host "   Health Check: https://$FunctionAppName.azurewebsites.net/health" -ForegroundColor White
    Write-Host "   Hello World: https://$FunctionAppName.azurewebsites.net/hello" -ForegroundColor White
    
    # Clean up zip file
    if (Test-Path $ZipFileName) {
        Remove-Item $ZipFileName -Force
        Write-Host "🧹 Cleaned up temporary zip file" -ForegroundColor Gray
    }
} else {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "   Please check the error messages above" -ForegroundColor Yellow
    Write-Host "   Zip file preserved for debugging: $ZipFileName" -ForegroundColor Yellow
    exit 1
}

Write-Host "🎉 Zip deployment completed successfully!" -ForegroundColor Green 