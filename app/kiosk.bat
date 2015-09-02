:: On ferme explorer.exe pour désactiver les barres latérales windows 8
taskkill /f /im explorer.exe

:start

::Sorte de sleep de 5 secondes
ping 0.0.0.0 -n 5 > NUL
:: Chemin relatif vers le main.py
"main.py" 
:: Une fois Museotouch fermé, on relance Museotouch

goto start