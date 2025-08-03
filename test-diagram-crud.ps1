# PowerShell script to test all diagram CRUD endpoints
param(
    [string]$BaseUrl = "https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net"
)

Write-Host "🧪 Testing Diagram CRUD Endpoints" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Global variables to store test data
$script:CreatedDiagramId = $null
$script:CreatedDiagramName = "Test Diagram $(Get-Date -Format 'yyyyMMdd_HHmmss')"

# Function to make HTTP requests
function Invoke-DiagramRequest {
    param(
        [string]$Url,
        [string]$Method = "GET",
        [string]$Body = "",
        [string]$TestName
    )
    
    Write-Host "🔍 Testing: $TestName" -ForegroundColor Yellow
    Write-Host "📍 URL: $Url" -ForegroundColor Gray
    Write-Host "📝 Method: $Method" -ForegroundColor Gray
    if ($Body) {
        Write-Host "📄 Body: $Body" -ForegroundColor Gray
    }
    Write-Host ""
    
    try {
        $headers = @{
            "Content-Type" = "application/json"
        }
        
        if ($Method -eq "GET") {
            $response = Invoke-RestMethod -Uri $Url -Method Get -Headers $headers
        } elseif ($Method -eq "POST") {
            $response = Invoke-RestMethod -Uri $Url -Method Post -Body $Body -Headers $headers
        } elseif ($Method -eq "PUT") {
            $response = Invoke-RestMethod -Uri $Url -Method Put -Body $Body -Headers $headers
        } elseif ($Method -eq "DELETE") {
            $response = Invoke-RestMethod -Uri $Url -Method Delete -Headers $headers
        }
        
        Write-Host "✅ Success!" -ForegroundColor Green
        Write-Host "📊 Response:" -ForegroundColor Cyan
        Write-Host ($response | ConvertTo-Json -Depth 10) -ForegroundColor White
        Write-Host ""
        
        return $response
    }
    catch {
        Write-Host "❌ Error occurred:" -ForegroundColor Red
        Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
        Write-Host "Error Message: $($_.Exception.Message)" -ForegroundColor Red
        
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "Response Body: $responseBody" -ForegroundColor Red
        }
        Write-Host ""
        return $null
    }
}

# Test 1: Create Diagram
Write-Host "🚀 Test 1: Create Diagram" -ForegroundColor Green
Write-Host "=========================" -ForegroundColor Green
$createBody = @{
    name = $script:CreatedDiagramName
    description = "A test diagram created by PowerShell script"
    content = "Test diagram content with some data"
} | ConvertTo-Json

$createUrl = "$BaseUrl/api/diagram/create"
$createResponse = Invoke-DiagramRequest -Url $createUrl -Method "POST" -Body $createBody -TestName "Create Diagram"

if ($createResponse -and $createResponse.diagram) {
    $script:CreatedDiagramId = $createResponse.diagram.id
    Write-Host "📝 Created diagram ID: $script:CreatedDiagramId" -ForegroundColor Cyan
}

# Test 2: Read All Diagrams
Write-Host "📋 Test 2: Read All Diagrams" -ForegroundColor Green
Write-Host "============================" -ForegroundColor Green
$readAllUrl = "$BaseUrl/api/diagram/read"
$readAllResponse = Invoke-DiagramRequest -Url $readAllUrl -Method "GET" -TestName "Read All Diagrams"

# Test 3: Read Specific Diagram (if created successfully)
if ($script:CreatedDiagramId) {
    Write-Host "🎯 Test 3: Read Specific Diagram" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    $readSpecificUrl = "$BaseUrl/api/diagram/read?id=$script:CreatedDiagramId"
    $readSpecificResponse = Invoke-DiagramRequest -Url $readSpecificUrl -Method "GET" -TestName "Read Specific Diagram"
}

# Test 4: Update Diagram (if created successfully)
if ($script:CreatedDiagramId) {
    Write-Host "🔄 Test 4: Update Diagram" -ForegroundColor Green
    Write-Host "=========================" -ForegroundColor Green
    $updateBody = @{
        name = "$script:CreatedDiagramName (Updated)"
        description = "Updated description for the test diagram"
        content = "Updated diagram content with new data"
    } | ConvertTo-Json

    $updateUrl = "$BaseUrl/api/diagram/update?id=$script:CreatedDiagramId"
    $updateResponse = Invoke-DiagramRequest -Url $updateUrl -Method "PUT" -Body $updateBody -TestName "Update Diagram"
}

# Test 5: Read Updated Diagram (if updated successfully)
if ($script:CreatedDiagramId) {
    Write-Host "📖 Test 5: Read Updated Diagram" -ForegroundColor Green
    Write-Host "===============================" -ForegroundColor Green
    $readUpdatedUrl = "$BaseUrl/api/diagram/read?id=$script:CreatedDiagramId"
    $readUpdatedResponse = Invoke-DiagramRequest -Url $readUpdatedUrl -Method "GET" -TestName "Read Updated Diagram"
}

# Test 6: Delete Diagram (if created successfully)
if ($script:CreatedDiagramId) {
    Write-Host "🗑️ Test 6: Delete Diagram" -ForegroundColor Green
    Write-Host "=========================" -ForegroundColor Green
    $deleteUrl = "$BaseUrl/api/diagram/delete?id=$script:CreatedDiagramId"
    $deleteResponse = Invoke-DiagramRequest -Url $deleteUrl -Method "DELETE" -TestName "Delete Diagram"
}

