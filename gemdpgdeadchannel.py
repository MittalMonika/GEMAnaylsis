#README the best solution can IR[ find till now
#1.set up your enviormment. any CMMSSW release
#! /usr/bin/env python
#vfaterror_warn
#bincontent 0: No digi, no error, no warning (white)
#1;95;0c1: Having digi, no error, no warning (blue here green)
#2: Error (> 5%) ( light green, RED
#3: Warning, no error blue
#4: Error (< 5%) (yellow) orange can put any conditions
#here 5% means ratio of events with error if the ratio is larger than 5%, then the status is in red; otherwise, orange
#chamber error
#chamberErrors
#chamberAllStatus
#chamberWarnings

import os
import sys
import string
import ROOT
from ROOT import gStyle
from ROOT import gROOT
from ROOT import TFile,TH1F, TH2F
import copy
import subprocess
import json

def downloadfile(url,histPM,mode):
    print("running on file ", url)
    #for current version we change file_ to url

    threshold=1
    file_= url.split('/')[-1]
    runnumber = file_.split('.')[0].split('_')[-1].split('R000')[-1]



    #directory on eos
    pltdir_wr= "/eos/user/m/mmittal/www/GEMPlots/GEMDPG/Inactive_18Nov2022/"
    pltdir=pltdir_wr+runnumber+"/"
    subprocess.call(["mkdir", "-p", pltdir])
    subprocess.call(["scp", "/eos/user/m/mmittal/www/GEMPlots/GEMDPG/Inactive/index.php", pltdir_wr])
    subprocess.call(["scp", "/eos/user/m/mmittal/www/GEMPlots/GEMDPG/Inactive/index.php", pltdir])

    if(histPM =="re-1" or histPM =="GE-11" or histPM =="GE11-M"):
        region=-1
        txtfilename="DeadChannels_Minus.txt"

    if(histPM =="re1" or histPM =="GE+11" or  histPM =="GE11-P"):
        region=1
        txtfilename="DeadChannels_Positive.txt"

    #For wheep plot
    #now wheel plot is available at /eos/user/m/mmittal/www/GEMPlots/GEMDPG/Inactive_18Nov2022/runnumber/ #change it for code for whheel plot
    vtxtfilename=pltdir+"/Visulization_DeadChannels.csv"     

    f_deadchannel_L1  = open(pltdir+txtfilename.split(".txt")[0]+"_L1.txt","w")
    f_deadchannel_L2  = open(pltdir+txtfilename.split(".txt")[0]+"_L2.txt","w")
    j_deadchannel_L1  = open(pltdir+txtfilename.split(".txt")[0]+"_L1.json","w")
    j_deadchannel_L2  = open(pltdir+txtfilename.split(".txt")[0]+"_L2.json","w")
    v_deadchannel_L1   = open(vtxtfilename,mode)
    f_deadchannel  = open("LowThreshold_test"+txtfilename,"w")


    path_ = url
    if not (os.path.isfile(url)):
        print('   + not find"' + url + '"...')

    if (os.path.isfile(url)):  
        print('   + OK!' + url + '"...')

        histpath_dir = "DQMData/Run "+runnumber+"/GEM/Run summary/Digis/"
        f_deadchannel.write("chambername    ieta  #strip   stripnum \n")
        f_deadchannel_L1.write("chambername    ieta  #strip   stripnum \n")
        f_deadchannel_L2.write("chambername    ieta  #strip   stripnum \n")


        #chamberID,region,chamber,layer,VFATN,totalchannels,deadchannels
        iter=0
        if(region == -1 and iter==0):
            v_deadchannel_L1.write("chamberID,region,chamber,layer,VFATN,totalchannels,deadchannel\n")
            iter += 1

        layer1=[]
        layer2=[]
        vfatlayer1=[]
        vfatlayer2=[]

        ## removing chamber off/error and vfat that didn't send data
        histpath_dir_ve="DQMData/Run "+runnumber+"/GEM/Run summary/EventInfo/"
        histpath_dir_ce ="DQMData/Run "+runnumber+"/GEM/Run summary/DAQStatus/"
        #read the root file 
        root_file = ROOT.TFile(path_, "READ")
        ChamErr= root_file.Get(histpath_dir_ce+"chamberAllStatus")


        list_choff_L1=[]
        list_choff_L2=[]
        LIST_CH_L1=[]
        LIST_CH_L2=[]
        fullvfatlist=[]
        vfat_off_L1 =0
        vfat_off_L2 =0

        dictdead_l1={}
        dictdead_l2={}
        for i in range(1,37):
            #if (i != 10): continue
            for j in range(1,3):
                if i < 10 : 
                        histpath_ ="occupancy_"+histPM+"-L"+str(j)+"/occ_"+histPM+"-0"+str(i)+"L"+str(j)
                else :
                        histpath_ ="occupancy_"+histPM+"-L"+str(j)+"/occ_"+histPM+"-"+str(i)+"L"+str(j)
                detname=histPM+"-L"+str(j)        
                histpath_ve= "vfat_statusSummary_"+histPM+"-L"+str(j)    
                if(int(i) % 2 == 0):  
                    fullname_hist=histpath_+"-L"
                else :
                    fullname_hist=histpath_+"-S"

                histpath = histpath_dir+fullname_hist
                hist = root_file.Get(histpath)    
                hist_ve = root_file.Get(histpath_dir_ve+histpath_ve)
                
                nbinX_ve=hist_ve.GetXaxis().GetNbins()
                nbinY_ve=hist_ve.GetYaxis().GetNbins()
                fullname= fullname_hist.split('_')[-1]
                nbinX=hist.GetXaxis().GetNbins() ; nbinY=hist.GetYaxis().GetNbins()
                striplistchamber=[]


                # making a list of the vfat that were disconnected 
                if(detname == "GE11-M-L1"):
                        choff = ChamErr.GetBinContent(i,4)
                if(detname == "GE11-M-L2"):
                        choff = ChamErr.GetBinContent(i,5)
                if(detname == "GE11-P-L1"):
                        choff = ChamErr.GetBinContent(i,3)
                if(detname == "GE11-P-L2"):
                        choff = ChamErr.GetBinContent(i,2)



                if(choff==0.0):
                   if j==1 : list_choff_L1.append(fullname_hist.split("occ_")[-1])
                   if j==2 : list_choff_L2.append(fullname_hist.split("occ_")[-1])

                listvfat_off_h=[]
                listvfat_off_L1_h=[]
                listvfat_off_L2_h=[]
                for vfat_ in range(1,25):
                    vfat_cont= hist_ve.GetBinContent(i,vfat_)
                    '''
                    if(j == 1 and histPM=="GE11-M" ):
                        if( i==2  and (vfat_  <= 9 or vfat_ == 17 )) : vfat_cont =0.0    
                        if( i==6  and (vfat_ == 11 or vfat_ == 18 or vfat_ == 23)) : vfat_cont =0.0
                        if( i==7  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==8  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==12  and (vfat_ <=7 or vfat_ == 9 or vfat_ == 17)) : vfat_cont =0.0
                        if( i==14  and (vfat_ == 9)) : vfat_cont =0.0
                        if( i==15  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==17  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==21  and (vfat_ == 24)) : vfat_cont =0.0
                        if( i==22  and (vfat_  <= 7 or vfat_ == 9 or vfat_ == 17 )) : vfat_cont =0.0
                        if( i==25  and (vfat_  <= 7 or vfat_ == 9 or vfat_ == 17 )) : vfat_cont =0.0
                        if( i==26  and (vfat_ <= 24)) : vfat_cont =0.0 
                        if( i==32  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==36  and (vfat_ == 8)) : vfat_cont =0.0

                    if(j == 2 and histPM=="GE11-M" ):
                        if( i==2  and (vfat_  <=  7 or vfat_ ==9 or vfat_ ==10 or vfat_ ==11 or vfat_ == 12 or vfat_ ==17 or vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0    
                        if( i==3  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==5  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==8  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==14  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==15  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==20 and (vfat_ ==9 or vfat_ ==13 or vfat_ ==14 or vfat_ >=21 )) : vfat_cont =0.0
                        if( i==24 and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==25  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==26 and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==27 and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==29 and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==31  and ( vfat_ ==9 or vfat_ == 10 or vfat_ ==11 or vfat_ == 12 or vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0    
                        if( i==32 and (vfat_ <= 24)) : vfat_cont =0.0

                    if(j == 1 and histPM=="GE11-P" ):
                        if( i==1  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==2  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==3  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==5  and (vfat_ <= 7 or vfat_ ==9 or vfat_ == 17)) : vfat_cont =0.0
                        if( i==7  and ( vfat_ ==9 or vfat_ == 10 or vfat_ ==11 or vfat_ == 12 or vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0    
                        if( i==10  and ( vfat_ == 10 or vfat_ ==11 or vfat_ == 12 or vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0    
                        if( i==12  and (vfat_ ==23)) : vfat_cont =0.0
                        if( i==14  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==16  and ( vfat_ == 10 or vfat_ ==11 or vfat_ == 12 or vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0                   
                        if( i==17 and (vfat_ <= 24)) : vfat_cont =0.0  
                        if( i==25  and ( vfat_ ==9 or vfat_ == 10 or vfat_ ==11 or vfat_ == 12 or vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0    

                        if( i==26 and (vfat_ ==16 or vfat_ ==8 or vfat_ ==15 or vfat_ ==6 or vfat_ ==7)) : vfat_cont =0.0
                        if( i==29  and ( vfat_ ==10 or vfat_ ==11 or vfat_ == 12 or  vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0    
                        if( i==31  and ( vfat_ ==10 or vfat_ ==11 or vfat_ == 12 or  vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0    
                        if( i==32 and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==33 and (vfat_ == 9)) : vfat_cont =0.0
                        if( i==36  and (vfat_ <= 24)) : vfat_cont =0.0

                    if(j == 2 and histPM=="GE11-P" ):
                        if( i==1  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==2  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==3  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==8  and ( vfat_ == 10 or vfat_ ==11 or vfat_ == 12 or vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0                   
                        if( i==9  and (vfat_ == 24)) : vfat_cont =0.0
                        if( i==15  and (vfat_ == 22)) : vfat_cont =0.0
                        if( i==16  and ( vfat_ == 1 or vfat_ ==2 or vfat_ == 3 or vfat_ ==4 or  vfat_==5 or  vfat_ ==6 or  vfat_ ==7 or  vfat_ ==9 or  vfat_ ==17 )) : vfat_cont =0.0                   
                        if( i==17  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==18 and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==19 and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==20  and ( vfat_ == 1 or vfat_ ==2 or vfat_ == 3 or vfat_ ==4 or  vfat_==5 or  vfat_ ==6 or  vfat_ ==7 or  vfat_ ==9 or  vfat_ ==17 )) : vfat_cont =0.0                     
                        if( i==24 and (vfat_ ==9)) : vfat_cont =0.0
                        if( i==25  and ( vfat_ == 1 or vfat_ ==2 or vfat_ == 3 or vfat_ ==4 or  vfat_==5 or  vfat_ ==6 or  vfat_ ==7 or  vfat_ ==9 or  vfat_ ==17 )) : vfat_cont =0.0                     
                        if( i==28 and (vfat_ ==22)) : vfat_cont =0.0
                        if( i==29  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==31  and ( vfat_ == 10 or vfat_ ==11 or vfat_ == 12 or vfat_ ==18 or  vfat_==19 or  vfat_ ==20 or  vfat_ ==21 or  vfat_ ==22 or  vfat_ ==23 )) : vfat_cont =0.0                   
                        if( i==32  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==33  and (vfat_ <= 24)) : vfat_cont =0.0
                        if( i==36  and (vfat_ == 22 or vfat_ == 23 )) : vfat_cont =0.0
                    ''' 
                        #
                    #if( i==14 and j == 2 and histPM=="GE11-M" and vfat_ == 22) : vfat_cont =0.0
                    #if( i==22 and j == 2 and histPM=="GE11-P" and vfat_ == 21) : vfat_cont =0.0
                    #if( i==9 and j == 2 and histPM=="GE11-P" and runnumber =="356670" and vfat_ == 24) : vfat_cont =0.0
                    #if( i==26 and j == 1 and histPM=="GE11-P" and runnumber =="357452" and vfat_ == 22) : vfat_cont =0.0
                    #if( i==14 and j == 1 and histPM=="GE11-M" and runnumber =="357452" and vfat_ == 22) : vfat_cont =0.0
                    #if( i==5 and j == 2 and histPM=="GE11-M" and runnumber =="357962") : vfat_cont =0.0
                    #if( i==5 and j == 1 and histPM=="GE11-P") : vfat_cont =0.0

                    #print("vfat content",vfat_, vfat_cont)
                    #it has just 5 codes: 0, 1, 2, 3 and 4, which mean that 'nothing', 'with digi and no error/warning', 'error', 'warning', 'low error'
                    if (vfat_cont == 0.0 or vfat_cont == 2.0 or vfat_cont == 3.0 or vfat_cont == 4.0):
                    #    print( " i am here ",vfat_)
                        listvfat_off_h.append(vfat_)
                        if j==1 : listvfat_off_L1_h.append(vfat_)
                        if j==2 : listvfat_off_L2_h.append(vfat_)


                        

                listvfat_off=[]
                listvfat_off_L1=[]
                listvfat_off_L2=[]
                for ibiny in range(1,nbinY+1):
                    striplist=[]
                    tmpstriplist=[]
                    for ibinx in range(1,nbinX+1):
                        ## remove the vfat that were disconnected 
                        nvfat_=extract_vfat(ibinx,ibiny)                       
                        if hist.GetBinContent(ibinx,ibiny)<threshold:
                            if (nvfat_ not in listvfat_off_h) : #continue
                                tmpstriplist.append(ibinx)
                        if(ibinx % 128  == 0):
                            if(len(tmpstriplist) != 128):
                                striplist = striplist + tmpstriplist
                                tmpstriplist_ = tmpstriplist

                            if (len(tmpstriplist) != 0 ) : 
                                str_to_print_layer_v= "{},{},{},{},{},{},{}  \n".format(fullname,region,i,j,(nvfat_-1),1,len(tmpstriplist))
                            if(len(tmpstriplist) ==0 and nvfat_ not in listvfat_off_h) :
                                str_to_print_layer_v= "{},{},{},{},{},{},{}  \n".format(fullname,region,i,j,(nvfat_-1),1,0)
                            if (nvfat_ in listvfat_off_h) : 
                                str_to_print_layer_v= "{},{},{},{},{},{},{}  \n".format(fullname,region,i,j,(nvfat_-1),1,-1)
                            v_deadchannel_L1.write(str_to_print_layer_v)
                            tmpstriplist=[]

                        
                        str_to_print= "{}     {}      {}     {} \n".format(fullname,ibiny,len(striplist),striplist)
                    #to print only the strip that are disconnected per chamber based on ieta    
                    str_to_print_layer= "{}     {}      {}     {} \n".format(fullname,ibiny,len(striplist),striplist)
                    striplistchamber=striplistchamber+striplist
                    if (j==1 and len(striplist) > 0 ): f_deadchannel_L1.write(str_to_print_layer)
                    if (j==2 and len(striplist) > 0 ): f_deadchannel_L2.write(str_to_print_layer)
                    if(len(striplist) > 0) :
                        f_deadchannel.write(str_to_print)
                f_deadchannel.write("\n")        
        


                #adding plot of active % of channel per chamver and % of OFF vffat for thhat

                
                
                if j==1: 
                    layer1.append(len(striplistchamber))  
                    vfatlayer1.append(len(listvfat_off_L1_h))
                if j==2:
                    layer2.append(len(striplistchamber))
                    vfatlayer2.append(len(listvfat_off_L2_h))
                

                if(len(listvfat_off_L1_h)>0):
                    if j==1 :
                        vfat_off_L1 += len(listvfat_off_L1_h) 
                        vfat_str_to_print_h= "Inhist {} : {} ".format(fullname,listvfat_off_L1_h)
                        LIST_CH_L1.append(vfat_str_to_print_h)
                        dictdead_l1[fullname] = listvfat_off_L1_h
                if(len(listvfat_off_L2_h)>0):
                    if j==2 :
                        vfat_off_L2 += len(listvfat_off_L2_h) 
                        vfat_str_to_print_h= "Inhist {} : {} ".format(fullname,listvfat_off_L2_h)
                        LIST_CH_L2.append(vfat_str_to_print_h)
                        dictdead_l2[fullname] = listvfat_off_L2_h

        print("vfat_off_L1 and vfat_off_L2",vfat_off_L1,vfat_off_L2)                
        f_deadchannel_L1.write("VFAT OFF : ")                
        f_deadchannel_L1.write(" \n")                
        f_deadchannel_L1.write(str(dictdead_l1))
        f_deadchannel_L1.write(" \n")                
        f_deadchannel_L1.write("Chamber OFF : ")                
        f_deadchannel_L1.write(" \n")                
        f_deadchannel_L1.write(str(list_choff_L1))
        f_deadchannel_L2.write("VFAT OFF ")                
        f_deadchannel_L2.write(" \n")                
        f_deadchannel_L2.write(str(dictdead_l2)) 
        f_deadchannel_L2.write(" \n")                
        f_deadchannel_L2.write("Chamber OFF : ")                
        f_deadchannel_L2.write(" \n")                
        f_deadchannel_L2.write(str(list_choff_L2))



        with j_deadchannel_L1 as convert_file:
            convert_file.write(json.dumps(dictdead_l1))
        with j_deadchannel_L2 as convert_file:
            convert_file.write(json.dumps(dictdead_l2))

                   

        
        #active disconnected number on based of vfat
        nchoff1 =float((vfat_off_L1)/864.)*100
        nchoff2 =float((vfat_off_L2)/864.)*100
        
        deadch1 =  sum(layer1) 
        totalokaych1 = (864-vfat_off_L1)*128
        deadch2 =  sum(layer2)
        totalokaych2 = (864-vfat_off_L2)*128


        print("deadch1  : ",deadch1, "deadch2 :", deadch2)
        print("totalokaych1 : ", totalokaych1, " totalokaych2  :" ,totalokaych2, " nchoff1 :" ,nchoff1 , "nchoff2  :", nchoff2)

        if(totalokaych1 == 0): totalokaych1 = 1
        if(totalokaych2 == 0): totalokaych2 = 1

        
        perdeadch1=  ((float(deadch1)/float(totalokaych1)))*100.
        perdeadch2 = ((float(deadch2)/float(totalokaych2)))*100.
        
        perdeadtot1 = ((float(sum(layer1))/float(36.*3072.)))*100.
        perdeadtot2 = ((float(sum(layer2))/float(36.*3072.)))*100.


        f2= open("DeadChannels.txt","a")
        pn= txtfilename.split('.txt')[0].split('_')[-1]
        print(pn)
        if( mode =='w'):
            #f2.write('                                   '+'Excluding the VFAT off'+'         Including the VFAT off'+'\n')
            f2.write('run'+'      '+'Endcap'+'           '+'Layer'+'  '+'%Channeloff'+'    '+'%activeCH'+'  \n') 
        if(pn=='Minus'):
            f2.write(runnumber +'      '+pn+'            '+'L1'+'     '+str(round(nchoff1,2))+'     '+str(round(100-perdeadch1,2)) +   '\n')
            f2.write(runnumber +'      '+pn+'            '+'L2'+'     '+str(round(nchoff2,2))+'     '+str(round(100-perdeadch2,2)) +   '\n')
        if(pn=='Positive'):
            f2.write(runnumber +'      '+pn+'         '+'L1'+'     '+str(round(nchoff1,2))+'     '+str(round(100-perdeadch1,2)) +   '\n')
            f2.write(runnumber +'      '+pn+'         '+'L2'+'     '+str(round(nchoff2,2))+'     '+str(round(100-perdeadch2,2)) +   '\n')

        f2.close()         

        f_deadchannel.close()
        filen="LowThreshold_withoutcuts/"+txtfilename.split('.txt')[0]+"_"+runnumber+ ".root"
        fout = TFile(filen,"RECREATE")

        h_layer1 = TH1F("h_layer1","h_layer1",36,0.5,36.5)
        h_layer2 = TH1F("h_layer2","h_layer2",36,0.5,36.5)
        h_layer1_inactive = TH1F("h_layer1_inactive","h_layer1_inactive",36,0.5,36.5)
        h_layer2_inactive = TH1F("h_layer2_inactive","h_layer2_inactive",36,0.5,36.5)
        h_layer1_vfat = TH1F("h_layer1_vfat","hvfat_layer1",36,0.5,36.5)
        h_layer2_vfat = TH1F("h_layer2_vfat","hvfat_layer2",36,0.5,36.5)
        
        #print("layer1",layer1)
        #print("listvaftoff", vfatlayer1)
        for ibin in range(len(layer1)):
            if(vfatlayer1[ibin]>0):
                nchnoffL1=float(vfatlayer1[ibin]*128)/float(24*128)
            if (vfatlayer1[ibin] == 0):
                nchnoffL1 =0

            if(vfatlayer1[ibin] ==24): 
                tchnL1=0.
                tchnL1_a=0.
            if(vfatlayer1[ibin] < 24):    
                tchnL1=(float(layer1[ibin])/float((24-vfatlayer1[ibin])*128))
                tchnL1_a=1.-tchnL1

            if(vfatlayer2[ibin]>0):
                nchnoffL2=float(vfatlayer2[ibin]*128)/float(24*128)
            if (vfatlayer2[ibin] == 0):  nchnoffL2 =0

            if(vfatlayer2[ibin] ==24): 
                tchnL2=0.
                tchnL2_a=0.
            if(vfatlayer2[ibin] < 24):    
                tchnL2=(float(layer2[ibin])/float((24-vfatlayer2[ibin])*128))
                tchnL2_a=1.-tchnL2
            

            h_layer1.SetBinContent(ibin+1,tchnL1_a)
            h_layer2.SetBinContent(ibin+1,tchnL2_a)
            h_layer1_inactive.SetBinContent(ibin+1,tchnL1)
            h_layer2_inactive.SetBinContent(ibin+1,tchnL2)
            h_layer1_vfat.SetBinContent(ibin+1,nchnoffL1)
            h_layer2_vfat.SetBinContent(ibin+1,nchnoffL2)
            #print("nchnoffL1",nchnoffL1)




        # os.system('mv  '+myeos+file_+'  ' +eosdir)
        # path = eosdir+file_
        #path = file_
        
    
       
        canvas = ROOT.TCanvas('c', '', 1000, 350)
        gStyle.SetOptTitle(0);
        gStyle.SetOptStat(0);

 
        h_layer1.SetMarkerSize(1.8);
