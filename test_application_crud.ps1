# Application CRUD Testing Script
# Tests all CRUD operations for the application functions

$baseUrl = "https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net/api"

Write-Host "🚀 Testing Application CRUD Functions" -ForegroundColor Green
Write-Host "Base URL: $baseUrl" -ForegroundColor Yellow
Write-Host ""

# Test 1: READ (should return empty list initially)
Write-Host "📖 Test 1: Reading all applications (should be empty initially)" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/read" -Method GET
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 2: CREATE first application
Write-Host "➕ Test 2: Creating first application" -ForegroundColor Cyan
$app1Data = @{
    name = "Test Web Application"
    description = "A test web application for CRUD testing"
    version = "1.0.0"
    status = "active"
    owner = "Test User"
    category = "web"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/create" -Method POST -Body $app1Data -ContentType "application/json"
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
    
    # Extract the created application ID for later tests
    $responseObj = $response.Content | ConvertFrom-Json
    $app1Id = $responseObj.application.id
    Write-Host "🆔 Created Application ID: $app1Id" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 3: CREATE second application
Write-Host "➕ Test 3: Creating second application" -ForegroundColor Cyan
$app2Data = @{
    name = "Mobile App"
    description = "A mobile application for testing"
    version = "2.0.0"
    status = "active"
    owner = "Mobile Developer"
    category = "mobile"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/create" -Method POST -Body $app2Data -ContentType "application/json"
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
    
    # Extract the second application ID
    $responseObj = $response.Content | ConvertFrom-Json
    $app2Id = $responseObj.application.id
    Write-Host "🆔 Created Application ID: $app2Id" -ForegroundColor Yellow
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 4: READ all applications
Write-Host "📖 Test 4: Reading all applications" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/read" -Method GET
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 5: READ specific application by ID
Write-Host "📖 Test 5: Reading specific application by ID" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/read?id=$app1Id" -Method GET
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 6: READ applications filtered by category
Write-Host "📖 Test 6: Reading applications filtered by category" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/read?category=web" -Method GET
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 7: UPDATE application
Write-Host "✏️ Test 7: Updating application" -ForegroundColor Cyan
$updateData = @{
    name = "Updated Web Application"
    description = "Updated description for testing"
    version = "1.1.0"
    status = "inactive"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/update?id=$app1Id" -Method PUT -Body $updateData -ContentType "application/json"
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 8: READ updated application
Write-Host "📖 Test 8: Reading updated application" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/read?id=$app1Id" -Method GET
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 9: DELETE application
Write-Host "🗑️ Test 9: Deleting application" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/delete?id=$app1Id" -Method DELETE
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

# Test 10: READ all applications after deletion
Write-Host "📖 Test 10: Reading all applications after deletion" -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/application/read" -Method GET
    Write-Host "✅ Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "📄 Response: $($response.Content)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
}
Write-Host ""

Write-Host "🎉 CRUD Testing Complete!" -ForegroundColor Green 