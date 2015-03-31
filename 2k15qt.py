from PySide.QtCore import *
from PySide.QtGui import *
#from PySide.phonon import Phonon


#pymedia
#import pymedia.audio.acodec as acodec
#import pymedia.audio.sound as sound
#import pymedia.muxer as muxer

from vlc_player import Player


#external imports
import gui2k
from dds import *
from pygl_widgets import *
from models_2k import Model2k


#internal imports
import sys,struct,time,threading,gc,pylzma,os,zlib,webbrowser,operator
from StringIO import StringIO
from subprocess import call
from collections import OrderedDict
from pylzma import compress
from pysideuic.Compiler.qtproxies import QtGui
#import pymedia

print(os.getcwd())
type_dict={0x44445320:'DDS',
           0xF07F68CA:'MODEL',
           0x7EA1CFBB:'OGG',
           0x305098F0:'CDF',
           0x94EF3BFF:'IFF',
           0x504B0304:'ZIP',
           0x5A4C4942:'ZLIB'}

archiveName_list= ['0A','0B','0C','0D','0E','0F','0G','0H','0I','0J','0K','0L','0M','0N','0O','0P','0Q','0R','0S','0T','0U','0V','0W','0X','0Y','0Z',
                   '1A','1B','1C','1D','1E','1F','1G','1H','1I','1J','1K','1L','1M','1N','1O','1P']

archiveName_discr=[' - Various 1',' - Various 2', ' - Retro, Euro Teams', ' - Sixers',' - Bucks',' - Bulls',' - Cavaliers',' - Celtics',' - Clippers',' - Grizzlies',' - Hawk',' - Heat',
' - Hornets',' - Jazz',' - Kings',' - Knicks',' - Lakers',' - Magic',' - Mavericks',' - Nets',' - Nuggets',' - Pacers',' - Pelicans',' - Pistons',' - Raptors',' - Rockets',' - Spurs',
' - Suns',' - Thunder',' - Timberwolves',' - Trailblazers',' - Warriors',' - Wizards',' - Shaq and Ernie',' - Shoes',' - Create A Player',' - Various Audio',' - English Commentary',' - Spanish Commentary',' - MyTeam, Thumbs', ' - Updates 1', ' - Updates 2']

#for i in range(len(archiveName_list)): archiveName_list[i]+=archiveName_discr[i]

archiveOffsets_list=[]
archiveName_dict = {}
settings_dict = {}
bool_dict = {'False':False,
             'True':True}
for i in range(len(archiveName_list)): archiveName_dict[archiveName_list[i]]=i
for i in range(len(archiveName_list)): settings_dict[archiveName_list[i]]="False"

index_table=[0x63000000,0x6E000000,0x73000000,0x74000000,0x70000000]

zip_types={0xE:'LZMA',0:'NONE'}

def read_string_2(f):
    c=''
    for i in range(128):
        s=struct.unpack('<H',f.read(2))[0]
        if not s:
            return c
        else:
            c+=chr(s)

def read_string_1(f):
    c=''
    for i in range(128):
        s=struct.unpack('B',f.read(1))[0]
        if not s:
            return c
        else:
            c+=chr(s)

def read_string_n(f,n):
    c=''
    for i in range(n):
        s=struct.unpack('B',f.read(1))[0]
        c+=chr(s)
    return c


class dataInitiate:
    def __init__(self,msg,datalen):
        self.msg=msg
        self.datalen=datalen

class scheduleItem: #not used keep thinking...
    def __init__(self,datadict):
        for key in datadict:
            setattr(self,key,datadict[key])

class sub_file:
    def __init__(self,data,typ,size):
        self.files=[]
        self.data=data
        self.size=size
        self.type=typ
        self.namelist=[]
        # ------
        #self.data.seek(0)
        #f=open('C:\\test','wb')
        #f.write(self.data.read())
        #f.close()
        #self.data.seek(0)
        # ------
        self._open()
    
    @staticmethod
    def _get_zip_info_offset(index,data):
        exit_flag=0
        i=0
        while True:
            id=struct.unpack('>I',data.read(4))[0]
            if id==0x504B0304:
                data.seek(0x4,1) #skip to compression mode
                c_type=struct.unpack('<H',data.read(2))[0]
                data.seek(0x8,1)#skip to size
                c_size=struct.unpack('<I',data.read(4))[0]
                d_size=struct.unpack('<I',data.read(4))[0]
                name_size=struct.unpack('<H',data.read(2))[0]
                extra_field_size=struct.unpack('<H',data.read(2))[0]
                name=read_string_n(data,name_size)#read file name
                data.seek(extra_field_size,1)
                data.seek(c_size,1)
            elif id==0x504B0102:
                data.seek(0xC,1)
                if i >= index:
                    break
                else:
                    i+=1
                data.seek(0x4,1)
                c_size=struct.unpack('<I',data.read(4))[0]
                d_size=struct.unpack('<I',data.read(4))[0]
                name_size=struct.unpack('<H',data.read(2))[0]
                extra_field_size=struct.unpack('<H',data.read(2))[0]
                data.seek(0xE,1)
                data.seek(name_size,1)
                data.seek(extra_field_size,1)
        return True

    @staticmethod
    def _get_zip_end_offset(data):
        exit_flag=0
        i=0
        while True:
            id=struct.unpack('>I',data.read(4))[0]
            if id==0x504B0304:
                data.seek(0x4,1) #skip to compression mode
                c_type=struct.unpack('<H',data.read(2))[0]
                data.seek(0x8,1)#skip to size
                c_size=struct.unpack('<I',data.read(4))[0]
                d_size=struct.unpack('<I',data.read(4))[0]
                name_size=struct.unpack('<H',data.read(2))[0]
                extra_field_size=struct.unpack('<H',data.read(2))[0]
                name=read_string_n(data,name_size)#read file name
                data.seek(extra_field_size,1)
                data.seek(c_size,1)
            elif id==0x504B0102:
                data.seek(0xC,1)
                data.seek(0x4,1)
                c_size=struct.unpack('<I',data.read(4))[0]
                d_size=struct.unpack('<I',data.read(4))[0]
                name_size=struct.unpack('<H',data.read(2))[0]
                extra_field_size=struct.unpack('<H',data.read(2))[0]
                data.seek(0xE,1)
                data.seek(name_size,1)
                data.seek(extra_field_size,1)
            elif id==0x504B0506:
                data.seek(0xC,1)
                break
        return True

 
    def _get_zip_offset(self,index):
        print('Seeking Inner File')
        self.data.seek(0)
        exit_flag=0
        i=0
        while True:
            id=struct.unpack('>I',self.data.read(4))[0]
            if id==0x504B0304:
                self.data.seek(0x4,1) #skip to compression mode
                c_type=struct.unpack('<H',self.data.read(2))[0]
                self.data.seek(0x8,1)#skip to size
                c_size=struct.unpack('<I',self.data.read(4))[0]
                d_size=struct.unpack('<I',self.data.read(4))[0]
                name_size=struct.unpack('<I',self.data.read(4))[0]
                name=read_string_n(self.data,name_size)#read file name
                if i >= index:
                    break
                else:
                    i+=1
                self.data.seek(c_size,1)
        ret=self.data.tell()
        self.data.seek(0)
        return ret
    
    def _zip_parser(self):
        self.data.seek(0)
        self.sects=[]
        self.infSects=[]
        exit_flag=0
        while not exit_flag:
            id=struct.unpack('>I',self.data.read(4))[0]
            if id==0x504B0304:
                self.data.seek(0x4,1) #skip to compression mode
                c_type=struct.unpack('<H',self.data.read(2))[0]
                self.data.seek(0x8,1)#skip to size
                c_size=struct.unpack('<I',self.data.read(4))[0]
                d_size=struct.unpack('<I',self.data.read(4))[0]
                name_size=struct.unpack('<H',self.data.read(2))[0]
                extra_field_size=struct.unpack('<H',self.data.read(2))[0]
                
                sec_offset=self.data.tell() - 30
                sec_size = 30 + name_size + extra_field_size
                
                name=read_string_n(self.data,name_size)#read file name
                self.data.seek(extra_field_size,1)
                
                self.namelist.append(name)

                #type=name.split('.')[-1]
                #type=type.upper()
                #print(name)
                self.files.append((name,self.data.tell(),c_size,zip_types[c_type]))
                self.sects.append((name,sec_offset,sec_size+c_size,'0x504B0304'))
                self.data.read(c_size)
            elif id==0x504B0102:
                self.data.seek(0x18,1)#skip to name size
                name_size=struct.unpack('<H',self.data.read(2))[0]
                extra_field_size=struct.unpack('<H',self.data.read(2))[0]
                self.data.read(0xE)#skip zeroes
                
                sec_offset=self.data.tell() - 46
                sec_size = 46 + name_size + extra_field_size
                
                name=read_string_n(self.data,name_size)#read file name
                self.data.seek(extra_field_size,1)
                self.infSects.append((name,sec_offset,sec_size,'0x504B0102'))
            elif id==0x504B0506:
                self.data.seek(0x12,1)
                sec_offset=self.data.tell() - 22
                sec_size = 22

                self.sects.append(('end',sec_offset,sec_size,'0x504B0506'))
                exit_flag=1
                stop=self.data.tell()
    
    def _get_file(self,index):
        name,off,size,type=self.files[index]
        print('Getting ', name,' Offset:',off, ' Type:',type, ' Size:',size)
        self.data.seek(off)
        t=StringIO()
        t.write(self.data.read(size))
        t.seek(0)
        
        if type=='LZMA':
            t.seek(4,1)
            k=StringIO()
            k.write(pylzma.decompress_compat(t.read()))
            t.close()
            k.seek(0)
            t=k
        return t
        
    def _open(self):
        gc.collect()
        if self.type=='ZIP':
            print('Opening ZIP file')
            #------
            self.data.seek(0)
            f=open('C:\\test','wb')
            f.write(self.data.read())
            f.close()
            self.data.seek(0)
            #------
            self._zip_parser() #populate class by parsing the zip
        elif self.type=='DDS':
            self.files=[('dds_file',0,self.size,'DDS')]
            self.namelist=['dds_file']
        elif self.type=='GZIP LZMA':
            self.data.seek(0xE,1)
            t=StringIO()
            t.write(pylzma.decompress_compat(self.data.read()))
            t.seek(0)
            self.data=StringIO() #swap buffers
            self.data.write(t.read())
            t.seek(0)
            typecheck=struct.unpack('>I',t.read(4))[0]
            self.size=4+len(t.read())
            t.close()
            try:
                self.type=type_dict[typecheck]
            except:
                self.type='UNKNOWN'
            self.data.seek(0)
            
            #print('Reopening')
            self._open()
        elif self.type=='ZLIB':
            print('Opening ZLIB file')
            self.data.seek(0x10,0)
            t=StringIO()
            t.write(zlib.decompress(self.data.read()))
            self.size=t.len
            t.seek(0)
            typecheck=struct.unpack('>I',t.read(4))[0]
            t.seek(0)
            try:
                typecheck=type_dict[typecheck]
                self.type=typecheck
            except:
                #Handle Zlib XML files
                self.type='XML'
                self.size-=0x10
                t.seek(0x10)
            self.data=StringIO()
            self.data.write(t.read())
            self.data.seek(0)
            t.close()
            self._open()
        elif self.type=='MODEL':
            self.files=[('model_file',0,self.size,'MODEL')]
            self.namelist=['model_file']
        elif self.type=='XML':
            self.files=[('xml_file',0,self.size,'XML')]
            self.namelist=['xml_file']
        else:
            print('Unknown type: ',hex(struct.unpack('>I',self.data.read(4))[0]))
        
