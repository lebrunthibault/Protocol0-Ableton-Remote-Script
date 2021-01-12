KillProcess (GetProcessFromNameOrTitle "*logs terminal*")
$host.ui.RawUI.WindowTitle = "logs terminal"

$logFile = "$env:userprofile\AppData\Roaming\Ableton\Live $Env:abletonVersion\Preferences\Log.txt"
$startSize = 70
$processLogFile = $true
$showDateTime = $true

function Get-LogColor
{
    Param([Parameter(Position = 0)]
        [String]$LogEntry)

    process {
        if ( $LogEntry.Contains("P0 -"))
        {
            if ( $LogEntry.Contains("P0 - info"))
            {
                Return "Green"
            }
            elseif ($LogEntry.Contains("P0 - error") -or $LogEntry.Contains("a_protocol_0"))
            {
                Return "Red"
            }
            elseif ($LogEntry.Contains("P0 - debug"))
            {
                Return "Yellow"
            }
            elseif ($LogEntry.Contains("send_keys"))
            {
                Return "Blue"
            }
            elseif ($LogEntry.Contains("send_click"))
            {
                Return "Blue"
            }
            else
            {
                Return "White"
            }
        }

        if ( $LogEntry.Contains("RemoteScriptError"))
        {
            Return "Red"
        }

        Return "DarkGray"
    }
}
function Format-LogLine
{
    Param([Parameter(Position = 0)]
        [String]$LogEntry)

    process {
        if ( $LogEntry.Contains("Protocol0 script loaded"))
        {
            Clear-Host
        }
        # Simplify date
        $timestampReg = "^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}:"
        if ($LogEntry -match $timestampReg)
        {
            $parts = $LogEntry.Split(" ")
            if ($showDateTime)
            {
                $date = [datetime]::parseexact($parts[0], 'yyyy-MM-ddTHH:mm:ss.ffffff:', $null)
                $logEntry = (Get-Date -Date $date -Format "HH:mm:ss.fff") + " " + $parts[1..($parts.Count - 1)] -join " "
            }
            else
            {
                $logEntry = $parts[1..($parts.Count - 1)] -join " "
            }
        }

        # remove Protocol 0 log prefix
        $LogEntry = $LogEntry -replace "P0 - (\w+: )?"

        # remove unecessary remote script log info
        $LogEntry = $LogEntry -replace "info: "
        $LogEntry = $LogEntry -replace "Python: INFO:root:\d* - "

        Return $LogEntry
    }
}

$P0Filter = "P0", "RemoteScriptError"

$host.ui.RawUI.WindowTitle = 'logs terminal'
Get-Process -Id $pid | Set-WindowState -State SHOWMAXIMIZED

if ($processLogFile)
{
    Get-Content -Tail $startSize -wait $logFile | Select-String -pattern $P0Filter -AllMatches | ForEach-Object { Write-Host -ForegroundColor (Get-LogColor $_) (Format-LogLine($_)) }
}
else
{
    Get-Content -Tail $startSize -wait $logFile
}