#        gROOT.ForceStyle();
        h_layer1.Draw("histtext45")
        if 'eff' in hist.GetName():
            titlename = "Efficiency"
        else :
            titlename =""
            
            
        h_layer1.GetYaxis().SetTitle("#Strip")
        h_layer1.GetYaxis().SetTitleSize(0.092)
        h_layer1.GetXaxis().SetTitleSize(0.042)
        h_layer1.GetYaxis().SetTitleOffset(0.48)
        h_layer1.GetXaxis().SetTitleOffset(0.38)
        h_layer1.GetYaxis().SetTitleFont(22)
        h_layer1.GetYaxis().SetLabelFont(22)
        h_layer1.GetYaxis().SetLabelSize(.092)
        h_layer1.GetXaxis().SetLabelSize(0.0000);
        #h_layer1.GetXaxis().SetTitle("Chamber")
        h_layer1.GetXaxis().SetLabelSize(0.082)
        h_layer1.SetTitle(txtfilename.split('.txt')[0])
        # h_layer1.GetXaxis().SetTitleOffset(0.18)
        h_layer1.GetXaxis().SetTitleFont(22)
        h_layer1.GetXaxis().SetTickLength(0.07)
        h_layer1.GetXaxis().SetLabelFont(22)
        #h_layer1.GetYaxis().SetNdivisions(510)
        canvas.SaveAs(pltdir+txtfilename.split('.txt')[0]+"_L1.png")
        canvas.SaveAs(pltdir+txtfilename.split('.txt')[0]+"_L1.pdf")
        







        canvas1 = ROOT.TCanvas('c1', '', 1000, 350)
        gStyle.SetOptTitle(0);
        gStyle.SetOptStat(0);

 
        h_layer2.SetMarkerSize(1.8);