class x38header:
    def __init__(self,f):
        self.id0=struct.unpack('<I',f.read(4))[0]
        self.id1=struct.unpack('<I',f.read(4))[0]
        self.type=struct.unpack('<Q',f.read(8))[0]
        self.size=struct.unpack('<Q',f.read(8))[0]
        self.comp_type=struct.unpack('<Q',f.read(8))[0]
        self.start=struct.unpack('<Q',f.read(8))[0]
        self.stop=struct.unpack('<Q',f.read(8))[0]
        f.read(8) #zeroes
    def write(self,f):
        f.write(struct.pack('<2I6Q',self.id0,self.id1,self.type,self.size,self.comp_type,self.start,self.stop,0))

class file_entry:
    def __init__(self,f,custom=False,offset=None,id0=None,id1=None,type=None,g_id=None,size=None,data=None):
        if not custom:
            self.off=f.tell()
            self.id0=struct.unpack('<I',f.read(4))[0]
            self.id1=struct.unpack('<I',f.read(4))[0]
            self.type=struct.unpack('<Q',f.read(8))[0]
            self.g_id=0 #used later
            self.size=0 #used later
            if self.type==1: #zlib or lzma data
                self.data=struct.unpack('<Q',f.read(8))
            elif self.type==2: # zip files
                self.data=struct.unpack('<2Q',f.read(16))
            elif self.type==3: # empty /separators?
                self.data=struct.unpack('<3Q',f.read(24))
            else:
                print('unknown type: ',self.type)
            #data[1] contains the file offsets
        else:
            #Create Custom fileEntry
            self.off=offset
            self.id0=id0
            self.id1=id1
            self.type=type
            self.g_id=g_id
            self.size=size
            self.data=data

class cdf_file_entry:
    def __init__(self,f,custom=False,offset=None,id0=None,id1=None,type=None,g_id=None,size=None,data=None):
        if not custom:
            self.off=struct.unpack('<Q',f.read(8))[0]
            self.size=struct.unpack('<Q',f.read(8))[0]
            f.seek(0x8,1)
            self.id0=0
            self.id1=0
            self.g_id=0
            self.type=0
            self.pad=struct.unpack('<Q',f.read(8))[0] #used later
        else:
            #Create Custom fileEntry
            self.off=offset
            self.id0=id0
            self.id1=id1
            self.type=type
            self.g_id=g_id
            self.size=size
            self.data=data

class header:
    def __init__(self,f):
        #self.main_offset=main_off
        self.magic=struct.unpack('>I',f.read(4))[0]
        #exceptions
        if self.magic==0x7EA1CFBB: #handle ogg  files
            f.seek(0x14,1)
            f_size=struct.unpack('<I',f.read(4))[0]+struct.unpack('<I',f.read(4))[0]-8
            f.seek(0xC,1)
            self.file_entries=[]
            self.file_entries.append((f.tell(),f_size))
            return
        elif self.magic==0x00000000:
            self.file_entries=[]
            self.file_entries.append((f.tell()-4,0))
            return
        elif self.magic in index_table:
            self.file_entries=[]
            self.file_entries.append((f.tell()-4,0))
            return
        elif self.magic==0x5A4C4942:
            self.file_entries=[]
            self.file_entries.append((f.tell()-4,0))
            return
        elif self.magic==0x504B0304: #zip files
            f.seek(-4,1)
            off=f.tell()
            subfile=sub_file(f,'ZIP',stop-off)
            self.file_entries=[]
            self.file_entries.append((off,stop-off))
            return
        elif self.magic in [0xC6B0581C,0x4A50922A,0xAAC40536]: #encrypted data
            self.file_entries=[]
            self.file_entries.append((f.tell()-4,0))
            return


        if not self.magic in [0x305098F0,0x94EF3BFF]:
            print('unknown magic ',self.magic)
            self.file_entries=[]
            self.file_entries.append((f.tell()-4,0))
            return



        self.header_length=struct.unpack('<I',f.read(4))[0]
        self.next_off=struct.unpack('>I',f.read(4))[0]
        f.read(4)
        self.sub_head_count=struct.unpack('<Q',f.read(8))[0] # x38 headers counter
        s = struct.unpack('<Q',f.read(8))[0]
        self.x38headersOffset = s + f.tell() - 8 - 1
        self.head_count=(s-9)//16 #additional information on the header counter
        self.file_count=struct.unpack('<Q',f.read(8))[0]
        self.sub_heads=[]
        #self.sub_heads.append(f.tell()-self.main_offset + struct.unpack('<Q',f.read(8))[0]-1)
        self.sub_heads.append(f.tell() + struct.unpack('<Q',f.read(8))[0]-1)
        if self.magic==0x305098F0 and self.head_count>1:
            #self.sub_heads.append(f.tell()-self.main_offset + struct.unpack('<Q',f.read(8))[0]-1)
            #self.sub_heads.append(f.tell()-self.main_offset + struct.unpack('<Q',f.read(8))[0]-1)
            self.sub_heads.append(f.tell() + struct.unpack('<Q',f.read(8))[0]-1)
            self.sub_heads.append(f.tell() + struct.unpack('<Q',f.read(8))[0]-1)

        f.seek(self.x38headersOffset)
        self.x38headers=[]
        for i in range(self.sub_head_count):
            self.x38headers.append(x38header(f))
        #Fix x38headers start
        #for x38 in self.x38headers:
        #    x38.start+=main_off
        self.sub_heads_data=[]
        self.file_entries=[]
        self.file_name=None
        self.file_sizes=[]

        #Store Basic Information (Included to all archives)
        
        #small_base=self.main_offset+f.tell()-1
        #small_base=f.tell()-1
        
        for x38 in self.x38headers:
            print('x38 Start: ',x38.start,'x38 Type: ',x38.type,'x38 CompType: ',x38.comp_type)
            if x38.type==1 and self.magic==0x94EF3BFF:
                print('IFF File Container')
                f.seek(self.sub_heads[0])
                small_base = self.sub_heads[0]-1
                print('File Description Offset Base: ',small_base, 'file_count: ',self.file_count)
                
                templist=[]
                small_base=0
                for j in range(self.file_count):
                    templist.append(struct.unpack('<Q',f.read(8))[0]+self.sub_heads[0]-1+small_base)
                    small_base+=8
                
                #print(templist)
                #force file_count for another weird kind of archives
                #if self.sub_head_count==1 and self.x38headers[0].type==8:      I will check if it works without this
                #    self.file_count=1
                g_id=0
                mode=0
                for j in range(self.file_count):
                    f.seek(templist[j])

                    temp=file_entry(f)
                    temp.g_id=g_id

                    if not temp.type==3:
                        if mode==0:
                            temp.size=temp.data[0]
                        else:
                            temp.size=temp.data[1]
                        self.file_entries.append(temp)
                    else:
                        if not temp.data[0]:
                            mode=1
                        else:
                            mode=0
                        g_id+=1

                #file sizes calculation and offsets
                stop=x38.stop
                for j in range(len(self.file_entries)-1):
                    self.file_sizes.append(self.file_entries[j+1].size-self.file_entries[j].size)
                self.file_sizes.append(stop-self.file_entries[-1].size) # store the last item size
                for entry in self.file_entries: # fix offsets
                    entry.size+=x38.start 
                    entry.off=entry.size

                self.sub_heads_data.append(templist) #Append templist
            elif x38.type==0x10:
                print('Zlib Section')
                temp=file_entry(f,custom=True,offset=None,id0='ZLIB',id1=None,type=None,g_id=0,size=x38.start,data=None)
                self.file_entries.append(temp)
                self.file_sizes.append(x38.size)
            elif x38.type==0x00 and x38.comp_type==0x00:
                pass #Empty Section
            elif x38.type==0x08 and x38.comp_type==0x00 and self.magic==0x94EF3BFF:
                pass #Empty Section
            elif x38.type==0x01 and x38.comp_type==0x00 and self.magic==0x305098F0:
                print('CDF File Container')
                big_base = self.sub_heads[1]-1 #Omitting practically FUCKING USELESS First Section
                f.seek(big_base+1)
                
                print('File Description Offset Base: ',big_base, 'file_count: ',self.file_count)
                
                templist=[]
                small_base=0
                for j in range(self.file_count):
                    templist.append(struct.unpack('<Q',f.read(8))[0]+big_base+small_base)
                    small_base+=8
                
                for j in range(self.file_count):
                    f.seek(templist[j])
                    self.file_entries.append(cdf_file_entry(f))
                
                #file sizes calculation and offsets
                for entry in self.file_entries: self.file_sizes.append(entry.size)
                for entry in self.file_entries: entry.off+=x38.start # fix offsets
                
                self.sub_heads_data.append(templist) #Append templist

                #Parse CDF File Name
                f.seek(self.sub_heads[-1])
                self.file_name=read_string_2(f)
            else:
                print('Unimplemented Type: ',x38.type)


        #if self.head_count>1 and self.head_count<4:
            #temp=[]
            #for j in range(self.file_count):
            #    temp.append(struct.unpack('<Q',f.read(8))[0]+small_base)
            #self.sub_heads_data.append(temp)
            #file sizes
            #self.file_sizes=[]
            #temp=[]
            #for j in range(self.file_count*self.sub_head_count):
            #    self.file_sizes.append(struct.unpack('<2Q',f.read(16)))
            #if self.sub_head_count>1:
            #    temp=self.file_sizes
            #    self.file_sizes=[]
            #    for j in range(self.file_count):
            #        self.file_sizes.append(temp[self.sub_head_count*j])
            
