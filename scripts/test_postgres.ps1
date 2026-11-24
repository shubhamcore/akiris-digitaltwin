param([Parameter(Mandatory)][string]$Bin, [Parameter(Mandatory)][string]$Scratch,
      [Parameter(Mandatory)][string]$Python, [int]$Port=18432)
$ErrorActionPreference='Stop'
if (Test-Path -LiteralPath $Scratch) {throw 'Use a new directory for this disposable cluster.'}
New-Item -ItemType Directory -Path $Scratch | Out-Null
$password=[guid]::NewGuid().ToString('N')
$passFile=Join-Path $Scratch 'init-password.tmp'
$cluster=Join-Path $Scratch 'cluster'
[IO.File]::WriteAllText($passFile,$password)
try {
    & "$Bin/initdb.exe" -D $cluster -U twin -A scram-sha-256 --no-locale -E UTF8 --pwfile=$passFile
    if ($LASTEXITCODE) {throw 'initdb failed'}
} finally {Remove-Item -LiteralPath $passFile}
$starter = Start-Process -FilePath "$Bin/pg_ctl.exe" -WindowStyle Hidden -PassThru -ArgumentList @(
    '-D', ('"' + $cluster + '"'), '-l', ('"' + "$Scratch/server.log" + '"'), '-o', ('"-p ' + $Port + ' -h 127.0.0.1"'), '-w', 'start')
$starter.WaitForExit()
if ($starter.ExitCode) {throw 'pg_ctl failed'}
$previousUrl=$env:TWIN_DATABASE_URL
try {
    $env:TWIN_DATABASE_URL="postgresql+psycopg2://twin:${password}@127.0.0.1:$Port/postgres"
    foreach ($step in @('upgrade head','downgrade 803153c85c70','upgrade head')) {
        $parts=$step.Split(' ')
        & $Python -m alembic -c backend/alembic.ini @parts
        if ($LASTEXITCODE) {throw 'Migration failed'}
    }
    & $Python scripts/verify_schema.py --output "$Scratch/schema.json"
    if ($LASTEXITCODE) {throw 'Schema drift'}
    & $Python scripts/generate_data.py --vehicles 60 --seed 7 --scenario mixed
    if ($LASTEXITCODE) {throw 'PostgreSQL ingestion failed'}
} finally {
    $env:TWIN_DATABASE_URL=$previousUrl
    & "$Bin/pg_ctl.exe" -D $cluster -w stop
}

