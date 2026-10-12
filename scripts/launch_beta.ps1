param([Parameter(Mandatory=$true)][string]$Script,[string]$BetaExecutable='C:\Program Files\Adobe\Adobe Photoshop (Beta)\Photoshop.exe')
$ErrorActionPreference='Stop'
$resolvedScript=(Resolve-Path -LiteralPath $Script).Path
$resolvedExe=(Resolve-Path -LiteralPath $BetaExecutable).Path
if([System.IO.Path]::GetFileName($resolvedExe) -ne 'Photoshop.exe'){throw 'Expected a Photoshop executable'}
if((Get-Content -LiteralPath $resolvedScript -Raw) -notmatch 'EXPECTED_BETA_ROOT'){throw 'JSX must contain the generated Beta installation guard'}
Start-Process -FilePath $resolvedExe -ArgumentList @('-r',('"'+$resolvedScript+'"')) -WindowStyle Hidden
Write-Output ('SUBMITTED '+$resolvedScript)
