# Contributing

## Local setup

```powershell
npm install --legacy-peer-deps
python -m pip install -r requirements.txt -r tests/requirements.txt
```

## Common tasks

```powershell
npm run build:js
npm run build:backends
python -m pytest
python usage.py
```

## Publishing

```powershell
python -m pip install -r requirements.txt -r tests/requirements.txt
python -m pip install build twine
.\scripts\check-release.ps1
python -m twine upload --repository testpypi dist/*
```

After uploading to TestPyPI, create a fresh environment and smoke-test the
published package:

```powershell
py -3.11 -m venv .venv-testpypi
.\.venv-testpypi\Scripts\python -m pip install --upgrade pip
.\.venv-testpypi\Scripts\python -m pip install --index-url https://test.pypi.org/simple --extra-index-url https://pypi.org/simple dash-mantine-datatable==0.1.0
.\.venv-testpypi\Scripts\python -c "import dash_mantine_datatable as dmdt; print(dmdt.__version__)"
```

If the TestPyPI smoke test passes, upload the same artifacts to PyPI:

```powershell
python -m twine upload dist/*
```

