from PyEMD import EMD
import numpy as np
import pickle
import librosa
from scipy.io import wavfile


def down_sample(input_wav,origin_sr,resample_sr):
    
    resample = librosa.resample(input_wav, origin_sr, resample_sr)
    
    return resample

def analysis(gameId):
    
    file = "./dataset/"+gameId+'_audio.wav'
    
    fs,data = wavfile.read(file)
    
    print(data.shape)
    data= down_sample(data,44100,800)
    print('data loaded')
    return entropy(data,gameId)

def entropy(data,gameId):
    
    print(len(data))
    
    maxP = max(np.abs(data))
    
    p = list(map(lambda x: np.abs(x)/maxP,data))
    
    p = list(map(lambda x:x*np.log(x) if x!=0 else 0, p))
    
    temp=[]
    tempi=0
    for i in range(80,len(p)+1,80):
        temp.append(np.average(p[tempi:i]))
        tempi = i
    p = temp
    
    temp=[]
    
    for i,v in enumerate(p):
        temp.append(-np.sum(p[max(0,i-int(230/2)):min(len(p),i+int(230/2))]))
        
    return emd(temp,gameId)

def emd(data,gameId):
    import numpy as np
    emd_arr = []
    emd = EMD()
    
    temp = 0
    
    data = np.array(data)
    for j in range(0,len(data)+1,600):
        if j !=0:
            IMFs_first = emd(data[temp:j])[0]
            temp = j
            emd_arr.append(IMFs_first)
            
    if temp < len(data):
        IMFs_first = emd(data[temp:len(data)])[0]
        emd_arr.append(IMFs_first)
    
    emd_arr_r = emd_arr[0]
    for i in range(1,len(emd_arr)):
        emd_arr_r = np.concatenate((emd_arr_r,emd_arr[i]),axis=None)
    
    #emd_arr = np.array(emd_arr).flatten()
    with open('/home/ubuntu/hyein/tsvt/web/dataset/'+gameId+'_audio.pickle','wb') as fw:
        pickle.dump(emd_arr_r,fw)
    return emd_arr_r
        
def main(game_id):
    print("Main Function")
    analysis(game_id)

if __name__ == "__main__":
	main('104841804589544588')