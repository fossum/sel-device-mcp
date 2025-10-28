# SEL Device PowerShell Helper Functions
# Usage: . .\sel-device-helper.ps1

$BaseUrl = "http://localhost:8000"

function Start-SELServer {
    <#
    .SYNOPSIS
    Starts the SEL Device REST API server
    #>
    Write-Host "Starting SEL Device Server..." -ForegroundColor Green
    Set-Location "c:\development\ericfoss\sel-device-mcp"
    pipenv run uvicorn src.server.main:app --host 127.0.0.1 --port 8000
}

function Get-SELConnections {
    <#
    .SYNOPSIS
    Lists all available SEL device connections
    #>
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/connections" -Method Get
        return $response
    }
    catch {
        Write-Error "Failed to get connections: $($_.Exception.Message)"
    }
}

function Connect-SELDevice {
    <#
    .SYNOPSIS
    Connects to a SEL device by connection ID
    .PARAMETER DeviceId
    The connection ID of the device to connect to
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$DeviceId
    )

    try {
        Write-Host "Connecting to device: $DeviceId" -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "$BaseUrl/connect/by-id/$DeviceId" -Method Post
        Write-Host "Connected successfully!" -ForegroundColor Green
        return $response
    }
    catch {
        Write-Error "Failed to connect to device: $($_.Exception.Message)"
    }
}

function Send-SELCommand {
    <#
    .SYNOPSIS
    Sends a command to the connected SEL device
    .PARAMETER Command
    The command to send to the device
    .PARAMETER Timeout
    Timeout in seconds (default: 10.0)
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$Command,
        [float]$Timeout = 10.0
    )

    try {
        Write-Host "Sending command: $Command" -ForegroundColor Yellow
        $body = @{
            command = $Command
            timeout = $Timeout
        } | ConvertTo-Json

        $response = Invoke-RestMethod -Uri "$BaseUrl/command" -Method Post -Body $body -ContentType "application/json"
        Write-Host "Command sent successfully!" -ForegroundColor Green
        return $response
    }
    catch {
        Write-Error "Failed to send command: $($_.Exception.Message)"
    }
}

function Get-SELStatus {
    <#
    .SYNOPSIS
    Gets the current connection status
    #>
    try {
        $response = Invoke-RestMethod -Uri "$BaseUrl/status" -Method Get
        return $response
    }
    catch {
        Write-Error "Failed to get status: $($_.Exception.Message)"
    }
}

function Disconnect-SELDevice {
    <#
    .SYNOPSIS
    Disconnects from the current SEL device
    #>
    try {
        Write-Host "Disconnecting from device..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "$BaseUrl/disconnect" -Method Delete
        Write-Host "Disconnected successfully!" -ForegroundColor Green
        return $response
    }
    catch {
        Write-Error "Failed to disconnect: $($_.Exception.Message)"
    }
}

function Show-SELHelp {
    <#
    .SYNOPSIS
    Shows available SEL device functions
    #>
    Write-Host "`nSEL Device Helper Functions:" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    Write-Host "Start-SELServer         - Start the REST API server"
    Write-Host "Get-SELConnections      - List available devices"
    Write-Host "Connect-SELDevice       - Connect to a device"
    Write-Host "Send-SELCommand         - Send command to device"
    Write-Host "Get-SELStatus          - Check connection status"
    Write-Host "Disconnect-SELDevice   - Disconnect from device"
    Write-Host "Show-SELHelp           - Show this help"
    Write-Host "`nExample Usage:" -ForegroundColor Yellow
    Write-Host "Get-SELConnections"
    Write-Host "Connect-SELDevice -DeviceId 'sel_2411'"
    Write-Host "Send-SELCommand -Command 'ID'"
    Write-Host "Get-SELStatus"
    Write-Host "Disconnect-SELDevice"
}

# Show help when script is loaded
Write-Host "SEL Device Helper loaded successfully!" -ForegroundColor Green
Show-SELHelp
