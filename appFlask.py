from fileinput import filename
from flask import Flask, flash, request, redirect, url_for, render_template, session
from werkzeug.utils import secure_filename
from vosk import Model, KaldiRecognizer, SetLogLevel
import wave, os, glob
import subprocess
import json
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud

UPLOAD_FOLDER = '/Users/andreluiz/Documents/projetos/audioTextoVoskFlask/uploads'
ALLOWED_EXTENSIONS = {'ogg', 'wav'}
#IMG_FOLDER = '/Users/andreluiz/Documents/projetos/audioTextoVoskFlask/imagens'

app = Flask(__name__)
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#app.config['IMG_FOLDER'] = IMG_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html', titulo='Audio Texto')

@app.route('/transcrever', methods=['POST','GET'])
def transcrever():
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

            arquivo_audio = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #arquivo_audio = '/Users/andreluiz/Documents/projetos/audioTextoVoskFlask/uploads/conversa2.ogg'
            #Começa a transcrição 
            SetLogLevel(0)

            #Escolhe o modelo treinado em português
            model = Model(r'/Users/andreluiz/Documents/projetos/audioTextoVoskFlask/static/vosk-model-small-pt-0.3')
    
            #abre o arquivo com o audio
            wf = wave.open(arquivo_audio, 'rb')
        
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":    
                print ("Arquivo deve estar no formato WAV mono PCM.")
                exit (1)
            
            #executa a transcrição
            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)
            rec.SetPartialWords(True)

            transcricao_completa = ''

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    transcricao_completa = transcricao_completa + res['text']
            res = json.loads(rec.FinalResult())
            
            #imprime apenas a trascrição completa, em vez de parcial
            transcricao_completa = transcricao_completa + res['text']
            wf.close()

            #imprime word cloud 
            #Imprime nuvem de palavras
            x, y = np.ogrid[:300, :300]

            mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
            mask = 255 * mask.astype(int)

            wc = WordCloud(background_color="white", repeat=True, mask=mask)
            wc.generate(transcricao_completa)
            wc.to_file("/Users/andreluiz/Documents/projetos/audioTextoVoskFlask/static/wordcloud.png")
     
           # plt.axis("off")
          #  plt.imshow(wc, interpolation="bilinear")

            # create path to save wc image
           # image_path = os.path.join(app.config['IMG_FOLDER'], 'img_filename' + '.png')  
           # plt.savefig(image_path)
           # plt.close()

           # img_file = os.listdir(app.config['IMG_FOLDER'])[0]
            #full_filename = os.path.join(app.config['IMG_FOLDER'], img_file)
            full_filename = "/Users/andreluiz/Documents/projetos/audioTextoVoskFlask/static/wordcloud.png"

            #primeiro retorno
            return render_template('resultado.html', titulo='Transcrição', nome_arquivo=arquivo_audio, texto=transcricao_completa, user_image = full_filename)
    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
    '''

@app.route('/pasta')
def pasta():
    return app.root_path

app.run(debug=True)
