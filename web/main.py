from flask import Flask, request, make_response,render_template
import datetime
import requests
#import json
import re
from chat import *
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

ClientId = "pnbcpj842zq89uy7hlhkakepr6xej7" # Client id 추가 #

def sync(sdate,edate,sync_v,sync_i):
    dur=(datetime.strptime(edate, "%Y-%m-%dT%H:%M:%S.%fZ")-datetime.strptime(edate, "%Y-%m-%dT%H:%M:%S.%fZ")).seconds
    H,M,S=map(int,sync_v.split(':'))
    i_m,i_s=map(int,sync_i.split(':'))
    
    v_stime=H*3600+M*60+S-(i_m*60+i_s)
    v_etime=v_stime+dur
    return v_stime,v_etime

@app.route("/result", methods=['GET', 'POST'])
def main():
    data_info={}
    #data_event = json.loads(request.data)
    #print(data_event)
    print(request)
    data_event = request.form
    url=data_event['url']
    print(url)
    sdate=data_event['sdate']
    edate=data_event['edate']
    sync_v=data_event['sync_v']
    sync_i=data_event['sync_i']
    #url 에서 id 얻기
    if re.findall(r'\d+', videos):
        v_id=re.findall(r'\d+', videos)[0]
    v_stime,v_etime=sync(sdate,edate,sync_v,sync_i)
    data_info['url']=url
    data_info['v_id']=v_id
    data_info['v_stime']=v_stime
    data_info['v_etime']=v_etime
    chat(v_id,Clientid,v_stime,v_etime)

@app.route("/cap", methods=['GET', 'POST'])
def home():
    return render_template('index.html')






if __name__ == '__main__':
    app.run('0.0.0.0', port=31400,debug=True)
    #token=response
