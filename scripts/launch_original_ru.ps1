param(
    [ValidateSet(230,232)][int]$Build = 230,
    [string]$Executable = 'C:\Users\Tanue Hou\Downloads\TestVkr (1).exe',
    [string]$LocaleEmulatorDirectory = (Join-Path $PSScriptRoot '..\..\runtime\locale-emulator-2.5.0.1')
)
$ErrorActionPreference = 'Stop'
if ($Build -eq 232 -and -not $PSBoundParameters.ContainsKey('Executable')) { $Executable = 'C:\Users\Tanue Hou\Downloads\TestVkr (2).exe' }
$launcher = Join-Path $LocaleEmulatorDirectory 'LEProc.exe'
$common = Join-Path $LocaleEmulatorDirectory 'LECommonLibrary.dll'
if (!(Test-Path -LiteralPath $launcher) -or !(Test-Path -LiteralPath $common)) {
    throw 'Portable Locale Emulator and LECommonLibrary.dll are required; this launcher does not change the Windows system locale.'
}
if (!(Test-Path -LiteralPath $Executable)) { throw "Target does not exist: $Executable" }
$identities = @{230='0BB43CEBC4C7EE196913D2EA2240F7BC53AAAC1E6B8F6394E6201024A108B8CB';232='5C04B57ACDBDA79073604D6E3CACC2994BC87C5ED316E3B8706555CA92B6A8F0'}
$expected = $identities[$Build]
if ((Get-FileHash -LiteralPath $Executable -Algorithm SHA256).Hash -ne $expected) {
    throw 'Target hash differs from the analyzed TestVkr build. Re-identify the version before using this evidence.'
}
# Profile lives beside the portable launcher; no shell extension or global locale install.
Start-Process -FilePath $launcher -ArgumentList @('-runas', 'f1a09388-5d14-4fa9-b501-5fc1a2b42561', ('"' + $Executable + '"')) -WindowStyle Hidden
