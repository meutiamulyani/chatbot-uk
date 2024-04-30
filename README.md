1. To run in localhost:
   ```uvicorn main:app --reload```
2. To check .env (postgres data) in linux:
   ```nano chatbot_oohbali/.env```
3. To stop background chatbot program run in linux:
   ```systemctl status uv.oohbali.service```
4. To restart background oohbali program in linux:
   ```systemctl start uv.oohbali.service```
5. To check error log in linux:
   ```tail -f /var/log/uv.oohbali.log```
6. To check background run status:
   ```systemctl status uv.oohbali.service```
   