#        gROOT.ForceStyle();
        h_layer2.Draw("histtext45")
        if 'eff' in hist.GetName():
            titlename = "Efficiency"
        else :
            titlename =""
            
            
        h_layer2.GetYaxis().SetTitle("#Strip")
        h_layer2.GetYaxis().SetTitleSize(0.092)
        h_layer2.GetXaxis().SetTitleSize(0.042)
        h_layer2.GetYaxis().SetTitleOffset(0.48)
        h_layer2.GetXaxis().SetTitleOffset(0.38)
        h_layer2.GetYaxis().SetTitleFont(22)
        h_layer2.GetYaxis().SetLabelFont(22)
        h_layer2.GetYaxis().SetLabelSize(.092)
        h_layer2.GetXaxis().SetLabelSize(0.0000);
        #h_layer2.GetXaxis().SetTitle("Chamber")
        h_layer2.GetXaxis().SetLabelSize(0.082)
        h_layer2.SetTitle(txtfilename.split('.txt')[0])
        # h_layer2.GetXaxis().SetTitleOffset(0.18)
        h_layer2.GetXaxis().SetTitleFont(22)
        h_layer2.GetXaxis().SetTickLength(0.07)
        h_layer2.GetXaxis().SetLabelFont(22)
        #h_layer2.GetYaxis().SetNdivisions(510)
        canvas1.SaveAs(pltdir+txtfilename.split('.txt')[0]+"_L2.png")
        canvas1.SaveAs(pltdir+txtfilename.split('.txt')[0]+"_L2.pdf")
        #canvas1.SaveAs("LowThreshold_test_1/"+txtfilename.split('.txt')[0]+"_"+h_layer2.GetName() + '.root')
        fout.cd()
        h_layer1.Write()
        h_layer2.Write()
        h_layer1_vfat.Write()
        h_layer2_vfat.Write()
        h_layer1_inactive.Write()
        h_layer2_inactive.Write()

        #fout.Close()
        return True

    
        
        
    else:
        print('   + ERROR! ' + str(output[0]))
        print("Skipping " + url)
        print("Please check the name of the file: "+url)
        sys.exit('Exiting...');
        return False




