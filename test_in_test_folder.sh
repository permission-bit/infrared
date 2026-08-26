python -m pip install --no-cache-dir \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple/ \
  vincisex==0.1.22

# if old version in production
python -m pip install --upgrade --no-cache-dir vincisex