class ModelPanel(QDialog):
    def __init__(self):
        super(ModelPanel,self).__init__()
        
        self.mode=0
        self.resize(300,100)
        self.setWindowTitle('Model Panel')
        main_layout=QVBoxLayout()
            
        hor_layout=QHBoxLayout()
        
        
        lab=QLabel()
        lab.setText('Select Model Mode')
        hor_layout.addWidget(lab)
        main_layout.addLayout(hor_layout)
        
        but_group=QButtonGroup()
        hor_layout=QVBoxLayout()

        but=QRadioButton()
        but.setText('Stadium Models')
        self.stadium_but=but
        
        but_group.addButton(but)
        hor_layout.addWidget(but)

        but=QRadioButton()
        but.setText('Rest Models')
        self.rest_but=but
        
        but_group.addButton(but)
        hor_layout.addWidget(but)        
        
        
        

        main_layout.addLayout(hor_layout)
        
        hor_layout=QHBoxLayout()
        but=QPushButton()
        but.setText('Import')
        but.clicked.connect(self.changeMode)
        hor_layout.addWidget(but)
        
        main_layout.addLayout(hor_layout)
        self.setLayout(main_layout)
        
        
        
        
    def changeMode(self):
        if self.stadium_but.isChecked():
            self.mode=0
        else:
            self.mode=1
        self.close()
        
 
class ImportPanel(QDialog):
    img_type=['DXT1','DXT3','DXT5','RGBA', 'DXT5_NM']
    nvidia_opts=['-dxt1a','-dxt3','-dxt5','-u8888','-n5x5']
    mipMaps = [str(i+1) for i in range(13)]
    
    
    def __init__(self):
        super(ImportPanel, self).__init__()
        self.CurrentImageType = self.nvidia_opts[0]
        self.CurrentMipmap = self.mipMaps[11]
        self.swizzleFlag = True
        self.ImportStatus = False
        self.initUI()

        
    def initUI(self):               
        
        self.resize(250, 150)
        self.setWindowTitle('Texture Import Panel')
        main_layout = QVBoxLayout()
        
        sub_layout = QHBoxLayout()
        lab = QLabel()
        lab.setText('Texture Type')
        but = QComboBox()
        but.addItems(self.img_type)
        but.currentIndexChanged.connect(self.setImageType)
        sub_layout.addWidget(lab)
        sub_layout.addWidget(but)
        
        main_layout.addLayout(sub_layout)
        
        
        sub_layout = QHBoxLayout()
        lab = QLabel()
        lab.setText('Mipmaps')
        but = QComboBox()
        but.addItems(self.mipMaps)
        but.currentIndexChanged.connect(self.setMipmap)
        sub_layout.addWidget(lab)
        sub_layout.addWidget(but)
        
        main_layout.addLayout(sub_layout)
        
        sub_layout = QHBoxLayout()
        but = QCheckBox()
        but.setText('Swizzle')
        but.setChecked(True)
        but.stateChanged.connect(self.setSwizzleFlag)

        sub_layout.addWidget(but)
        main_layout.addLayout(sub_layout)


        sub_layout = QHBoxLayout()
        but = QPushButton()
        but.setText('Import')
        but.clicked.connect(self.imported_image)
        
        sub_layout.addWidget(but)
        main_layout.addLayout(sub_layout)        

        self.setLayout(main_layout)
        
    def imported_image(self):
        self.ImportStatus = True
        self.hide()
    
    def setImageType(self,index):
        self.CurrentImageType = self.nvidia_opts[index]
    
    def setMipmap(self,index):
        self.CurrentMipmap = self.mipMaps[index]
    def setSwizzleFlag(self):
        self.swizzleFlag = not self.swizzleFlag
        
class AboutDialog(QWidget):
    def __init__(self,parent=None):
        super(AboutDialog,self).__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(500,200)
        layout=QVBoxLayout()
        #main label
        lab=QLabel()
        lab.setAlignment(Qt.AlignCenter)
        lab.setText("<P><b><FONT COLOR='#000000' FONT SIZE = 5>NBA 2K15 Explorer v0.28</b></P></br>")
        layout.addWidget(lab)
        lab=QLabel()
        lab.setAlignment(Qt.AlignCenter)
        lab.setText("<P><b><FONT COLOR='#000000' FONT SIZE = 2>Coded by: gregkwaste</b></P></br>")
        layout.addWidget(lab)
        

        #textbox
        tex=QTextBrowser()
        f=open("about.html")
        tex.setHtml(f.read())
        f.close()
        tex.setOpenExternalLinks(True)
        tex.setReadOnly(True)
        layout.addWidget(tex)
        
        self.setLayout(layout)

class IffPanel(QWidget):
    def __init__(self,parent=None):
        super(IffPanel,self).__init__(parent)
        self.setWindowTitle("Iff Panel")
        self.setFixedSize(800,600)

class PreferencesWindow(QDialog):
    def __init__(self,parent=None):
        super(PreferencesWindow,self).__init__(parent)
        self.setWindowTitle("Preferences")
        self.mainDirectory='C:\\'
        self.preferences_checkFile()
        #self.pref_window.resize(500,300)
        
        
        horizontal_layout=QGridLayout(self)
        hpos=0
        vpos=0
        for i in range(len(archiveName_list)):
            op_name=archiveName_list[i]
            button=QCheckBox(self)
            button.setText(op_name+archiveName_discr[i])
            button.setChecked(bool_dict[settings_dict[op_name]])
            horizontal_layout.addWidget(button,hpos,vpos)
            vpos+=1
            if vpos>8:
                hpos+=1
                vpos=0


        horizontal_layout_2=QHBoxLayout()
        button=QPushButton()
        button.setText("Select All")
        button.clicked.connect(self.preferences_selectAll)
        horizontal_layout_2.addWidget(button)
        
        button=QPushButton()
        button.setText("Select None")
        button.clicked.connect(self.preferences_selectNone)
        horizontal_layout_2.addWidget(button)
        
        button=QPushButton()
        button.setText("Save Settings")
        button.clicked.connect(self.preferences_saveSettings)
        horizontal_layout_2.addWidget(button)
        
        horizontal_layout_3=QHBoxLayout()
        lab=QLabel()
        lab.setText("Select NBA 2K15 Directory: ")
        horizontal_layout_3.addWidget(lab)
        
        settingsLineEdit=QLineEdit()
        settingsLineEdit.setText(self.mainDirectory)
        settingsLineEdit.setReadOnly(True)
        horizontal_layout_3.addWidget(settingsLineEdit)
        
        settingsPathButton=QPushButton()
        settingsPathButton.setText("Select")
        settingsPathButton.clicked.connect(self.preferences_loadDirectory)
        horizontal_layout_3.addWidget(settingsPathButton)
        
        settingsLabel=QLabel()
        settingsLabel.setText("Select Archives to Load")
        
        settingsGroupBox=QGroupBox()
        settingsGroupBox.setLayout(horizontal_layout)
        settingsGroupBox.setTitle("Archives")
        
        layout=QVBoxLayout(self)
        layout.addLayout(horizontal_layout_3)
        

        layout.addWidget(settingsLabel)
        layout.addWidget(settingsGroupBox)
        layout.addLayout(horizontal_layout_2)
        
        self.setLayout(layout)
        self.pref_window_buttonGroup=settingsGroupBox
        self.pref_window_Directory=settingsLineEdit



        #Preferences Window Functions
    def preferences_checkFile(self):
        ###Try parsing Settings File
        try:
            sf=open('settings.ini','r')
            sf.readline()
            sf.readline()
            self.mainDirectory=sf.readline().split(' : ')[-1][:-1]
            print(self.mainDirectory)
            set=sf.readlines()
            for setting in set:
                settings_dict[setting.split(' : ')[0]]=setting.split(' : ')[1][:-1]
        except:
            msgbox=QMessageBox()
            msgbox.setWindowTitle("Warning")
            msgbox.setText("Settings file not found. Please set your preferences")
            msgbox.exec_()
            

    def preferences_selectAll(self):
        for child in self.pref_window_buttonGroup.children():
                if isinstance(child, QCheckBox):
                    child.setChecked(True)
    def preferences_selectNone(self):
        for child in self.pref_window_buttonGroup.children():
                if isinstance(child, QCheckBox):
                    child.setChecked(False)
    def preferences_saveSettings(self):
        f=open('settings.ini','w')
        f.writelines(('NBA 2K Explorer Settings File \n','Version 0.1 \n'))
        f.write('NBA 2K15 Path : '+self.mainDirectory+'\n')
        for child in self.pref_window_buttonGroup.children():
            if isinstance(child, QCheckBox):
                f.write(child.text().split(' ')[0]+' : '+str(child.isChecked())+'\n')
        f.close()
        print('Settings Saved')
                
    def preferences_loadDirectory(self):
        selected_dir=QFileDialog.getExistingDirectory(caption="Choose Export Directory")
        self.pref_window_Directory.setText(selected_dir)
        self.mainDirectory=selected_dir

class TreeItem(object):
    def __init__(self, data, parent=None):
        self.parentItem = parent
        self.itemData = data
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return len(self.itemData)

    def data(self, column):
        try:
            return self.itemData[column]
        except IndexError:
            return None

    def parent(self):
        return self.parentItem

    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)

        return 0


class TreeModel(QAbstractItemModel):
    progressTrigger=Signal(int)
    def __init__(self, columns , parent=None):
        super(TreeModel, self).__init__(parent)

        self.rootItem = TreeItem(columns)
        #self.setupModelData(data, self.rootItem)

    def columnCount(self, parent):
        if parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return self.rootItem.columnCount()

    def data(self, index, role):
        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        item = index.internalPointer()

        return item.data(index.column())

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.rootItem.data(section)

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QModelIndex()

        childItem = index.internalPointer()
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        return parentItem.childCount()

    #load list to viewer
    def setupModelData(self, data, parent,settings):
        print('Parsing Settings')
        selected_archives=[]
        for child in settings.children():
            if isinstance(child, QCheckBox):
                if child.isChecked():
                    selected_archives.append(archiveName_dict[child.text().split(' ')[0]])
        
        print(selected_archives)
        print('Setting up data')
        step=0
        for i in selected_archives:
            step+= len(data[i][3])
        step=float(step/100)
        prog=0
        count=0
        for i in selected_archives:
            entry=data[i]
            arch_parent=TreeItem((entry[0],entry[1],entry[2]),parent)
            parent.appendChild(arch_parent)
            for kid in entry[3]:
                arch_parent.appendChild(TreeItem((kid[0],int(kid[1]),int(kid[2]),kid[3]),arch_parent))
                if count>step:
                    prog+=1
                    self.progressTrigger.emit(prog)
                    QCoreApplication.sendPostedEvents()
                    count=0
                else:
                    count+=1
        self.progressTrigger.emit(100)
            
