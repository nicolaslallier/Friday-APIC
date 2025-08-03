# PowerShell script to test the diagram_read endpoint
param(
    [string]$BaseUrl = "https://func-frdyapic-prd-cac-ffgrbhfrfxatbqgy.canadacentral-01.azurewebsites.net",
    [string]$DiagramId = ""
)

Write-Host "🧪 Testing Diagram Read Endpoint" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Function to make HTTP requests
function Invoke-DiagramRead {
    param(
        [string]$Url,
        [string]$TestName
    )
    
    Write-Host "🔍 Testing: $TestName" -ForegroundColor Yellow
    Write-Host "📍 URL: $Url" -ForegroundColor Gray
    Write-Host ""
    
    try {
        $response = Invoke-RestMethod -Uri $Url -Method Get -ContentType "application/json"
        
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

# Test 1: Read all diagrams
Write-Host "🚀 Test 1: Read All Diagrams" -ForegroundColor Green
Write-Host "=============================" -ForegroundColor Green
$allDiagramsUrl = "$BaseUrl/api/diagram/read"
$allDiagramsResponse = Invoke-DiagramRead -Url $allDiagramsUrl -TestName "Read All Diagrams"

# Test 2: Read specific diagram (if ID provided)
if ($DiagramId) {
    Write-Host "🎯 Test 2: Read Specific Diagram" -ForegroundColor Green
    Write-Host "=================================" -ForegroundColor Green
    $specificDiagramUrl = "$BaseUrl/api/diagram/read?id=$DiagramId"
    $specificDiagramResponse = Invoke-DiagramRead -Url $specificDiagramUrl -TestName "Read Specific Diagram"
}

# Test 3: Read non-existent diagram
Write-Host "❌ Test 3: Read Non-existent Diagram" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
$nonExistentUrl = "$BaseUrl/api/diagram/read?id=non_existent_diagram_12345"
$nonExistentResponse = Invoke-DiagramRead -Url $nonExistentUrl -TestName "Read Non-existent Diagram"

# Test 4: Read with empty ID parameter
Write-Host "🔍 Test 4: Read with Empty ID Parameter" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
$emptyIdUrl = "$BaseUrl/api/diagram/read?id="
$emptyIdResponse = Invoke-DiagramRead -Url $emptyIdUrl -TestName "Read with Empty ID Parameter"

# Summary
Write-Host "📋 Test Summary" -ForegroundColor Cyan
Write-Host "===============" -ForegroundColor Cyan
Write-Host ""

if ($allDiagramsResponse) {
    $diagramCount = if ($allDiagramsResponse.diagrams) { $allDiagramsResponse.diagrams.Count } else { 0 }
    Write-Host "✅ Read All Diagrams: SUCCESS ($diagramCount diagrams found)" -ForegroundColor Green
} else {
    Write-Host "❌ Read All Diagrams: FAILED" -ForegroundColor Red
}

if ($DiagramId) {
    if ($specificDiagramResponse) {
        Write-Host "✅ Read Specific Diagram: SUCCESS" -ForegroundColor Green
    } else {
        Write-Host "❌ Read Specific Diagram: FAILED" -ForegroundColor Red
    }
}

if ($nonExistentResponse -eq $null) {
    Write-Host "✅ Read Non-existent Diagram: SUCCESS (404 as expected)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Read Non-existent Diagram: UNEXPECTED RESPONSE" -ForegroundColor Yellow
}

if ($emptyIdResponse) {
    $emptyIdCount = if ($emptyIdResponse.diagrams) { $emptyIdResponse.diagrams.Count } else { 0 }
    Write-Host "✅ Read with Empty ID: SUCCESS ($emptyIdCount diagrams found)" -ForegroundColor Green
} else {
    Write-Host "❌ Read with Empty ID: FAILED" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 Diagram Read Testing Completed!" -ForegroundColor Cyan

# Usage instructions
Write-Host ""
Write-Host "📖 Usage Examples:" -ForegroundColor Yellow
Write-Host "==================" -ForegroundColor Yellow
Write-Host ""

Write-Host "Test with default settings:" -ForegroundColor White
Write-Host "  .\test-diagram-read.ps1" -ForegroundColor Gray
Write-Host ""

Write-Host "Test with custom base URL:" -ForegroundColor White
Write-Host "  .\test-diagram-read.ps1 -BaseUrl 'https://your-function-app.azurewebsites.net'" -ForegroundColor Gray
Write-Host ""

Write-Host "Test with specific diagram ID:" -ForegroundColor White
Write-Host "  .\test-diagram-read.ps1 -DiagramId 'diag_20240803_120000_123'" -ForegroundColor Gray
Write-Host ""

Write-Host "Test with both custom URL and diagram ID:" -ForegroundColor White
Write-Host "  .\test-diagram-read.ps1 -BaseUrl 'https://your-function-app.azurewebsites.net' -DiagramId 'diag_20240803_120000_123'" -ForegroundColor Gray
Write-Host "" 