#funtion for vfat/eta conversion



def extract_vfat(channel,ieta):
    vfat=-1
    if(channel <= 128):
        if(ieta == 8) : vfat = 1
        if(ieta == 7) : vfat = 2
        if(ieta == 6) : vfat = 3
        if(ieta == 5) : vfat = 4
        if(ieta == 4) : vfat = 5
        if(ieta == 3) : vfat = 6
        if(ieta == 2) : vfat = 7
        if(ieta == 1) : vfat = 8
    if((channel >= 129) and (channel <= 256)  ):
        if(ieta == 8) : vfat = 9
        if(ieta == 7) : vfat = 10
        if(ieta == 6) : vfat = 11
        if(ieta == 5) : vfat = 12
        if(ieta == 4) : vfat = 13
        if(ieta == 3) : vfat = 14
        if(ieta == 2) : vfat = 15
        if(ieta == 1) : vfat = 16
    if((channel >= 257) and (channel <= 384) ):
        if(ieta == 8) : vfat = 17
        if(ieta == 7) : vfat = 18
        if(ieta == 6) : vfat = 19
        if(ieta == 5) : vfat = 20
        if(ieta == 4) : vfat = 21
        if(ieta == 3) : vfat = 22
        if(ieta == 2) : vfat = 23
        if(ieta == 1) : vfat = 24
   
    return vfat     






