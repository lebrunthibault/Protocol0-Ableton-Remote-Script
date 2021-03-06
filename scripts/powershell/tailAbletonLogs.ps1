KillProcess (GetProcessFromNameOrTitle "*logs terminal*")
$host.ui.RawUI.WindowTitle = "logs terminal"

$version = $Env:abletonVersion
#$version = "11.0"

$logFile = "$env:userprofile\AppData\Roaming\Ableton\Live $version\Preferences\Log.txt"
$startSize = 70
$processLogFile = $true
$showDateTime = $true
$global:write_next_n_lines = 0

$host.ui.RawUI.WindowTitle = 'logs terminal'
Get-Process -Id $pid | Set-WindowState -State SHOWMAXIMIZED

function FocusLogs()
{
    python.exe "$p0\scripts\python\focus_window.py" "logs terminal"
}

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
            elseif ($LogEntry.Contains("error") -or $LogEntry.Contains("a_protocol_0") -or $LogEntry.Contains("RuntimeError") -or $LogEntry.Contains("Protocol0Error") -or $LogEntry.Contains("exception"))
            {
                Return "Red"
                FocusLogs
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
            FocusLogs
        }

        Return "DarkGray"
    }
}
function Format-LogLine
{
    Param([Parameter(Position = 0)]
        [String]$LogEntry)

    process {
        if ( $LogEntry.Contains("(Protocol0) Initializing"))
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
function Select-Log-Line
{
    Param([Parameter(Position = 0)]
        [String]$LogEntry)

    if ($write_next_n_lines -ne 0)
    {
        $global:write_next_n_lines -= 1
        return $LogEntry
    }

#    discarding None messages
    $SplitLine = $LogEntry -split "P0 - "

    if ($SplitLine.Length -eq 2) {
        $Message = $SplitLine[1]
        if ($Message -eq "None") {
            return $null
        }
    }

    $Filters = "P0", "Protocol0", "RemoteScriptError"

    foreach ($Filter in $Filters)
    {
        if ( $LogEntry.Contains($Filter))
        {
            if ( $LogEntry.Contains("ArgumentError"))
            {
                $global:write_next_n_lines = 3

            }
            return $LogEntry
            Write-Host -ForegroundColor (Get-LogColor $LogEntry) (Format-LogLine($LogEntry))
        }
    }

    return $null
}
function Write-Log-Line
{
    Param([Parameter(Position = 0)]
        [String]$LogEntry)

    if (Select-Log-Line($LogEntry))
    {
        Write-Host -ForegroundColor (Get-LogColor $LogEntry) (Format-LogLine($LogEntry))
    }
}

if ($processLogFile)
{
    Get-Content -Tail $startSize -wait $logFile | ForEach-Object { Write-Log-Line($_) }
}
else
{
    Get-Content -Tail $startSize -wait $logFile
}