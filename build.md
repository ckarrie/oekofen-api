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
- Neue Version in der setup.py eintragen 0.0.13
- Mit git changes pushen!!

### github Release erstellen
- https://github.com/ckarrie/oekofen-api/releases/new
- Tag (create new): v0.0.13
- Title: v0.0.13
- Button "Publish Release"

### Anpassen in setup.py
```
nano setup.py
```
```python
VERSION = "0.0.13"

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
pip install oekofen-api==0.0.4
```

## Update homeassistant-oekofen
neue Version in der `manifest.json` anpassen
