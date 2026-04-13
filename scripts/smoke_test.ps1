param(
    [switch]$WithPytest,
    [switch]$WithOllama,
    [switch]$WithSamples,
    [switch]$WithLiveSamples,
    [int]$SamplesTimeout = 60,
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
if ($WithSamples) { $args += "--with-samples" }
if ($WithLiveSamples) { $args += "--with-live-samples" }
if ($VerboseOutput) { $args += "--verbose" }
$args += @("--samples-timeout", "$SamplesTimeout")
$args += @("--ollama-base", $OllamaBase)

python @args
exit $LASTEXITCODE
