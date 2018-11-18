set /a number=%random% %% 100
start http://inf-1049-%number%.localtunnel.me
start http://127.0.0.1:5000
ruby localtunnel.rb --port 5000 --subdomain inf-1049-%number%