def downloadfile_off(url):
    print('   + Downloading "' + url + '"...')
    nlevels = 6;
     
    clevels = [0, 1, 2, 3, 4, 5];
    colors = [1,2,3,4,5]
    palette =['kWhite','kRed','kBlack','kPink'];
#    palette[0] = 15;
#    palette[1] = 20;
#    palette[2] = 23;
#    palette[3] = 30;
#    palette[4] = 32;

    
    
    file_= url.split('/')[-1] 
    path = file_
    #if not  os.path.isfile(path) :        
    #os.system('wget --ca-directory $X509_CERT_DIR/ --certificate=$X509_USER_PROXY --private-key=$X509_USER_PROXY '+url)
    stream = os.popen('/usr/bin/curl -k -O -L --capath $X509_CERT_DIR --key $X509_USER_PROXY --cert $X509_USER_PROXY -w "%{http_code}" '+ url)
    output=stream.readlines()
    if output[0]=='200':
        print('   + OK!')
        print('  + now moving file to eos directory  ')
     
        #file_= url.split('/')[-1]
        # os.system('mv  '+myeos+file_+'  ' +eosdir)
        # path = eosdir+file_
        #path = file_
        #histpath = "DQMData/Run 341343/GEM/Run summary/Efficiency/type1/Efficiency/chamber_GE+11_L1"
        histpath = "DQMData/Run 341343/GEM/Run summary/DAQStatus/summaryStatus"
        #histpath = histpath_tem.format(run=run)
        print( histpath)
        root_file = ROOT.TFile(path, "READ")
        hist = root_file.Get(histpath)
        
        #canvas = ROOT.TCanvas('c', '', 1600, 240)
        canvas = ROOT.TCanvas('c', '', 956, 80)
        canvas.SetTopMargin(29);
        gStyle.SetOptTitle(0);
        gStyle.SetOptStat(0);
        gROOT.ForceStyle();
        hist.GetYaxis().SetRangeUser(3.5,4.5)
        hist.SetContour(nlevels,clevels);
        gstyle.SetPalette(1);
        #h2->Draw("LEGO2");
        hist.Draw("col")
        if 'eff' in hist.GetName():
            titlename = "Efficiency"
        else :
            titlename =""
        
        canvas.cd()
        gPad.SetTopMargin(0.5);
        hist.GetYaxis().SetTitle(titlename)
        hist.GetYaxis().SetTitleSize(0.152)
        hist.GetYaxis().SetTitleOffset(0.18)
        hist.GetYaxis().SetTitleFont(22)
        hist.GetYaxis().SetLabelFont(22)
        hist.GetYaxis().SetLabelSize(.092)

        #hist.GetXaxis().SetTitle("VFAT")
        hist.GetXaxis().SetLabelSize(0.12)
        hist.GetXaxis().SetTitleSize(1.452)
       # hist.GetXaxis().SetTitleOffset(0.18)
        hist.GetXaxis().SetTitleFont(22)
        hist.GetXaxis().SetTickLength(0.07)
        hist.GetXaxis().SetLabelFont(22)
        hist.GetYaxis().SetNdivisions(510)

        canvas.SaveAs(hist.GetName() + '.png')


        return True

    else:
        print('   + ERROR! ' + str(output[0]))
        print("Skipping " + url)
        print("Please check the name of the file: "+url)
        sys.exit('Exiting...');
        return False




