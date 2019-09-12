from os import system as sys
import os, time
import xml.etree.ElementTree as ET
import threading
import numpy as np
import csv



def PermListUpdater():
    #additionalPerm = []
    updateList = []
    defaultList = []
    with open('./PermList/UpdatePermList.txt') as updateFile:
        updatedata = updateFile.read()
        updateList = updatedata.split('\n')
    updateList.pop()
    with open('./PermList/DefaultPermList.txt') as defaultFile:
        defaultdata = defaultFile.read()
        defaultList = defaultdata.split('\n')
    defaultList.pop()

    newList=defaultList+list(set(updateList) - set(defaultList))

    with open('./PermList/UpdatedPermList.txt', 'w') as dumpFile:
        for i in newList:
            dumpFile.write(i+'\n')


def CSVFormatter():
    test_file=open("./PermList/UpdatedPermList.txt")
    data=test_file.read()
    test_file.close()

    permlist=data.split('\n')
    permlist.pop()

    csv_row_data=['NAME']
    csv_row_data += permlist
    csv_row_data.append('CLASS')

    with open('data.csv','w') as csv_file:
        writer=csv.writer(csv_file)
        writer.writerow(csv_row_data)

def Extract():
    DIRTYPE=["./MalwareAPK","./BenignAPK"]
    permCollection = set()


    for datastoredir in DIRTYPE:
        if datastoredir == "./MalwareAPK":
            apktype="MALWARE"
        else:
            apktype="BENIGN"
        Flag=1
        TimeStamp = str(time.time())
        Jdax = "./Modules/jadx/bin/jadx"
        TargetApkPath = datastoredir
        ApkNameList = os.listdir(datastoredir)
        if len(ApkNameList) == int(0):
            Flag=0

        if Flag != int(0):
            ApkNameList.sort()
            TargetApkPath = datastoredir+"/"
            CurrentApk = 0

            for ApkName in ApkNameList:
                TargetApk = TargetApkPath + ApkName

                print("("+str(apktype)+")"+ " [" + str(CurrentApk + 1) + ' / ' + str(len(ApkNameList)) + "] --- "+ApkName)
               
                sys(Jdax + " -d ./UnpackedApk/" + ApkName + TimeStamp + " " + TargetApk+ " >/dev/null" )#+ " >/dev/null"
                

                # UNPACK DIR LOCATION SET
                UnpackedDir = "./UnpackedApk/" + ApkName + TimeStamp
                MainfestPath = UnpackedDir + "/resources/AndroidManifest.xml"
                try:
                    root = ET.parse(MainfestPath).getroot()
                    permissions = root.findall("uses-permission")

                    print("SET STATUS :", end=' ')
                    for perm in permissions:
                        for att in perm.attrib:
                            permelement = perm.attrib[att]

                            if permelement in permCollection:
                                print("0", end=' ')
                            else:
                                print("1", end=' ')
                                permCollection.add(permelement)

                except FileNotFoundError:
                    print('Error')
                    print(TargetApk)
                    pass
                sys("rm -f -R " + UnpackedDir)
                print()
                CurrentApk += 1


    permList = list(permCollection)


    with open("./PermList/UpdatePermList.txt", 'w') as file:
        for i in permList:
            file.write(i + '\n')

def Bagger(datastoredir):
    if datastoredir == "./MalwareAPK":
        TYPE=1
        print("\n\t ** Extracting From Malware Samples ** \n\n")
    elif datastoredir =="./BenignAPK":
        TYPE=0
        print("\n\t ** Extracting From Benign Samples ** \n\n")
    permCollection = set()

    TimeStamp = str(time.time())
    # print(TimeStamp)
    Flag=1

    # JDAX LOCATION SET
    Jdax = "./Modules/jadx/bin/jadx"
    TargetApkPath = datastoredir+"/"
    ApkNameList = os.listdir(datastoredir)
    if len(ApkNameList) == int(0):
        Flag=0

    if Flag != int(0):
        ApkNameList.sort()
        TotalApks = len(ApkNameList)
        CurrentApk = 0
        #get field names
        fieldnames=[]
        with open('data.csv') as csv_file:
            CSVREADER=csv.DictReader(csv_file)
            fieldnames=CSVREADER.fieldnames

        csv_master_dict=dict.fromkeys(fieldnames,0)


        for ApkName in ApkNameList:
            TargetApk = TargetApkPath + ApkName

            print(">[" + str(CurrentApk + 1) + ' / ' + str(TotalApks) + "] --- "+ApkName ,end=' ')
            print("\t.",end=' ')
            sys(Jdax + " -d ./UnpackedApk/" + ApkName + TimeStamp + " " + TargetApk + " >/dev/null") #+ " >/dev/null"
            print(".",end=' ')

            # UNPACK DIR LOCATION SET
            UnpackedDir = "./UnpackedApk/" + ApkName + TimeStamp
            MainfestPath = UnpackedDir + "/resources/AndroidManifest.xml"

            try:
                root = ET.parse(MainfestPath).getroot()
                permissions = root.findall("uses-permission")
                csv_master_dict=dict.fromkeys(fieldnames,0)
                csv_master_dict['NAME']=ApkName
                csv_master_dict['CLASS']=TYPE
                # 1 for malware
                # 0 for safe/ benign
                for perm in permissions:
                    for att in perm.attrib:
                        permelement = perm.attrib[att]
                        csv_master_dict[permelement]=1
                sys("rm -f -R " + UnpackedDir)
                print(".", end=' ')
                with open('data.csv', 'a') as csv_dump:
                    CSVwriter = csv.DictWriter(csv_dump, fieldnames=fieldnames)
                    CSVwriter.writerow(csv_master_dict)
                print(".")
            except Exception:
                print("EERRRROORR")
                pass
            CurrentApk += 1


def Main():
    sys("rm './PermList/UpdatePermList.txt' './PermList/UpdatePermList2.txt' './PermList/UpdatedPermList.txt'")
    sys("touch './PermList/UpdatePermList2.txt' && touch './PermList/UpdatePermList.txt' ")
    Malware_Directory_Name="./MalwareAPK"
    Benign_Directory_Name="./BenignAPK"
    sys("clear")
    print("\tANDROID PERMISSION BASED DATASET CREATOR FOR ML MODELS \n\tGIT : https://github.com/Saket-Upadhyay/Android-Permission-Extraction-and-Dataset-Creation-with-Python\n\n")
    print("Extracting Permissions\t[*---]")
    Extract()
    print("\n\nCreating Base Permission List\t[**--]")
    PermListUpdater()
    print("\n\nCreating Base Dataset\t[***-]")
    CSVFormatter()
    print("\n\nCreating Main Dataset\t[****]")
    Bagger(Benign_Directory_Name)
    Bagger(Malware_Directory_Name)
    print("\n\n ***************DONE*****************  ")


if __name__ == '__main__':
    Main()