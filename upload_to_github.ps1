# Скрипт для загрузки файлов на GitHub
# Замени YOUR_USERNAME на свой GitHub username
# Замени REPO_NAME на имя репозитория

$username = "YOUR_USERNAME"  # Замени на свой GitHub username
$repo = "telegram-bot-maxwin"  # Замени на имя репозитория

git init
git add main.py requirements.txt help_screenshot.jpg .gitignore
git commit -m "Initial commit: Telegram bot MaxWIN Radar"
git branch -M main
git remote add origin "https://github.com/$username/$repo.git"
git push -u origin main

Write-Host "Файлы загружены на GitHub!" -ForegroundColor Green

