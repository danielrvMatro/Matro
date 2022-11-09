import os
import pandas as pd
import PyPDF2 
import json


data={
    "pagina":[],
    "nombre":[],
    "accion":[]
    }
data2={
    "equipo":[],
    "descripcion":[],
    "usuario":[]
}

ruta=""
ds={}


ruta=f"./uploads/INFORME_PRUEBA.pdf"
pdfFileObj = open(ruta, 'rb')
dim = json.load( open('./uploads/Datos_US.json'))
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
number_of_pages = pdfReader.numPages

for i in range (0,number_of_pages):
            pageObj = pdfReader.getPage(i) 
            chain =pageObj.extractText()
            index=chain.find(u'\u2703')
            step =chain[index:]
            step=step.replace(u'\u2703','')
            ds=step.splitlines()
            
            for row in ds:
                indx = row.find(':')
                k=row[:indx].strip()
                v=row[(indx+2):].strip()
                if k=="Aprobación solicitada":
                    data['pagina'].append(i+1)
                    data['accion'].append(k)
                    data['nombre'].append(v)    
frame = pd.DataFrame.from_dict(data)
print(frame)
for row in dim['dim_usuarios']:
    data2["equipo"].append(row["EQUIPO"])
    data2["descripcion"].append(row["DESCRIPCION"])
    data2["usuario"].append(row["USUARIO"].upper())

frame2 = pd.DataFrame.from_dict(data2)

fframe = pd.merge(frame2[['equipo','descripcion','usuario']],frame[['nombre','accion']],how="left",left_on='usuario',right_on='nombre')
fframe=fframe.groupby(['equipo','usuario']).agg(Npaginas=('nombre','count'))
fframe["Mpag"]=fframe.groupby('equipo')['Npaginas'].transform(max)


fframe.to_excel('./downloads/Test.xlsx',sheet_name='Andrea', index = True)