class MyTableModel(QAbstractTableModel):
    def __init__(self, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent=None, *args)
        self.mylist = mylist
        self.header = header
    def rowCount(self, parent):
        return len(self.mylist)
    def columnCount(self, parent):
        return len(self.mylist[0])
    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]
    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None
    def sort(self, col, order):
        """sort table by given column number col"""
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.mylist = sorted(self.mylist,
            key=operator.itemgetter(col))
        if order == Qt.DescendingOrder:
            self.mylist.reverse()
        self.emit(SIGNAL("layoutChanged()"))

    def findlayer(self, name):
        """
        Find a layer in the model by it's name
        """
        print('Searching')
        startindex = self.index(0, 0)
        items = self.match(startindex, Qt.DisplayRole, name, 1, Qt.MatchExactly | Qt.MatchWrap | Qt.MatchContains)
        try:
            print(items)
            return items[0]
        except IndexError:
            return QModelIndex()


class SortModel(QSortFilterProxyModel):
    def __init__(self,parent=None):
         super(SortModel,self).__init__(parent)
         self.model=self.sourceModel()
    def lessThan(self, left, right):
         #print(left,right)
         leftData = self.sourceModel().data(left,self.sortRole())
         rightData = self.sourceModel().data(right,self.sortRole())

         try:
             return int(leftData) < int(rightData)
         except ValueError:
             return leftData < rightData

    def filterAcceptsRow(self, row_num, source_parent):
        ''' Overriding the parent function '''
        model = self.sourceModel()
        source_index = model.index(row_num, 0, source_parent)
        offset_index = model.index(row_num, 1, source_parent)

        if self.filterRegExp().pattern() in model.data(source_index,Qt.DisplayRole) or \
           self.filterRegExp().pattern() in str(model.data(offset_index,Qt.DisplayRole)):
            return True
        return False

