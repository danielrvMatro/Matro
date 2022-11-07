import os
import pandas as pd
from flask import Flask, flash, request, redirect, url_for, send_from_directory,render_template,send_file
from werkzeug.utils import secure_filename
import PyPDF2
import json





# en el mismo lugar del archivo main.py crear la carpeta "archivos"
UPLOAD_FOLDER = 'uploads' # /ruta/a/la/carpeta
DOWNLOAD_FOLDER ='downloads'
dim = json.load( open('./uploads/Datos_US.json'))

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
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

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('transform',filename=filename))
    return  render_template('upload.html')

@app.route('/transform/<filename>')
def transform(filename):
    ruta=f"./uploads/{filename}"
    pdfFileObj = open(ruta, 'rb')
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
                data['pagina'].append(i+1)
                data['accion'].append(k)
                data['nombre'].append(v)    
    frame = pd.DataFrame.from_dict(data)
    filename=filename.replace('pdf', 'xlsx')
    #frame.to_excel(f'./downloads/{filename}',sheet_name='Andrea', index = False)
    
    for row in dim['dim_usuarios']:
        data2["equipo"].append(row["EQUIPO"])
        data2["descripcion"].append(row["DESCRIPCION"])
        data2["usuario"].append(row["USUARIO"].upper())

    frame2 = pd.DataFrame.from_dict(data2)
    
    fframe = pd.merge(frame2[['equipo','descripcion','usuario']],frame[['nombre','accion']],how="left",left_on='usuario',right_on='nombre')
    fframe=fframe.groupby(['equipo','usuario']).agg(num_paginas=('nombre','count'))
    fframe["maximo_num_paginas"]=fframe.groupby('equipo')['num_paginas'].transform(max)
    fframe.to_excel(f'./downloads/{filename}',sheet_name='Andrea', index = True)
    
    return redirect(url_for('descargar',file=filename))
   
@app.route('/descargar/<file>', methods=['GET', 'POST'])
def descargar(file="None"):
    if request.method == 'POST': 
        #return  redirect(url_for('upload_file'))
        file_path = os.path.join(app.config['DOWNLOAD_FOLDER'], file)
        return send_file(file_path)
    return  render_template('descargar.html',file=file)

#@app.route('/', methods=['GET', 'POST'])
#def upload_file():
#    if request.method == 'POST':
#         
#        if 'file' not in request.files:
#            flash('No file part')
#            return redirect(request.url)
#        file = request.files['file']
#        
#        if file.filename == '':
#            flash('No selected file')
#            return redirect(request.url)
#        if file and allowed_file(file.filename):
#            filename = secure_filename(file.filename)
#            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#            return redirect(url_for('uploaded_file',filename=filename))
#    return  render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

if __name__ == "__main__":
 app.run()
                    
#if __name__ == "__main__":
# app.run(debug=True, port=5000)
           