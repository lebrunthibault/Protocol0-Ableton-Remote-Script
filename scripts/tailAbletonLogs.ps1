KillProcess (GetProcessFromNameOrTitle "*logs terminal*") -force
$host.ui.RawUI.WindowTitle = "logs terminal"

$version = $Env:abletonVersion
#$version = "11.0.2"

$logFile = "$env:userprofile\AppData\Roaming\Ableton\Live $version\Preferences\Log.txt"
#$logFile = "C:\Users\thiba\AppData\Roaming\Ableton\Live 11.0.5b1\Preferences\Log.txt"

$startSize = 70
$processLogFile = $true
$debug = $false
$filterLogs = $true
$showDateTime = $true
$global:write_next_n_lines = 0

$host.ui.RawUI.WindowTitle = 'logs terminal'
Get-Process -Id $pid | Set-WindowState -State SHOWMAXIMIZED

if ($debug)
{
    $startSize *= 5
}

# simple FocusLogs debounce
$focusLogStopWatch = New-Object System.Diagnostics.Stopwatch
function FocusLogs()
{
    if ($focusLogStopWatch.IsRunning -and $focusLogStopWatch.ElapsedMilliseconds -lt 1000)
    {
        return;
    }
    $focusLogStopWatch.Restart()
    python "$system\scripts\cli.py" "focus_window" "logs terminal" 2> $nul
}

function Get-LogColor
{
    Param([Parameter(Position = 0)]
        [String]$LogEntry)

    process {
        if ( $LogEntry.Contains("P0 -"))
        {
            if ( $LogEntry.Contains("P0 - dev"))
            {
                Return "Yellow"
            }
            elseif ($LogEntry.Contains("P0 - debug"))
            {
                Return "Gray"
            }
            elseif ( $LogEntry.Contains("P0 - info"))
            {
                Return "Green"
            }
            elseif ($LogEntry.Contains("P0 - notice"))
            {
                Return "Blue"
            }
            elseif ($LogEntry.Contains("P0 - warning"))
            {
                Return "Magenta"
            }
            elseif ($LogEntry.Contains("P0 - error"))
            {
                # copying the filename where the error happened
                if ($LogEntry -match "at (?<filename>\.\\.*\.py)")
                {
                    Set-Clipboard -Value $matches["filename"]
                }
                Return "Red"
            }
            else
            {
                FocusLogs
                Return "Red"
            }
        }

        if ($LogEntry.Contains("P0") -or $LogEntry.Contains("Protocol0"))
        {
            return "Green"
        }


        if ($LogEntry -like ("*error*") -or $LogEntry -like ("*exception*"))
        {
            FocusLogs
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
        # remove Protocol 0 log prefix
        if ($debug)
        {
            Write-Host $LogEntry
        }
        $LogEntry = $LogEntry -replace "P0 - (\w+:)?"

        # remove unecessary remote script log info
        $LogEntry = $LogEntry -replace "Python: INFO:root:\d* - "
        $LogEntry = $LogEntry -replace "(info|debug):\s?"
        $LogEntry = $LogEntry -replace "RemoteScriptError: "

        # Simplify date
        $timestampReg = "^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.\d{6}:"
        if ($LogEntry -match $timestampReg)
        {
            $parts = $LogEntry.Split(" ")  # keeping indentation

            if (-not ($parts[2..($parts.Count - 1)] -join " ").Trim())
            {
                return ""
            }
            if ($showDateTime)
            {
                $date = [datetime]::parseexact($parts[0], 'yyyy-MM-ddTHH:mm:ss.ffffff:', $null)
                $logEntry = (Get-Date -Date $date -Format "HH:mm:ss.fff") + " " + $parts[1].Trim() + " " + ($parts[2..($parts.Count - 1)] -join " ")
            }
            else
            {
                $logEntry = $parts[1..($parts.Count - 1)] -join " "
            }
        }

        Return $LogEntry
    }
}
function Select-Log-Line
{
    Param([Parameter(Position = 0)]
        [String]$LogEntry)

    if (-not$filterLogs)
    {
        return $true
    }

    if ( $LogEntry.Contains("clear_logs"))
    {
        Clear-Host
        return $false
    }

    if ($LogEntry.Contains("(Protocol0) Initializing") -or $LogEntry.Contains("Check :"))
    {
        Clear-Host
    }

    # contains is case insensitive
    $Filters = "P0", "Protocol0", "ArgumentError", "RemoteScriptError", "Exception"

    foreach ($Filter in $Filters)
    {
        if ( $LogEntry.Contains($Filter))
        {
            if ($LogEntry.Contains("ArgumentError") -or $LogEntry.Contains("Pythonargument"))
            {
                $global:write_next_n_lines = 3
            }
            return $LogEntry
        }
    }

    if ($write_next_n_lines -ne 0)
    {
        $global:write_next_n_lines -= 1
        return $LogEntry
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