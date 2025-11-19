
@echo off
echo Atualizando aplicacao...

REM Aguarda o programa fechar
ping 127.0.0.1 -n 2 >nul

REM Remove backup antigo se existir
if exist "\\192.168.1.2\Tecnologia\desenvolvimento\CÓDIGOS GITHUB\Sistema-Capt-Empresarial\INTERFACE.old.exe" del "\\192.168.1.2\Tecnologia\desenvolvimento\CÓDIGOS GITHUB\Sistema-Capt-Empresarial\INTERFACE.old.exe"

REM Renomeia o executável atual
ren "\\192.168.1.2\Tecnologia\desenvolvimento\CÓDIGOS GITHUB\Sistema-Capt-Empresarial\INTERFACE.py" "INTERFACE.old.exe"

REM Copia o novo executável baixado
copy "\\192.168.1.2\Tecnologia\desenvolvimento\CÓDIGOS GITHUB\Sistema-Capt-Empresarial\update\CaptacaoEmpresarial14D.exe" "\\192.168.1.2\Tecnologia\desenvolvimento\CÓDIGOS GITHUB\Sistema-Capt-Empresarial\INTERFACE.py" /Y

REM Inicia o executável atualizado
start "" "\\192.168.1.2\Tecnologia\desenvolvimento\CÓDIGOS GITHUB\Sistema-Capt-Empresarial\INTERFACE.py"

REM Apaga o próprio script
del "%~f0"
