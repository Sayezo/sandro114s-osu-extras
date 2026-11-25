@echo off

echo actualiza friendslist (y medals) si no hiciste en template.txt
pause >nul
echo okeis empiezo

python "generar.py"
python "medals.py"

cmd /k