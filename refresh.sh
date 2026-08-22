# build new 
rm -rf build dist
python -m build
python -m pip uninstall infraredx
python -m pip install dist/infraredx-0.1.0-py3-none-any.whl

# upload

python -m pip install --upgrade twine

python -m twine check dist/*

python -m twine upload --repository testpypi dist/*

python -m twine upload dist/*

pip install infrared