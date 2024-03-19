$hostname = hostname
$customerName = $hostname

# Gather package information
$packages = Get-Package -ProviderName Programs
$packageInfoArray = @()

foreach ($package in $packages) {
    $packageName = $package.Name
    $packageVersion = if ($package.Version) { $package.Version } else { "Unknown" }
    $packageInfo = @{
        Name = $packageName
        Version = $packageVersion
    }
    $packageInfoArray += $packageInfo
}

# Gather hotfix information
$hotfixes = Get-WmiObject -Class Win32_QuickFixEngineering | Sort-Object InstalledOn -Descending
$hotfixInfoArray = @()

foreach ($hotfix in $hotfixes) {
    $hotfixID = $hotfix.HotFixID
    $description = if ($hotfix.Description) { $hotfix.Description } else { "Unknown" }
    $installedOn = if ($hotfix.InstalledOn) { $hotfix.InstalledOn } else { "Unknown" }

    $hotfixInfo = @{
        HotFixID = $hotfixID
        Description = $description
        InstalledOn = $installedOn
    }
    $hotfixInfoArray += $hotfixInfo
}

# Gather process metrics
$processes = Get-Process | Where-Object { $_.ProcessName -like '*EveryAngle*' -or $_.ProcessName -like '*Tanium*' -or $_.ProcessName -like '*Sentinel*' } | Sort-Object CPU -Descending
$jsonObjects = @()

foreach ($process in $processes) {
    $processName = $process.ProcessName
    $cpuUsage = if ($process.CPU) { $process.CPU } else { 0 }
    $jsonObject = @{
        ProcessName = $processName
        CPUUsage = $cpuUsage
    }
    $jsonObjects += $jsonObject
}

# Create combined JSON object
$timestamp = Get-Date -Format "yyyy-MM-ddTHH:mm:ss.fffZ"

$combinedJson = @{
    "customer"  = $customerName
    "Timestamp" = $timestamp
    "InstalledSoftware" = $packageInfoArray
    "SystemUpdates" = $hotfixInfoArray
    "CPUMetrics"  = $jsonObjects
}

# Convert combined JSON object to JSON
$jsonData = $combinedJson | ConvertTo-Json

# Send data to API endpoint
$url = "https://cloudcanvas.iswcloudapp.com/product/A4S/A4S-Dev-Acc"

$headers = @{
    "Content-Type" = "application/json"
}

$response = Invoke-RestMethod -Uri $url -Method Post -Headers $headers -Body $jsonData

if ($response) {
    Write-Host "Data pushed successfully to the API endpoint."
} else {
    Write-Host "Failed to push data."
    Write-Host "Response:" $response
}
