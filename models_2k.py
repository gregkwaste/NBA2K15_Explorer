import struct, sys, os
#from mathutils import Vector

class Model2k:
    def __init__(self, f):
        self.type = struct.unpack('>I', f.read(4))[0]
        self.size = struct.unpack('<I', f.read(4))[0]
        self.hash = struct.unpack('>I', f.read(4))[0]
        self.num0 = struct.unpack('<H', f.read(2))[0]
        self.num1 = struct.unpack('B', f.read(1))[0]
        self.num2 = struct.unpack('B', f.read(1))[0]
        self.data = None
        print('Section ', hex(self.type), self.size, hex(self.hash), self.num0, self.num1, self.num2)

    def get_verts(self,f,scale):
        if self.num2==2:
            return self.read_vertices_half(f,scale)
        elif self.num2==1:
            return self.read_vertices_float(f,scale)
        else:
            print('Wrong num2')

    def get_normals(self,f):
        if self.num2==2:
            return self.read_vertices_float(f)
        elif self.num2==1:
            return self.read_normals_half(f)
        else:
            print('Wrong num2')

    def fill_normals(self,count):
        
        norms=[]
        for i in range(count):
            norms.append((0,0,1))
        return norms

    def read_strips(self, f):
        n = 0
        indices = []
        while True:
            temp = []
            s = struct.unpack('<H', f.read(2))[0]
            n += 2
            while True:
                temp.append(s)
                s = struct.unpack('<H', f.read(2))[0]
                n += 2
                if s == 0xFFFF:
                    break
                if n >= self.size - 0x10:
                    #print('exiting')
                    temp.append(s) #append the last one
                    break
            
            indices.append(temp)
            if n >= self.size - 0x10: break
        return indices

    def read_vertices_half(self, f, scale):
        v_count = (self.size- 0x10) // 8
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<h', f.read(2))[0] / 65535.0
            v2 = struct.unpack('<h', f.read(2))[0] / 65535.0
            v3 = struct.unpack('<h', f.read(2))[0] / 65535.0
            f.read(2)
            verts.append((scale*v1, scale*v3, scale*v2))
        return verts
    
    def read_normals_half(self, f):
        v_count = (self.size- 0x10) // 8
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<h', f.read(2))[0] / 65535.0
            v2 = struct.unpack('<h', f.read(2))[0] / 65535.0
            v3 = struct.unpack('<h', f.read(2))[0] / 65535.0
            f.read(2)
            verts.append((1.0 - v1,1.0 -  v3,1.0 -  v2))
        return verts


    def read_vertices_float(self, f, scale):
        v_count = (self.size- 0x10) // 12
        verts = []
        for i in range(v_count):
            v1 = struct.unpack('<f', f.read(4))[0]
            v2 = struct.unpack('<f', f.read(4))[0]
            v3 = struct.unpack('<f', f.read(4))[0]
            verts.append((scale*v1, scale*v3, scale*v2))
        return verts
    
    def read_uvs(self, f):
        uv_count = (self.size -0x10) //4
        uvs = []
        for i in range(uv_count):
            uv1 = struct.unpack('<h', f.read(2))[0] / 65535.0
            uv2 = struct.unpack('<h', f.read(2))[0] / 65535.0
            uvs.append((0.5 + uv1, 0.5 + uv2))
        return uvs
    
    def read_unknown(self,f):
        count = (self.size -0x10) //8
        for i in range(count):
            f.read(8)
        return None
    
    def tris_to_faces(self):
        chunkNum=len(self.data)
        faces = []
        for i in range(chunkNum):
            if len(self.data[i])==4:
                faces.append(self.data[i])
            elif len(self.data[i])==8:
                faces.append(self.data[i][0:3])
                faces.append(self.data[i][4:7])
        return faces    
                
                
    
    def strips_to_faces(self):
        chunkNum=len(self.data)
        faces=[]
        for i in range(chunkNum):
            strip=self.data[i]
            faceNum=len(strip)-2
            flag=True
            index=0
            for j in range(faceNum):
                if flag:
                    tup=(strip[index],strip[index+1],strip[index+2])
                    if not (tup[0]==tup[1] or tup[1]==tup[2] or tup[0]==tup[2]):
                        faces.append(tup)
                    index += 1
                    flag=not flag
                else:
                    tup=(strip[index+1],strip[index],strip[index+2])
                    if not (tup[0]==tup[1] or tup[1]==tup[2] or tup[0]==tup[2]):
                        faces.append(tup)
                    index += 1
                    flag= not flag
        return faces
                    
#===============================================================================
# 
# 
# f = open('C:\\Users\\gregkwaste\\Desktop\\model\\0D\\stadium\\0D\\group_7_unknown_327', 'rb')
# #f = open('C:\\Users\\gregkwaste\\Desktop\\model\\0D\\player_fa1ba768c8bfa9a0.model', 'rb')
# 
# fType = struct.unpack('>I', f.read(4))[0]
# print('File Type: ', hex(fType))
# 
# first = Model2k(f)
# first.data = first.read_strips(f)
# #print(first.data)
# first.data = first.strips_to_faces()
# #first.data = first.tris_to_faces()
# #print(first.data)
# 
# f.seek(first.size+4)
# 
# #vertices
# second = Model2k(f)
# second.data = second.read_vertices_float(f)
# print('Mesh Vertex Count: ', len(second.data))
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
# 
# 
# uvs = []
# uvs.append(fifth.data)
# uvs.append(sixth.data)
#===============================================================================


#createmesh(second.data,first.data,uvs,'nba_player_model',0,0,'',[],False,[],0.001)






