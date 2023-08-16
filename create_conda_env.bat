@echo off
echo Installing...
call conda create -n MrKenCommunity_Luna_v3 Python=3.10 -y
call conda activate MrKenCommunity_Luna_v3
pip3 install git+https://github.com/Pycord-Development/pycord
pip3 install PyNaCl
echo Complete!!
pause