from flask import Flask, request, make_response,render_template,Response
import datetime
import requests
import json
import re
import chat
import audio
import api
import chat_audio_model
import final_model
import asyncio
import threading
from multiprocessing import Process
import smtplib
from email.mime.text import MIMEText
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
#import api.py
url=''
game_id=''
sync_i=''
sync_v=''
dur=''
email=''
time=''
ClientId = "pnbcpj842zq89uy7hlhkakepr6xej7" # Client id 추가 #
#create dir
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('weights'):
    os.makedirs('weights')
def sync():
    H,M,S=map(int,sync_v.split(':'))
    i_h,i_m,i_s=map(int,sync_i.split(':'))
    
    v_stime=H*3600+M*60+S-(i_h*3600+i_m*60+i_s)
    v_etime=v_stime+int(dur)
    return v_stime,v_etime

@app.route("/api", methods=['GET','POST'])
def main_api():
    global url
    global game_id
    global sync_i
    global sync_v
    global email
    global time
    api_return = request.json
    print(api_return)
    #api_return = request.get_json()
    if 'url' in api_return.keys():
        print(api_return['url'])
        url=api_return['url']
        return make_response("",200)
    elif 'email' in api_return.keys():
        email=api_return['email']
        print(email)
        return make_response("",200)
    else:
        print(api_return)
        game_id=api_return['id']
        time=api_return['time']
        sync_v=api_return['videotime']
        sync_i=api_return['gametime']
        heavy_process = Process(  # Create a daemonic process with heavy "my_func"
        target=main,
        daemon=True)
        heavy_process.start()

        return make_response("",200)




def main():
    global dur
        #url 에서 id 얻기
    v_id=''
    if re.findall(r'\d+', url):
        v_id=re.findall(r'\d+', url)[0]
    print("======================******* video ******==========================")
    dur=api.main(game_id,time)
    print(dur)
    v_stime,v_etime=sync()
    print("======================******* chat ******==========================")
    #chat_data
    #chat.main(v_id,ClientId,v_stime,v_etime,game_id)
    print("======================******* audio ******==========================")
    #audio_data
    #audio.main(v_id,v_stime,dur,game_id)
    print("======================******* audio&chat feature ******==========================")
    #chat_audio_model.main(game_id)
    print("======================******* 2step ******==========================")
    final_model.main(game_id)
    with open('./dataset/'+game_id+'_result.txt','r') as f: 
        reresult=f.read()
        
    print("**************************Sending Email!******************************")
    smtp = smtplib.SMTP('smtp.gmail.com', 587)
    smtp.ehlo()      # say Hello
    smtp.starttls()  # TLS 사용시 필요
    smtp.login('wjdrmf314@gmail.com', 'qkrrkdals314')
    msg = MIMEText(reresult)
    msg['Subject'] = 'e-sports highlight!'
    print('check')
    print(email)
    msg['To'] = email
    smtp.sendmail('wjdrmf314@gmail.com', email, msg.as_string())
    smtp.quit()
    print("DONE! BYE :)")
@app.route("/cap", methods=['GET', 'POST'])
def home():
    return render_template('index.html')




if __name__ == '__main__':
    app.run('0.0.0.0', port=31400,debug=True)
    #token=response
