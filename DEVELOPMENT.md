# Build lib

python setup.py sdist bdist_wheel

# INSTALL LIB

pip install dist/traderhub_tradeanalytica-0.0.3-py3-none-any.whl

# RUN TEST

python3 -m unittest test.py