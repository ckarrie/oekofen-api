# Upload to pypi Flow
## Vorbereitung / Installation
```
cd ~/workspace/venvs/homeassistant-oekofen
source bin/activate
pip install build
pip install twine
```

## pypi settings 
```
nano ~/.pypirc
```

## Neue Version uploaden
```
cd ~/workspace/venvs/homeassistant-oekofen
source bin/activate
cd ~/workspace/src/oekofen-api
```

### Push git changes
- Mit git changes pushen

### github Release erstellen
- https://github.com/ckarrie/oekofen-api/releases/new
- Tag (create new): v0.0.2
- Title: v0.0.2
- Button "Publish Release"

### Anpassen in setup.py
```
nano setup.py
```
```python
setup(
    ...
    version="0.0.2",
    download_url='https://github.com/ckarrie/oekofen-api/archive/refs/tags/v0.0.2.tar.gz',
    ...
)

```

```
rm -rf dist
python3 -m build
```

## Upload Test
```
twine upload -r testpypi dist/*
```

## Upload Live
```
twine upload dist/*
```

Lokal updaten

```
pip install oekofen-api==<NEUE VERSIONSNUMMER>
```

## Update homeassistant-oekofen
neue Version in der `manifest.json` anpaasen
