# infrared

## Requirements

- Python 3.11 or newer
  https://www.python.org/downloads/

## Make a project and change to your project

```bash
mkdir your_project
cd your_project
```

## Create and use virtual environment

```bash
python3.11 -m venv venv
source venv/bin/actiavte
```

## Install braxton

### What did you have in mind?

```bash
python -m pip install --upgrade --no-cache-dir braxton
```

# USAGE EXAMPLE

```python
import braxton

braxton.cwd_files()
```

creates RSA private and public key in current working directory