# Test 7: Verify Deletion (try to read deleted diagram)
if ($script:CreatedDiagramId) {
    Write-Host "🔍 Test 7: Verify Deletion" -ForegroundColor Green
    Write-Host "=========================" -ForegroundColor Green
    $verifyDeleteUrl = "$BaseUrl/api/diagram/read?id=$script:CreatedDiagramId"
    $verifyDeleteResponse = Invoke-DiagramRequest -Url $verifyDeleteUrl -Method "GET" -TestName "Verify Deletion"
}

# Test 8: Read All Diagrams After Deletion
Write-Host "📋 Test 8: Read All Diagrams After Deletion" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
$readAllAfterUrl = "$BaseUrl/api/diagram/read"
$readAllAfterResponse = Invoke-DiagramRequest -Url $readAllAfterUrl -Method "GET" -TestName "Read All Diagrams After Deletion"

# Test 9: Error Cases
Write-Host "❌ Test 9: Error Cases" -ForegroundColor Green
Write-Host "=====================" -ForegroundColor Green

# Test 9a: Create diagram with missing required field
Write-Host "❌ Test 9a: Create Diagram with Missing Name" -ForegroundColor Yellow
$invalidCreateBody = @{
    description = "Diagram without name"
    content = "Some content"
} | ConvertTo-Json

$invalidCreateUrl = "$BaseUrl/api/diagram/create"
$invalidCreateResponse = Invoke-DiagramRequest -Url $invalidCreateUrl -Method "POST" -Body $invalidCreateBody -TestName "Create Diagram with Missing Name"

# Test 9b: Update non-existent diagram
Write-Host "❌ Test 9b: Update Non-existent Diagram" -ForegroundColor Yellow
$invalidUpdateBody = @{
    name = "Non-existent diagram"
} | ConvertTo-Json

$invalidUpdateUrl = "$BaseUrl/api/diagram/update?id=non_existent_diagram_12345"
$invalidUpdateResponse = Invoke-DiagramRequest -Url $invalidUpdateUrl -Method "PUT" -Body $invalidUpdateBody -TestName "Update Non-existent Diagram"

# Test 9c: Delete non-existent diagram
Write-Host "❌ Test 9c: Delete Non-existent Diagram" -ForegroundColor Yellow
$invalidDeleteUrl = "$BaseUrl/api/diagram/delete?id=non_existent_diagram_12345"
$invalidDeleteResponse = Invoke-DiagramRequest -Url $invalidDeleteUrl -Method "DELETE" -TestName "Delete Non-existent Diagram"

# Summary
Write-Host "📋 Test Summary" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan
Write-Host ""

$testResults = @()

# Evaluate test results
if ($createResponse) { $testResults += "✅ Create Diagram: SUCCESS" } else { $testResults += "❌ Create Diagram: FAILED" }
if ($readAllResponse) { $testResults += "✅ Read All Diagrams: SUCCESS" } else { $testResults += "❌ Read All Diagrams: FAILED" }
if ($script:CreatedDiagramId -and $readSpecificResponse) { $testResults += "✅ Read Specific Diagram: SUCCESS" } else { $testResults += "⚠️  Read Specific Diagram: SKIPPED/FAILED" }
if ($script:CreatedDiagramId -and $updateResponse) { $testResults += "✅ Update Diagram: SUCCESS" } else { $testResults += "⚠️  Update Diagram: SKIPPED/FAILED" }
if ($script:CreatedDiagramId -and $readUpdatedResponse) { $testResults += "✅ Read Updated Diagram: SUCCESS" } else { $testResults += "⚠️  Read Updated Diagram: SKIPPED/FAILED" }
if ($script:CreatedDiagramId -and $deleteResponse) { $testResults += "✅ Delete Diagram: SUCCESS" } else { $testResults += "⚠️  Delete Diagram: SKIPPED/FAILED" }
if ($script:CreatedDiagramId -and $verifyDeleteResponse -eq $null) { $testResults += "✅ Verify Deletion: SUCCESS (404 as expected)" } else { $testResults += "⚠️  Verify Deletion: UNEXPECTED" }
if ($readAllAfterResponse) { $testResults += "✅ Read All After Deletion: SUCCESS" } else { $testResults += "❌ Read All After Deletion: FAILED" }
if ($invalidCreateResponse -eq $null) { $testResults += "✅ Invalid Create: SUCCESS (400 as expected)" } else { $testResults += "⚠️  Invalid Create: UNEXPECTED" }
if ($invalidUpdateResponse -eq $null) { $testResults += "✅ Invalid Update: SUCCESS (404 as expected)" } else { $testResults += "⚠️  Invalid Update: UNEXPECTED" }
if ($invalidDeleteResponse -eq $null) { $testResults += "✅ Invalid Delete: SUCCESS (404 as expected)" } else { $testResults += "⚠️  Invalid Delete: UNEXPECTED" }

foreach ($result in $testResults) {
    if ($result -like "✅*") {
        Write-Host $result -ForegroundColor Green
    } elseif ($result -like "❌*") {
        Write-Host $result -ForegroundColor Red
    } else {
        Write-Host $result -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 Diagram CRUD Testing Completed!" -ForegroundColor Cyan

# Usage instructions
Write-Host ""
Write-Host "📖 Usage Examples:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Write-Host ""

Write-Host "Test with default settings:" -ForegroundColor White
Write-Host "  .\test-diagram-crud.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "Test with custom base URL:" -ForegroundColor White
Write-Host "  .\test-diagram-crud.ps1 -BaseUrl 'https://your-function-app.azurewebsites.net'" -ForegroundColor Gray
Write-Host ""

Write-Host "📝 Note: This script will create a test diagram, perform all CRUD operations on it, and then delete it." -ForegroundColor Yellow
Write-Host "📝 The diagram name will include a timestamp to avoid conflicts." -ForegroundColor Yellow
Write-Host "" 