<# Offline tests (no cluster needed): student CRUD, health endpoints, dashboard demo logic, manifest consistency.
   Requires Python 3.10+ :   pip install -r tests\requirements.txt   (once) #>
Set-Location (Split-Path -Parent $PSScriptRoot)
python -m unittest discover -s tests -p "test_*.py" -v
exit $LASTEXITCODE