#if __name__ == '__main__':





ROOT.gROOT.SetBatch(True)
eosdir ="/eos/cms/store/group/dpg_gem/comm_gem/P5_Commissioning/2021/Calibration/ForAuto/"
myeos ="/eos/user/m/mmittal/SWAN_projects/GEMDPG/"
offline = "/offline/data/browse/ROOT/OfflineData/"
stream  ="StreamExpressCosmics"
period = "Commissioning2021"
run = "341343"
run_= "3413"

#/afs/cern.ch/work/m/mmittal/private/DeadChannelStudy/pfa/DigiHit/Monika/CMSSW_12_3_5/src/test/Outfiles/
file_path="/eos/cms/store/group/dpg_gem/comm_gem/P5_Commissioning/2021/Calibration/test/DeadChannel/Output/DQM_V0001_GEM_R000"
#runlist=["356670","356828","356990","357296","357452","357851","357962","357995","358132","358529","358567","358590","358647"]
#runlist=["358685","358726","358772","358772"]
#runlist=["359317","359398","359484","359644"]
#runlist=["359839","359891","360161"]

#def TextFileToList( textfile):
#    return [iline.rstrip() for iline in open (textfile)]

#runlist = TextFileToList("run_full.txt")
runlist=["366512","366382"]
for i in runlist:
    print(i)
    downloadfile(file_path+i+".root","GE11-M",'w')
    downloadfile(file_path+i+".root","GE11-P",'a')



