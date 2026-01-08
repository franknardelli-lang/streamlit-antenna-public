# Configuration
$ServerUser = "alan"
$ServerIP = "192.168.1.162"
$AppFolder = "~/apps/streamlit-antenna-public"

# 1. Push Local Changes to GitHub
Write-Host "🚀 Pushing changes to GitHub..." -ForegroundColor Cyan
git push

# 2. Tell XPS to Pull and Restart
Write-Host "🔄 Updating XPS Server..." -ForegroundColor Cyan
ssh $ServerUser@$ServerIP "cd $AppFolder && git pull && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && pkill -f streamlit; nohup streamlit run app.py --server.port 8501 > app.log 2>&1 &"

Write-Host "✅ Deployed! App is running at http://$ServerIP:8501" -ForegroundColor Green