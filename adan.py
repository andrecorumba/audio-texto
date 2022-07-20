import json
from vosk import Model, KaldiRecognizer
import os
import wave
import numpy as np
from pydub import AudioSegment

#funcao que convert mp3 ou opus em wav
def mp3_to_wav(source, skip=0, excerpt=False):
    sound = AudioSegment.from_mp3(source) # load source
    sound = sound.set_channels(1) # mono
    sound = sound.set_frame_rate(16000) # 16000Hz
    
    if excerpt:
        excrept = sound[skip*1000:skip*1000+30000] # 30 seconds - Does not work anymore when using skip
        output_path = os.path.splitext(source)[0]+"_excerpt.wav"
        excrept.export(output_path, format="wav")
    else:
        audio = sound[skip*1000:]
        output_path = os.path.splitext(source)[0]+".wav"
        audio.export(output_path, format="wav")
    
    return output_path


#captura o diretorio de audios na pasta do diretorio do projeto
diretorio_projeto = os.getcwd()
diretorio_audios  = os.path.join(diretorio_projeto, 'audios')

#inicializa o modelo
diretorio_modelos = os.path.join(diretorio_projeto, 'modelos')
modelo_pequeno = os.path.join(diretorio_modelos, 'vosk-model-small-pt-0.3')
print('Diretorio do Modelo: ', diretorio_modelos)
print('Modelo Pequeno:      ', modelo_pequeno)
modelo = Model(modelo_pequeno)

#captura todos os arquivos da pasta audio, degrava e grava os nomes no dicionario
tamanho = 0
conta = 0
dict_audios = {}
for nome_arquivo in os.listdir(diretorio_audios):
    conta += 1
    caminho_arquivo = os.path.join(diretorio_audios, nome_arquivo)
    tamanho += os.path.getsize(caminho_arquivo)
    print(conta, '->', nome_arquivo, '->', tamanho, 'KB', '->', caminho_arquivo)

    #arquivo de audio
    wf = wave.open(caminho_arquivo, 'rb')
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        print("Arquivo deve estar no formato WAV mono PCM.")
        exit(1)


    rec = KaldiRecognizer(modelo, wf.getframerate())
    rec.SetWords(True)
    rec.SetPartialWords(True)

    while True:
        dados = wf.readframes(4000)
        if len(dados) == 0:
            break
        if rec.AcceptWaveform(dados):
            resultado = json.loads(rec.Result())
            print(resultado)

    wf.close()

    #grava num dicionario
    dict_audios.update({ conta : {'nome' : nome_arquivo, 'tam' : tamanho, 'caminho' : caminho_arquivo} })

print(dict_audios)