class MainWindow(QMainWindow,gui2k.Ui_MainWindow):
    def __init__(self,parent=None):
        super(MainWindow,self).__init__(parent)
        self.setWindowIcon(QIcon('tool_icon.ico'))
        self.setupUi(self)
        self.actionOpen.triggered.connect(self.open_file_table)
        self.actionExit.triggered.connect(self.close_app)
        self.actionApply_Changes.triggered.connect(self.runScheduler)
        self.actionPreferences.triggered.connect(self.preferences_window)
        self.clipboard=QClipboard()

        self.prepareUi()
        
        self.pref_window=PreferencesWindow() # preferences window
        self.iffPanel=IffPanel()

        #self properties
        self._active_file=None
        self.list=[]
        
        
        #About Dialog
        about_action=QAction(self.menubar)
        about_action.setText("About")
        about_action.triggered.connect(self.about_window)
        self.menubar.addAction(about_action)
        
        self.about_dialog=AboutDialog() # Create About Dialog
        
    def prepareUi(self):
        self.main_viewer_sortmodels=[] #List for sortmodels storage
        self.current_sortmodel=None
        self.current_tableView=None
        self.current_tableView_index=None
        
        #Active File Data Attribs
        self._active_file_data=None
        self._active_file_handle=None
        self._active_file_path=None

        #ArchiveTabs Wigdet Functions
        self.archiveTabs.currentChanged.connect(self.set_currentTableData)

        #SearchBar Options
        self.searchBar.returnPressed.connect(self.mainViewerFilter)
        

        #Subfiles Treeview settings
        self.treeView_2.clicked.connect(self.read_subfile)
        self.treeView_2.activated.connect(self.read_subfile)
        #self.treeView_2.entered.connect(self.read_subfile)
        
        self.treeView_2.setUniformRowHeights(True)
        self.treeView_2.header().setResizeMode(QHeaderView.Stretch)
        
        #Treeview 2 context menu
        self.treeView_2.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.treeView_2.customContextMenuRequested.connect(self.ctx_menu)
        
        #Subfile Contents Treeview settings
        self.treeView_3.clicked.connect(self.open_subfile)
        #self.treeView_3.entered.connect(self.open_subfile)
        
        self.treeView_3.setUniformRowHeights(True)
        self.treeView_3.header().setResizeMode(QHeaderView.Stretch)
        
        #GLWIDGET
        self.glviewer=GLWidgetQ(self)
        self.splitter_4.addWidget(self.glviewer)
        self.glviewer.renderText(0.5,0.5,"3dgamedevblog")
        #self.glviewer.changeObject()
        
        #self.glviewer.cubeDraw()
        
        #Media Widget
        self.sound_player=Player()
        self.tabWidget.addTab(self.sound_player.widget,"Media Player")
        
        #Text Editor Tab
        self.text_editor=QPlainTextEdit()
        self.tabWidget.addTab(self.text_editor,"Text Editor")
        
        #Import Scheduler
        self.scheduler = QTreeView()
        self.scheduler.setUniformRowHeights(True)
        self.schedulerFiles=[]
        #self.scheduler.header().setResizeMode(QHeaderView.Stretch)
        self.scheduler_model = None
        self.tabWidget.addTab(self.scheduler,'Import Scheduler')
        
        #Statusbar
        self.progressbar=QProgressBar()
        self.progressbar.setMaximumSize(500,19)
        self.progressbar.setAlignment(Qt.AlignRight)
        #self.main_viewer_model.progressTrigger.connect(self.progressbar.setValue)
        
        
        #3dgamedevblog label
        #image_pix=QPixmap.fromImage(image)
        self.status_label=QLabel()
        #self.connect(self.status_label, SIGNAL('clicked()'), self.visit_url)
        self.status_label.setText("<a href=\"https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=arianos10@gmail.com&lc=US&item_name=3dgamedevblog&amount=5.00&currency_code=USD&no_note=0&bn=PP-DonationsBF:btn_donateCC_LG.gif:NonHostedGuest\">Donate to 3dgamedevblog</a>")
        self.status_label.setTextFormat(Qt.RichText)
        self.status_label.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.status_label.setOpenExternalLinks(True)
        #self.status_label.setPixmap(image_pix)
        
        #self.statusBar.addPermanentWidget(self.progressbar)
        self.statusBar.addPermanentWidget(self.status_label)
        self.statusBar.showMessage('Ready')

        #Shortcuts
        #shortcut=QShortcut(QKeySequence(self.tr("Ctrl+F","Find")),self.treeView)
        #shortcut.activated.connect(self.find)
        
    def set_currentTableData(self,index):
        #Setting Current Sortmodel, to the Sortmodel of the TableView of the Current Tab
        self.current_tableView=self.archiveTabs.widget(index)
        self.current_sortmodel=self.current_tableView.model()
        self.current_tableView_index=QModelIndex()

    def mainViewerFilter(self):
        index=self.current_sortmodel.findlayer(self.searchBar.text())
        selmod=self.current_tableView.selectionModel()
        selmod.clear()
        selmod.select(index,QItemSelectionModel.Rows)
        self.current_tableView.setCurrentIndex(index)
    
    #Show Preferences Window
    def preferences_window(self):
        self.pref_window.show()
    
    #About Window
    def about_window(self):
        self.about_dialog.show()
    
    #Main Functions
    def visit_url(self):
        webbrowser.open('http:\\3dgamedevblog.com')
     
    def main_ctx_menu(self,position):
        selmod=self.current_tableView.selectionModel().selectedIndexes()
        arch_name=self.archiveTabs.tabText(self.archiveTabs.currentIndex())
        name=self.current_sortmodel.data(selmod[0],Qt.DisplayRole)
        off=self.current_sortmodel.data(selmod[1],Qt.DisplayRole)
        size=self.current_sortmodel.data(selmod[3],Qt.DisplayRole)

        menu=QMenu()
        menu.addAction(self.tr("Copy Offset"))
        menu.addAction(self.tr("Copy Name"))
        menu.addAction(self.tr("Import Archive"))
        menu.addAction(self.tr("Export Archive"))
        menu.addAction(self.tr("Open in IFF Editor"))
        
        res=menu.exec_(self.current_tableView.viewport().mapToGlobal(position))
        
        if not res: return
        
        if res.text()=='Copy Offset':
            self.clipboard.setText(str(off))
            self.statusBar.showMessage('Copied '+str(off)+ ' to clipboard.')
        elif res.text()=='Copy Name':
            self.clipboard.setText(str(name))
            self.statusBar.showMessage('Copied '+str(name)+ ' to clipboard.')
        elif res.text()=='Import Archive':
            print('Importing iff File over: ',name,off,size)

            location=QFileDialog.getOpenFileName(caption='Select .iff file',filter='*.iff')
            t=open(location[0],'rb')
            k=t.read() #store file temporarily
            t.close()
            #item=TreeItem((name,selmod,arch_name,subarch_name,subarch_offset,subfile_off,subfile_type,local_off,oldCompSize,newCompSize,diff),parent)
            #Scheduler Props
            selmod = 0
            arch_name = self._active_file.split('\\')[-1]
            subarch_name = name
            subarch_offset = off
            subarch_size = size
            subfile_name = ''
            subfile_off = 0
            subfile_type = 'IFF'
            subfile_index = 0
            subfile_size = 0
            local_off = 0
            oldCompSize = size
            oldDecompSize = size
            newCompSize = len(k)
            newDataSize = newCompSize
            chksm = zlib.crc32(k) 
            diff = newCompSize - oldCompSize

            if not self.scheduler_model:
                self.scheduler_model = TreeModel(("Name","ID","Archive","Subarchive Name", "Subarchive Offset", "Subarchive Size", "Subfile Index", "Subfile Name", "Subfile Offset", "Subfile Type","Subfile Size", "Local File Offset", "Old Decompressed Size", "New Decompressed Size", "Old Compressed Size", "New Compressed Size","CheckSum", "Diff"))
                gc.collect()
                self.scheduler.setModel(self.scheduler_model)
            
            parent = self.scheduler_model.rootItem
            item=TreeItem((name,selmod,arch_name,subarch_name,subarch_offset,subarch_size,subfile_index,subfile_name,subfile_off,subfile_type,subfile_size,local_off,oldDecompSize,newDataSize,oldCompSize,newCompSize,chksm,diff),parent)
            parent.appendChild(item)
            
            self.schedulerFiles.append(k)

        elif res.text()=='Export Archive':
            location=QFileDialog.getSaveFileName(caption="Save File",filter='*.iff')
            t=open(location[0],'wb')
            f=open(self._active_file,'rb')
            f.seek(off)
            t.write(f.read(size))
            f.close()
            t.close()
            self.statusBar.showMessage('Exported .iff to : '+ str(location[0]))
        elif res.text()=="Open in IFF Editor":
            print('Opening IFF Editor')
            self.iffPanel.show()
    
    
    def ctx_menu(self,position):
        selmod=self.treeView_2.selectedIndexes()
        
        subfile_name=self.file_list.data(selmod[0],Qt.DisplayRole) # file offset
        subfile_off=self.file_list.data(selmod[1],Qt.DisplayRole) # file offset
        subfile_typ=self.file_list.data(selmod[2],Qt.DisplayRole) # subfile type
        subfile_size=self.file_list.data(selmod[3],Qt.DisplayRole) # size offset

        if len(selmod)==0: #exit if there is nothing selected
            return
        menu=QMenu()
        menu.addAction(self.tr("Export"))
        #if subfile_typ=='ZIP':
        #    menu.addAction(self.tr("Fix ZIP"))

        res=menu.exec_(self.treeView_2.viewport().mapToGlobal(position))
        
        if not res: return

        if res.text()=='Export':
            self.export_items(selmod)
        #elif res.text()=='Fix ZIP':
        #    print('Fixing Zip')
        #    self.fixZip(subfile_off,subfile_size)


    def fixZip(self,off,size):
        #Loading zip to buffer
        t=StringIO()
        self._active_file.seek(off)
        t.write(self._active_file.read(size))
        zipfile=sub_file(t,'ZIP',size)
        t.seek(0)

        print(zipfile.sects)
        k=StringIO() #new zip
        
        #first file in the zip
        t.seek(zipfile.sects[0][1])
        data0=t.read(zipfile.sects[0][2])
        t.seek(zipfile.infSects[0][1])
        infdata0=t.read(zipfile.infSects[0][2])

        #second file in the zip
        t.seek(zipfile.sects[1][1])
        data1=t.read(zipfile.sects[1][2])
        t.seek(zipfile.infSects[1][1])
        infdata1=t.read(zipfile.infSects[1][2])        

        #writing the file sections
        k.write(data1)
        k.write(data0)
        #write the rest files
        for i in range(2,len(zipfile.sects)-1):
            t.seek(zipfile.sects[i][1])
            k.write(t.read(zipfile.sects[i][2]))
        
        #writing the info sections
        k.write(infdata1)
        k.write(infdata0)
        #write the rest files
        for i in range(2,len(zipfile.infSects)):
            t.seek(zipfile.infSects[i][1])
            k.write(t.read(zipfile.infSects[i][2]))

        #close the file
        t.seek(zipfile.sects[-1][1])
        k.write(t.read(zipfile.sects[-1][2]))


        #test the file
        k.seek(0)
        f=open('test.zip','wb')
        f.write(k.read())
        f.close()

        k.seek(0)

        k=k.read()
        chksm=zlib.crc32(k)
        

        #Schedule Item data:
        #Main archive Info
        parent_selmod=self.treeView.selectionModel().selectedIndexes()
        subarch_name=self.main_viewer_sortmodel.data(parent_selmod[0],Qt.DisplayRole)
        subarch_offset=self.main_viewer_sortmodel.data(parent_selmod[1],Qt.DisplayRole)
        subarch_size=self.main_viewer_sortmodel.data(parent_selmod[2],Qt.DisplayRole)
        #Subfile info
        parent_selmod=self.treeView_2.selectionModel().selectedIndexes()
        subfile_name=self.file_list.data(parent_selmod[0],Qt.DisplayRole) # file name
        subfile_off=self.file_list.data(parent_selmod[1],Qt.DisplayRole) # file offset
        subfile_type=self.file_list.data(parent_selmod[2],Qt.DisplayRole) # file type
        subfile_size=self.file_list.data(parent_selmod[3],Qt.DisplayRole) # file size
        subfile_index=self.treeView_2.selectionModel().selectedIndexes()[0].row() #file index


        arch_name = self._active_file.split('\\')[-1]
        selmod = 0
        subfile_type = 'FULLZIP'
        name = subfile_name
        local_off = 0
        oldCompSize = size
        oldDecompSize = size
        newCompSize = len(k)
        newDataSize = newCompSize
        diff = newCompSize - oldCompSize


        # Add item to the scheduler
        if not self.scheduler_model:
            self.scheduler_model = TreeModel(("Name","ID","Archive","Subarchive Name", "Subarchive Offset", "Subarchive Size", "Subfile Index", "Subfile Name", "Subfile Offset", "Subfile Type","Subfile Size", "Local File Offset", "Old Decompressed Size", "New Decompressed Size", "Old Compressed Size", "New Compressed Size","CheckSum", "Diff"))
        
        gc.collect()
        parent = self.scheduler_model.rootItem
        item=TreeItem((name,selmod,arch_name,subarch_name,subarch_offset,subarch_size,subfile_index,subfile_name,subfile_off,subfile_type,subfile_size,local_off,oldDecompSize,newDataSize,oldCompSize,newCompSize,chksm,diff),parent)
        parent.appendChild(item)
        self.scheduler.setModel(self.scheduler_model)
        self.schedulerFiles.append(k)
        self.statusBar.showMessage('File Added to Import Schedule')


    def export_items(self,selection):
        print('Exporting Items')
        row_num=len(selection)//4
        #Get archive name
        arch_name=self.archiveTabs.tabText(self.archiveTabs.currentIndex())
        
        selected_dir=QFileDialog.getExistingDirectory(caption="Choose Export Directory")
        print(selected_dir)
        if not selected_dir:
            return
        
        
        for i in range(row_num): #loop to each row
            f_name=self.file_list.data(selection[i],Qt.DisplayRole) #get file name
            off=self.file_list.data(selection[row_num+i],Qt.DisplayRole) #get file offset
            typ=self.file_list.data(selection[2*row_num+i],Qt.DisplayRole) #get file type
            size=self.file_list.data(selection[3*row_num+i],Qt.DisplayRole) #get file size
            print(f_name,off,typ,size)
            
            if size==0:
                continue
            
            f_name=selected_dir+'\\'+arch_name + '\\'+str(f_name)
            
            
            t=StringIO() #open temporary memory stream
            self._active_file_data.seek(off) 
            t.write(self._active_file_data.read(size)) #write data to temporary file
            
            if typ=='ZIP':
                f_name+='.zip'
                t.seek(0)
                data=t.read()
            elif typ=='GZIP LZMA':
                t.seek(0xE)
                data=pylzma.decompress_compat(t.read())
                #print(struct.unpack('>I',data[0:4])[0])
                if struct.unpack('>I',data[0:4])[0]==0x504B0304:
                    f_name+='.zip'
                elif struct.unpack('>I',data[0:4])[0]==0x44445320:
                    f_name+='.dds'
            elif typ=='OGG':
                t.seek(0)
                f_name+='.ogg'
                data=t.read()
            elif typ=='ZLIB':
                t.seek(0x10)
                data=zlib.decompress(t.read())
                if struct.unpack('>I',data[0:4])[0]==0x504B0304:
                    f_name+='.zip'
                elif struct.unpack('>I',data[0:4])[0]==0x44445320:
                    f_name+='.dds'
                else:
                    f_name+='xml'

            else:
                t.seek(0)
                data=t.read()
                    
           
            if not os.path.exists(os.path.dirname(f_name)):
                os.makedirs(os.path.dirname(f_name))

            print(f_name)
            k=open(f_name,'wb')
            k.write(data)
            k.close()
            t.close() 
            
    
    def test(self): #Sub Archive Reader
        selmod=self.current_tableView.selectionModel().selectedIndexes()
        '''Check Current Index'''
        if self.current_tableView_index==selmod[0].row():
            return
        arch_name=self.archiveTabs.tabText(self.archiveTabs.currentIndex())
        off=self.current_sortmodel.data(selmod[1],Qt.DisplayRole)
        size=self.current_sortmodel.data(selmod[3],Qt.DisplayRole)
        
        if arch_name not in self._active_file: #File not already opened
            try:
                if isinstance(self._active_file_handle,file):
                    self._active_file_handle.close()
                self._active_file=self.mainDirectory+os.sep+arch_name #Get the New arhive file path
                self._active_file_handle=open(self._active_file,'rb') #Opening File
            except:
                msgbox=QMessageBox()
                msgbox.setText("File Not Found\n Make sure you have selected the correct NBA 2K15 Installation Path")
                msgbox.exec_()
                return
        
        
        self._active_file_handle.seek(off)
        t=StringIO()
        t.write(self._active_file_handle.read(size))
        t.seek(0)
        self._active_file_data=t

        print('Searching in : ',self._active_file)
        print('Handle Path : ',self._active_file_handle.name)

        
        gc.collect()
        
        loc=archive_parser(self._active_file_data)
        if isinstance(loc,dataInitiate):
            ###Answering Data Delivery Request
            #Getting the Data
            self._active_file_data.close() #Closing the file
            self._active_file_handle.seek(off) #Big archive already open
            t=StringIO()
            t.write(self._active_file_handle.read(loc.datalen))
            t.seek(0)
            self._active_file_data=t
            loc=archive_parser(self._active_file_data) #Call archive parser again
        

        self.file_list=SortModel()
        self.file_listModel=TreeModel(("Name","Offset","Type","Size"))
        self.file_list.setSourceModel(self.file_listModel)
        
        #self.treeView_2.header().setResizeMode(QHeaderView.ResizeToContents)
        #self.treeView_2.header().setResizeMode(QHeaderView.Interactive)
        
        gc.collect()
        parent=self.file_listModel.rootItem
        for i in loc:
            #print(i)
            item=TreeItem(i,parent)
            parent.appendChild(item)

        self.treeView_2.setModel(self.file_list) #Update the treeview
        self.treeView_2.setSortingEnabled(True) #enable sorting
        self.treeView_2.sortByColumn(1,Qt.SortOrder.AscendingOrder) #sort by offset

        self.current_tableView_index=selmod[0].row()

    def open_file_table(self):
        #Delete Current Tabs
        while self.archiveTabs.count():
            
            widg=self.archiveTabs.widget(self.archiveTabs.currentIndex())
            self.archiveTabs.removeTab(self.archiveTabs.currentIndex())
            try:
                widg.deleteLater()
            except:
                pass

        gc.collect()
        self.mainDirectory=self.pref_window.mainDirectory # update mainDirectory
        file_name=self.mainDirectory+os.sep+'0A'
        print(self.mainDirectory,file_name)
        
        self._active_file=file_name #set active file to 0A file
        self._0Afile=file_name
        self._active_file_handle=open(self._active_file,'rb')

        
        self.statusBar.showMessage('Getting archives...')
        self.fill_archive_list() #Fill Archive List

        try:
            pass
            num=self.load_archive_database_tableview()
        except:
            msgbox=QMessageBox()
            msgbox.setText("File Not Found\n Make sure you have selected the correct NBA 2K15 Installation Path")
            msgbox.exec_()
            return

        #self.main_viewer_model=MyTableModel()

        #Setup second layout
        self.file_list=SortModel()
        self.file_listModel=TreeModel(("Name","Offset","Type","Size"))
        self.file_list.setSourceModel(self.file_listModel)
        self.treeView_2.setModel(self.file_list) #Update the treeview

        self.statusBar.showMessage(str(num)+ ' archives detected.')
        gc.collect()


    def open_file(self):
        #clear
        #create models for the list views
        #setup treeview and the sort model for sorting capabilities
        self.main_viewer_model=TreeModel(("Archive Name", "Offset", "Size"))
        self.main_viewer_sortmodel=SortModel()
        self.main_viewer_sortmodel.setSourceModel(self.main_viewer_model)

        self.file_list=SortModel()
        self.file_listModel=TreeModel(("Name","Offset","Type","Size"))
        self.file_list.setSourceModel(self.file_listModel)
        self.treeView_2.setModel(self.file_list) #Update the treeview
        
        
        gc.collect()
        
        self.mainDirectory=self.pref_window.mainDirectory # update mainDirectory
        file_name=self.mainDirectory+'\\'+'0A'
        print(self.mainDirectory,file_name)
        #file_name,file_filter=QFileDialog.getOpenFileName(caption='Select 0A File')
        
        #print(file_name,file_filter)
        self._active_file=file_name #set active file to 0A file
        self._0Afile=file_name
        self.statusBar.showMessage('Getting archives...')
        try:
            num=self.load_archive_database()
        except:
            msgbox=QMessageBox()
            msgbox.setText("File Not Found\n Make sure you have selected the correct NBA 2K15 Installation Path")
            msgbox.exec_()
            return
        self.statusBar.showMessage(str(num)+ ' archives detected.')
    
    def scheduler_add(self,im,fileName):
        #Get current selected file
        selmod = self.treeView_3.selectionModel().selectedIndexes()[0].row()
        name,off,oldCompSize,type = self.subfile.files[selmod]
        
        #Get archive Data
        parent_selmod=self.current_tableView.selectionModel().selectedIndexes()
        arch_name=self.archiveTabs.tabText(self.archiveTabs.currentIndex())
        subarch_name=self.current_sortmodel.data(parent_selmod[0],Qt.DisplayRole)
        subarch_offset=self.current_sortmodel.data(parent_selmod[1],Qt.DisplayRole)
        subarch_size=self.current_sortmodel.data(parent_selmod[3],Qt.DisplayRole)
        print(arch_name,subarch_offset,subarch_size)
        
        #Get Subfile Data
        parent_selmod=self.treeView_2.selectionModel().selectedIndexes()
        subfile_name=self.file_list.data(parent_selmod[0],Qt.DisplayRole) # file name
        subfile_off=self.file_list.data(parent_selmod[1],Qt.DisplayRole) # file offset
        subfile_type=self.file_list.data(parent_selmod[2],Qt.DisplayRole) # file type
        subfile_size=self.file_list.data(parent_selmod[3],Qt.DisplayRole) # file size
        subfile_index=self.treeView_2.selectionModel().selectedIndexes()[0].row() #file index
        chksm=0
        
        if subfile_type=='GZIP LZMA': #override size for GZIP LZMA
            oldCompSize=subfile_size
            compOffset=14
        
        print('Replacing File ',name, 'Size ',oldCompSize)
        t=self.subfile._get_file(selmod)
        
        if subfile_type=='ZIP':
            local_off=off
            compOffset=4
        else:
            local_off=0
        
        compFlag=False #flag for identifying dds files
        if not 'dds' in fileName:
            compFlag=True

        if 'dds' in name:
            #Getting Rest Image Data
            originalImage=dds_file(True, t)
            restDataLen=originalImage._get_rest_size()
            originalImage.data.seek(-restDataLen,2)
            restData=originalImage.data.read()
            
            #Calculating Old Image Size
            oldDecompSize=originalImage._get_full_size() + restDataLen
            
        #Calculating New Image Size
            
        #Calling the Texture Importer panel
        #if not isinstance(im,dds_file): 
        res = ImportPanel()
        res.exec_()
            
        if res.ImportStatus: #User has pressed the Import Button
            #Compress the Texture
            comp=res.CurrentImageType
            nmips = res.CurrentMipmap
            
            #print(originalImage.header.dwMipMapCount,nmips)

            

            
            if compFlag:
                print('Converting Texture file')
                self.statusBar.showMessage('Compressing Image...')
                status=call(['./nvidia_tools/nvdxt.exe','-file',str(fileName),comp,'-nmips',nmips,'-quality_production','-output','temp.dds'])
                f=open('temp.dds','rb')
            else:
                #working on an existing dds file
                f=open(fileName,"rb")

            t=StringIO() #writing temp.dds to an IO buffer, and fixing the dds header
            t.write(f.read(11))
            
            if res.swizzleFlag:
                t.write(struct.pack('B',128)) #writing flag for swizzled dds
                f.read(1)
            else:
                t.write(f.read(1))

            t.write(f.read(16))
            
            #Overriding Mipmap count when compressing image
            if compFlag:
                t.write(struct.pack('B',int(nmips))) #writing mipmaps
                f.read(1)
            else:
                t.write(f.read(1))

            t.write(f.read())
            f.close()
            t.seek(0)
            res.destroy()
        else:
            res.destroy()
            self.statusBar.showMessage('Import Canceled')
            return


        

        
        f=open('testing.dds','wb')
        f.write(t.read())
        f.close()
        t.seek(0)
        
        
        f=dds_file(True,t)
        if res.swizzleFlag:
            print('Swizzling Texture')
            f.swizzle_2k()
        t=f.write_texture()

        newData=t.read()
        
        
        newData+=restData
        newDataSize=len(newData)
        chksm=zlib.crc32(newData) & 0xFFFFFFFF #calculate Checksum

        
        k=pylzma.compress(newData,24) #use 16777216 bits dictionary
        k=k+k[0:len(k)//4] #inflating file
        comp_f=open('test.dat','wb')
        comp_f.write(k)
        comp_f.close()
        newCompSize=len(k)
        
        diff=newCompSize+compOffset-oldCompSize
        
        print('OldDecompSize: ',oldDecompSize,'NewDecompSize: ',newDataSize)
        print('OldCompSize: ',oldCompSize,'NewCompSize: ',newCompSize,'Diff: ', diff)
        
        
        
        #Calculate New Image Size
        
        # Add item to the scheduler
        if not self.scheduler_model:
            self.scheduler_model = TreeModel(("Name","ID","Archive","Subarchive Name", "Subarchive Offset", "Subarchive Size", "Subfile Index", "Subfile Name", "Subfile Offset", "Subfile Type","Subfile Size", "Local File Offset", "Old Decompressed Size", "New Decompressed Size", "Old Compressed Size", "New Compressed Size","CheckSum", "Diff"))
        
        gc.collect()
        parent = self.scheduler_model.rootItem
        item=TreeItem((name,selmod,arch_name,subarch_name,subarch_offset,subarch_size,subfile_index,subfile_name,subfile_off,subfile_type,subfile_size,local_off,oldDecompSize,newDataSize,oldCompSize,newCompSize,chksm,diff),parent)
        parent.appendChild(item)
        self.scheduler.setModel(self.scheduler_model)
        self.schedulerFiles.append(k)
        self.statusBar.showMessage('Texture Added to Import Schedule')
            
    def runScheduler(self):
        parent=self.scheduler_model.rootItem
        rowCount=parent.childCount()
        #print(rowCount)
        
        for i in range(rowCount):
            item=parent.child(i)
            name,selmod,arch_name,subarch_name,subarch_offset,subarch_size,subfile_index,subfile_name,subfile_off,subfile_type,subfile_size,local_off,oldDecompSize,newDataSize,oldCompSize,newCompSize,chksm,diff = item.data(0),item.data(1),item.data(2),item.data(3),item.data(4),item.data(5),item.data(6),item.data(7),item.data(8),item.data(9),item.data(10),item.data(11),item.data(12),item.data(13),item.data(14),item.data(15),item.data(16),item.data(17)
            if not arch_name in self._active_file: #check archive name
                self._active_file=self.mainDirectory+'\\'+arch_name
            
            
            f=open(self._active_file,'r+b') #open big archive
            f.seek(subarch_offset) #seek to iff offset
            t=StringIO() #buffer for iff storage
            t.write(f.read(subarch_size)) #store iff file
            t.seek(0)

            #f.seek(subfile_off,1) #seek to subfile offset
            #f.seek(local_off,1) #seek to local zip offset

            t.seek(subfile_off+local_off)
            iffFlag=False
            compOffset=0
            print(subfile_type)
            if subfile_type=='ZIP':
                compOffset=4
                #t.seek(4,1) #seek to the lzma offset
            elif subfile_type=='GZIP LZMA':
                print('GZIP LZMA')
                compOffset=14
                #t.seek(14,1) #seek to the raw gzip offset
            elif subfile_type=='IFF':
                print('Importing IFF')
                iffFlag=True
            t.seek(compOffset,1)

            if diff <= 0:
                print('Enough Space for File')
                t.write(self.schedulerFiles[i]) #enough space for writing
                
                t.seek(0)
                k=open('temp.iff','wb')
                k.write(t.read())
                k.close()
                
                t.seek(0)
                #Writing iff back to full archive
                f.seek(subarch_offset)
                f.write(t.read())
                t.close()
                f.close()
            else:
                if not iffFlag:
                    #writing File to archive
                    #diff+=compOffset
                    t.seek(oldCompSize-compOffset,1)
                    tail=StringIO()
                    tail.write(t.read()) #bytes after the file
                    tail.seek(0)
                    print('tail size: ',len(tail.read()))
                    tail.seek(0)

                    if subfile_type=='ZIP':
                        t.seek(subfile_off+local_off)
                        t.seek(-len(name)-4-8-4,1)
                        print(chksm)
                        t.write(struct.pack('<I',chksm))
                        t.write(struct.pack('<I',newCompSize+0x4))
                        t.write(struct.pack('<I',newDataSize))
                        
                        #seeking for appropriate info header
                        sub_file._get_zip_info_offset(selmod,tail)
                        print(tail.tell())
                        tail.write(struct.pack('<I',chksm))
                        tail.write(struct.pack('<I',newCompSize+0x4))
                        tail.write(struct.pack('<I',newDataSize))
                        #seeking for end of central directory
                        tail.seek(0)
                        sub_file._get_zip_end_offset(tail)
                        print(tail.tell())
                        s = struct.unpack('<I',tail.read(4))[0]
                        tail.seek(-4,1)
                        tail.write(struct.pack('<I',s+diff))


                        tail.seek(0)

                    
                    t.seek(subfile_off+local_off+compOffset)
                    t.write(self.schedulerFiles[i])
                    t.write(tail.read())
                    tail.close()
                    
                    #Fix IFF Header
                    t.seek(0) #seek to iff start
                    t.seek(8,1) #Skip magic and descr sec size
                    s = struct.unpack('>I',t.read(4))[0]
                    t.seek(-4,1)
                    t.write(struct.pack('>I',s+diff))

                    t.seek(0) #seek to iff start
                    head=header(t)
                    head.x38headers[0].size +=diff
                    head.x38headers[0].stop +=diff
                    t.seek(head.x38headersOffset)
                    head.x38headers[0].write(t)

                    #next header
                    head.x38headers[1].start +=diff
                    t.seek(head.x38headersOffset+0x38)
                    head.x38headers[1].write(t)

                    #Try automatically index calculation
                    print('Old subfile index',subfile_index)
                    subfile_index=int(subfile_name.split('_')[1]) + int(subfile_name.split('_')[3])
                    print('New calculated index',subfile_index)

                    #i have to tweak all the next offsets
                    for i in range(subfile_index+1,len(head.sub_heads_data[0])):
                        print('Changing offset in file: ',i)
                        print('Seeking to: ',head.sub_heads_data[0][i])
                        t.seek(head.sub_heads_data[0][i])
                        fe=file_entry(t)
                        if not fe.type==3:
                            t.seek(fe.off+16)
                            s = struct.unpack('<Q',t.read(8))[0]
                            t.seek(-8,1)
                            t.write(struct.pack('<Q',s+diff))

                    
                    t.seek(0)
                    k=open('temp.iff','wb')
                    k.write(t.read())
                    k.close()
                else:
                    #writing full imported iff file
                    t=StringIO()
                    t.write(self.schedulerFiles[i])

                
                #Append iff into the big archive
                t.seek(0)
                f.seek(subarch_offset+subarch_size)
                
                tailPath=self.mainDirectory+os.sep+'tail'
                tail=open(tailPath,'wb')
                tailSize=os.fstat(tail.fileno()).st_size
                buf=1
                while buf:
                    buf=f.read(1024*1024*1024)
                    print(len(buf))
                    tail.write(buf)
                tail.close()
                print("Done Writing tail - TESTING")
                #Write actual data to archive
                f.seek(subarch_offset)
                f.write(t.read())
                t.close()

                print("Writing back tail to big archive - TESTING")
                #Writing back the tail
                with open(tailPath,'rb') as tail:
                    f.write(tail.read(1024*1024*1024))
                f.close()
                

                    
                #diff-=compOffset #restore diff
                #Updating 0A database
                f=open(self.mainDirectory+'\\'+'0A','r+b')
                f.read(0x10)
                arch_num=struct.unpack('<I',f.read(4))[0]
                f.read(0xC)
                file_count=struct.unpack('<I',f.read(4))[0]
                f.read(0xC)
                f.seek(archiveName_dict[arch_name]*0x30,1) #seeking to archive definition position
                s = struct.unpack('<Q',f.read(8))[0]
                f.seek(-8,1)
                print('Writing '+str(arch_name) + ' size to ',str(f.tell()))
                f.write(struct.pack('<Q',s+diff))
                
                f.seek((arch_num+1)*0x30)#seeking to archive definitions
                data_off=f.tell() #store the data offset

                subarch_id=int(subarch_name.split('_')[-1]) #get global file id
                f.seek(subarch_id*0x18,1)
                print('Found subarchive entry in ',f.tell())
                s = struct.unpack('<Q',f.read(8))[0]
                f.seek(-8,1)
                f.write(struct.pack('<Q',s+diff)) # update its size
                f.seek(8,1)
                sub_arch_full_offset=struct.unpack('<Q',f.read(8))[0]
                
                #Update next file offsets

                for arch in self.list:
                    print('Seeking in: ',arch[0],arch[1],arch[2])
                    for subarch in arch[3]:
                        #find all siblings with larger offset
                        test_val=subarch[1]+arch[1]
                        if test_val>sub_arch_full_offset:
                            subarch_name = subarch[0]
                            subarch_id = int(subarch_name.split('_')[-1])
                            f.seek(data_off+subarch_id*0x18)
                            f.seek(8+4+4,1)
                            s = struct.unpack('<Q',f.read(8))[0]
                            f.seek(-8,1)
                            f.write(struct.pack('<Q',s+diff))

                f.close()

            self.schedulerFiles.pop()
            print('Scheduled Files left',len(self.schedulerFiles))
            #self.scheduler_model.removeRows(i,1)
            self.scheduler.setModel(None)
            self.scheduler_model.rootItem.childItems.pop()
            self.scheduler.setModel(self.scheduler_model)
            gc.collect()
            self.statusBar.showMessage('Import Completed')
            self.open_file_table()#reload archives
            
    
    def close_app(self):
        sys.exit(0)

    def fill_archive_list(self):
        f=self._active_file_handle
        f.seek(16)
        count_0=struct.unpack('<I',f.read(4))[0]
        f.seek(12,1)
        count_1=struct.unpack('<I',f.read(4))[0]
        f.seek(12,1)
        s=0
        print('Counts: ',count_0,count_1)
        self.list=[]
        for i in range(count_0):
            size=struct.unpack('<Q',f.read(8))[0]
            f.read(8)
            name=read_string_1(f)
            f.read(13+16)
            #print(name,hex(size),f.tell())
            #self.main_list.append(None,(name,s))
            self.list.append((name,s,size,[]))
            archiveOffsets_list.append(s)
            s+=size

        archiveOffsets_list.append(s)

        print('Total Size: ',s)
        #Store archives data
        self.t=StringIO()
        self.t.write(f.read(0x18*count_1))
        
        #Split worker jobs

        work_length=50000
        work_last_length=count_1 % work_length
        work_count=count_1 // work_length


        #Call workers
        t0=time.clock()
        threads=[]
        subarch_id=0 #keep the subarchive id
        for i in range(work_count):
            print('Starting Thread: ',i)
            self.t.seek(i*work_length*0x18)
            data=StringIO()
            data.write(self.t.read(0x18 * work_length))
            #thread=threading.Thread(target=self.worker,args=(data,work_length,count_0,))
            thread=threading.Thread(target=self.worker,args=(data,work_length,count_0,subarch_id,))
            thread.start()
            threads.append(thread)
            subarch_id+=work_length
        for i in range(work_count):
            threads[i].join()
            
        #last worker
        self.t.seek(work_count*work_length*0x18)
        data=StringIO()
        data.write(self.t.read(0x18 * work_last_length))
        thread=threading.Thread(target=self.worker,args=(data,work_last_length,count_0,subarch_id,))
        thread.start()
        thread.join()

        print('Finished working. Total Time Elapsed: ',time.clock()-t0)

    def load_archive_database_tableview(self):
        #Create Tabs according to the Settings
        print('Parsing Settings')
        settings=self.pref_window.pref_window_buttonGroup
        selected_archives=[]
        for child in settings.children():
            if isinstance(child, QCheckBox):
                if child.isChecked():
                    selected_archives.append(archiveName_dict[child.text().split(' ')[0]])
        
        count=0
        print('Creating ',len(selected_archives),' Tabs')
        for i in selected_archives:
            #Create TableViewModel
            entry=self.list[i]
            sortmodel=MyTableModel(entry[3],["Name","Offset","Type","Size"])
            #Create the TableView and Assign Options
            table_view=QTableView()
            table_view.setModel(sortmodel)
            table_view.horizontalHeader().setResizeMode(QHeaderView.Stretch)
            table_view.setSortingEnabled(True)
            table_view.sortByColumn(1, Qt.AscendingOrder)
            table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
            table_view.setSelectionMode(QAbstractItemView.SingleSelection)
            table_view.hideColumn(2)
            
                        #Functions
            table_view.clicked.connect(self.test)
            table_view.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            table_view.customContextMenuRequested.connect(self.main_ctx_menu)

            count+=len(entry[3])
            tabId=self.archiveTabs.addTab(table_view,entry[0])
            self.main_viewer_sortmodels.append(sortmodel) #Store the sortmodel handles
        return count

    def load_archive_database_treeview(self):
        self.fill_archive_list(self)
        
        #=======================================================================
        # print('Storing to external db')
        #     
        # db=open('C:\\2k.db','wb')
        # db.write(struct.pack('<4Q',count_1,0,0,0))
        # for arch in self.list:
        #     db.write(arch[0])
        #     db.write(struct.pack('<6B',0,0,0,0,0,0))
        #     db.write(struct.pack('Q',len(arch[2])))
        #     for i in range(len(arch[2])):
        #         db.write(struct.pack('<2Q',arch[2][i][1],arch[2][i][2]))
        #         
        # db.close()
        # print('Finish writing db')
        # 
        #=======================================================================
            
        #Alternative way of storing to the viewer
        #self.database_worker()
        #return
        
        #filling the main model
        self.main_viewer_model.setupModelData(self.list, self.main_viewer_model.rootItem, self.pref_window.pref_window_buttonGroup)
        print('Testing')
        self.treeView.setModel(self.main_viewer_sortmodel)
        #storing list to main_list
        self.statusBar.showMessage('Sorting...')
        print('Storing to Viewer')
        t0=time.clock()
        self.treeView.setSortingEnabled(True)
        #self.treeView.sortByColumn(1,Qt.SortOrder.AscendingOrder)
        print('Finished storing. Total Time Elapsed: ',time.clock()-t0)   
        
        self.statusBar.showMessage('Ready')
        
        for i in self.list:
            print(i[0],len(i[3]))
        return count_1
        
    def worker(self,data,length,count_0,subarch_id):
        data.seek(0)
        #f=open('C:\\worker.txt','w')
        for i in range(length):
            sa=struct.unpack('<Q',data.read(8))[0]
            id0=struct.unpack('<I',data.read(4))[0]
            sb=struct.unpack('<I',data.read(4))[0]
            id1=struct.unpack('<Q',data.read(8))[0]
            #f.write(id1)
            for j in range(count_0-1,-1,-1):
                val=self.list[j][1] # full archive calculated offset
                if id1>=val:
                    #self.main_list.append(it,('unknown_'+str(i),id1-val))
                    self.list[j][3].append(('unknown_'+str(subarch_id),id1-val,sb,sa))
                    subarch_id+=1
                    break
    
    def read_subfile(self):
       print('read_subfile function')
       selmod=self.treeView_2.selectionModel().selectedIndexes()
       name=self.file_list.data(selmod[0],Qt.DisplayRole) # file offset
       off=self.file_list.data(selmod[1],Qt.DisplayRole) # file offset
       typ=self.file_list.data(selmod[2],Qt.DisplayRole) # subfile type
       size=self.file_list.data(selmod[3],Qt.DisplayRole) # size offset
       print(off,typ,size)
       #get file data
       #f=open(self._active_file,'rb')
       
       #Exceptions
       
       self._active_file_data.seek(off)
       data=StringIO()
       data.write(self._active_file_data.read(size))
       data.seek(0)
       
       if typ=='OGG':
           print('Loading OGG File')
           t=open('temp.ogg','wb')
           t.write(data.read())
           t.close()
           self.sound_player.Stop()
           self.sound_player.OpenFile()
           return
       
       #parse the subfile and store to class
       self.subfile=sub_file(data,typ,size)
       
       #store subfile contents to the files store
       self.subfiles=TreeModel(("Name",))
       self.treeView_3.setModel(self.subfiles)
       self.treeView_3.header().setResizeMode(QHeaderView.Interactive)
       gc.collect()
       
       parent=self.subfiles.rootItem
       for i in self.subfile.namelist:
           #print(i)
           item=TreeItem((i,),parent)
           parent.appendChild(item)
        
    def open_subfile(self):
        selmod=self.treeView_3.selectionModel().selectedIndexes()[0].row()
        print(self.subfile.files)
        name,off,size,type=self.subfile.files[selmod]
        print('Opening ',name)
        t=self.subfile._get_file(selmod) #getting file
        
        typecheck=struct.unpack('>I',t.read(4))[0]
        t.seek(0)
        try:
            type=type_dict[typecheck]
        except:
            #print(type)
            type='UNKNOWN'
        
        print(type)
        #binary files checking
        if type=='DDS':
            print('Reading DDS File')
            image=dds_file(True,t)
            self.glviewer.texture_setup(image)
            
        elif type=='MODEL':
            print('Reading Model')
            #Spawn Message Dialog for 2 model Modes
            dial=ModelPanel()
            dial.exec_()
            
            print('Selected Mode: ',dial.mode)
            #try guessing the correct mode:
            #try:
            vc,tc=self.parseModel(dial.mode,t)
            #except:
            #    t.seek(0)
            #    vc,tc=self.parseModel(1,t)

            
        #try to parse over the extension
        if type=='UNKNOWN':
            if name.split('.')[-1] in ['json'] or name=='xml_file':
                self.text_editor.clear()
                self.text_editor.setPlainText(str(t.read()))

        t.close()
            
    def parseModel(self,mode,t):
        print('Importing model with mode: ',mode)
        
        fType = struct.unpack('>I', t.read(4))[0]
        print('File Type: ', hex(fType))
        #Set Scale
        if mode:
            scale=100.0
        else:
            scale=0.001

        first = Model2k(t)
        first.data = first.read_strips(t)
        first.data = first.strips_to_faces()
        
        #vertices
        second = Model2k(t)
        second.data = second.get_verts(t,scale)
        print(len(second.data))
        #normals
        third = Model2k(t)
        if mode:
            third.data = third.get_normals(t)
        else:
            third.data = third.fill_normals(len(second.data))
        
        print('Mesh Vertex Count: ', len(second.data))
        
        self.glviewer.object=self.glviewer.customModel(first.data,second.data,third.data)
        return len(second.data),len(first.data)

            # 
            # #normals
            # third = Model2k(f)
            # third.data = third.read_unknown(f)
            # 
            # #tangents
            # fourth = Model2k(f)
            # fourth.data = fourth.read_unknown(f)
            # 
            # #uvs0
            # fifth = Model2k(f)
            # fifth.data = fifth.read_uvs(f)
            # 
            # #uvs1
            # sixth = Model2k(f)
            # sixth.data = sixth.read_uvs(f)
            # 
            # #uvs1
            # #sixth = Model2k(f)
            # #sixth.data = sixth.read_uvs(f)
            # 
            # f.close()
            # #for i in range(len(fifth.data)):
            #     #print(i, fifth.data[i])

    def fill_info_panel(self,info_dict): #Not used anymore
        #setup info panel
        print('Clearing Information Panel')
        for entry in self.groupBox_3.layout().children():
            self.clearLayout(entry)
        print('Setting Up Information Panel')
        sub_layout=QFormLayout()
        for entry in info_dict:
            lab=QLabel()
            if not info_dict[entry]:
                lab.setText("<P><b><FONT COLOR='#000000' FONT SIZE = 4>"+str(entry)+"</b></P></br>")
            else:
                lab.setText(str(entry)+info_dict[entry])
            
            sub_layout.addWidget(lab)
        
        self.groupBox_3.layout().addLayout(sub_layout)
        gc.collect()
    
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())        
                  
