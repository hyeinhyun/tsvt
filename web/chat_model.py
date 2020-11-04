import numpy as np
import torch
import string
import torch.nn as nn
from torch.autograd import Variable
from torch.nn.utils.rnn import pad_packed_sequence as unpack
from torch.nn.utils.rnn import pack_padded_sequence as pack
import math
import torch.utils.data as data
import json
import os
import pandas as pd
import random
import copy
import torch.utils.data.sampler as sampler
import torch.optim.lr_scheduler as lr_scheduler
import pickle

all_letters = string.printable
n_letters = len(all_letters)
def letterToIndex(letter):
    return all_letters.find(letter)
def linesToTensor(lines):
    line_length = 15000
    if max([ len(line) for line in lines]) < line_length:
        line_length = max( [len(line) for line in lines] )
    #line_length = max( [len(line) for line in lines] )
    #xx = [max(len(line)-15000,0) for line in lines]
    #print float(np.sum(xx)) / float(np.sum([len(line) for line in lines]))
    tensor = torch.zeros(len(lines), line_length, n_letters)
    for b, line in enumerate(lines): 
        line = line[:15000]
        for li, letter in enumerate(line):
            tensor[b][li + line_length - len(line)][letterToIndex(letter)] = 1 #뒤로 맞춰줌

    return tensor

class LangModel(nn.Module):
    def __init__(self, preTrained='True', input=100):
        super(LangModel, self).__init__()

        # Language Model
        self.lang = nn.LSTM(input, 128, 3, batch_first=True) 
 
        # Output 
        self.output = nn.Linear(128, 2)
        n = self.output.in_features * self.output.out_features
        self.output.weight.data.normal_(0, math.sqrt(2. / n))
        self.output.bias.data.zero_()

    def forward(self, text):
        text.cuda()
        h0 = ( Variable(torch.zeros(3, text.size(0), 128)).cuda(),  Variable(torch.zeros(3, text.size(0), 128)).cuda())

        lang_feature, hn = self.lang(text, h0 )
        lang_feature = lang_feature[:,-1,:]

        pred = self.output(lang_feature)
        return lang_feature
import torch.utils.data as data

class chat_ds(data.Dataset):
    def __init__(self,d_type):
        self.d_type=d_type

        with open('./chat.json','rb') as f2:  
            self.text=json.load(f2)
        if d_type=='test':
            self.sample = ['test']


        self.sum=np.insert(np.cumsum([len(self.text[str(i)]) for i in self.sample]),0,0)
        print("data load fin")

        
    def __len__(self):
        return self.sum[-1]
    def __getitem__(self,index):
            vid=np.histogram(index,self.sum)
            vid = np.where(vid[0]>0)[0][0]
            vframe=index-self.sum[vid]
            game_id=str(self.sample[vid])

            win_text=''
            for idx in range(7): #7 : window size
                if vframe+idx<len(self.text[str(game_id)]):
                    win_text+=self.text[str(game_id)][vframe+idx]+'\n'

            return win_text,str(game_id)
def main():
    ###### model load #####
    model=LangModel().cuda()
    criterion = nn.CrossEntropyLoss().cuda()


    test=chat_ds('test')
    test_loader=torch.utils.data.DataLoader(test,batch_size=1)
    dataset='./chat_best'
    checkpoint=torch.load(dataset,map_location='cuda:0')
    model.load_state_dict(checkpoint)
    model.cuda()
    model.eval()

    result={}
    with torch.no_grad():
        for it, (text,game_id) in enumerate(test_loader):
            inputs=linesToTensor(text)
            inputs = inputs.cuda()
            output=model(inputs)
            if game_id[0] not in result.keys():
                print(game_id[0])
                result[game_id[0]]=[(output[0]).tolist()]

            else:
                result[game_id[0]]+=[(output[0]).tolist()]
    with open('./chat_features.json','w') as f:
        json.dump(result,f)