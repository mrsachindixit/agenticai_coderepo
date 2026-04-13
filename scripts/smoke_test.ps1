param(
    [switch]$WithPytest,
    [switch]$WithOllama,
    [string]$OllamaBase = $env:OLLAMA_BASE,
    [switch]$VerboseOutput
)

if (-not $OllamaBase) {
    $OllamaBase = "http://localhost:11434"
}

$scriptPath = Join-Path $PSScriptRoot "smoke_test.py"
$args = @($scriptPath)

if ($WithPytest) { $args += "--with-pytest" }
if ($WithOllama) { $args += "--with-ollama" }
if ($VerboseOutput) { $args += "--verbose" }
$args += @("--ollama-base", $OllamaBase)

python @args
exit $LASTEXITCODE