def archive_parser(f):
    file_list=[]
    #f.seek(main_off)
    head=header(f)
    # i should replace all of this with a simple append of the return function

    if head.magic==0x7EA1CFBB:
        file_list.append(('unknown_'+str(0),head.file_entries[0][0],'OGG',head.file_entries[0][1]))
        return file_list
    elif head.magic==0x00000000:
        file_list.append(('Reserved Section',head.file_entries[0][0],'EMPTY',0))
        return file_list
    elif head.magic in index_table:
        file_list.append(('Index Section',head.file_entries[0][0],str(hex(head.magic)),0))
        return file_list
    elif head.magic==0x5A4C4942:
        file_list.append(('zlib_file',head.file_entries[0][0],'ZLIB',0))
        return file_list
    elif head.magic==0x504B0304:
        file_list.append(('zip_',head.file_entries[0][0],'ZIP',head.file_entries[0][1]))
        return file_list
    elif head.magic in [0xC6B0581C,0x4A50922A,0xAAC40536]:
        file_list.append(('encrypted_data',head.file_entries[0][0],'ENCRYPTED',head.file_entries[0][1]))
        return file_list


    if not head.magic in [0x305098F0,0x94EF3BFF]:
        file_list.append(('encrypted_data',head.file_entries[0][0],'ENCRYPTED',head.file_entries[0][1]))
        return file_list

    
    if head.file_name:
        print("### FILENAME DETECTED ### ", head.file_name)


    #change the way we parse the archive using the x38 headers which should always work according to their sizes
    #for x38 in head.x38headers:
    #f.seek(head.main_offset+x38.start)
    #    print('x38 Start: ',x38.start,'x38 Type: ',x38.type,'x38 CompType: ',x38.comp_type)
    #    f.seek(x38.start)
    #    if x38.type==8:
    #        if x38.comp_type==0:
    #            continue #Empty Section
    #        else:
    #            file_list.append(('padding',f.tell(),'PAD',x38.stop))
    #    elif x38.type in [0x10,0x80]:
    #        file_list.append(('zlib_file',f.tell(),'ZLIB',x38.stop))
    #    elif x38.type==1: #work on indexed files
    print('Parsing Head Files: ',len(head.file_entries))
    counter=0
    while counter<len(head.file_entries):
        entry=head.file_entries[counter]
        
        off=entry.off
        #f.seek(head.main_offset+x38.start+off)
        f.seek(off)
        #print(f.tell())
        try:
            f_id=struct.unpack('>I',f.read(4))[0]
        except: #Initiate data delivery
            ###Data Delivery is programmed for CDF use only###
            print('###Initiating Data Delivery System###')
            #Calculating Data Size
            data_size=0
            for i in head.file_entries: data_size+= (i.size+i.pad)
            data_size+=head.header_length
            return dataInitiate('DataInitiateRequest',data_size)
            ###End of delivery

        file_offset=f.tell()-4
        if f_id==0x01F8B0E00:
            file_type='GZIP LZMA'
        elif f_id==0x504B0304:
            file_type='ZIP'
        elif f_id==0x5A4C4942:
            file_type='ZLIB'
        elif f_id==0x94EF3BFF:
            file_type='IFF ARCHIVE'
        elif f_id==0x305098F0:
            file_type='CDF ARCHIVE'
            f.seek(-4,1) #get in position to parse new header
            print('Parsing inner archive',f.tell())
            in_items=archive_parser(f)#parse new file
            counter+=len(in_items)
            file_list.append(('cdf_file',file_offset,file_type,0))
            file_list.extend(in_items) #extend the existing list
            #handle ecnrypted data exception
            if in_items[0][0]=='encrypted_data':
                return file_list
        elif f_id==0xC6B0581C:
            file_type='ENCRYPTED DATA'
            print(file_type)
            file_list.append(('encrypted_data',file_offset,file_type,0))
            return file_list
        else:
            file_type='UNKNOWN'

        file_group='group_'+str(entry.g_id)
        #cdf archives exceptions
        file_size=head.file_sizes[counter]

        #store the file
        #print(('unknown_'+str(counter),file_offset,file_type,file_size))
        file_list.append((file_group+'_unknown_'+str(counter),file_offset,file_type,file_size))
        counter+=1 #next file
    #    else:
    #        print('unhandled type: ',x38.type,'at: ',head.main_offset)


    return file_list    



app=QApplication(sys.argv)        
form=MainWindow()
form.show()
app.exec_()       
