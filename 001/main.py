from flask import Flask, render_template, redirect,request, flash, send_from_directory
import json
import ast
import os
import mysql.connector

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dudsSantos'

logado = False

@app.route('/')
def pagInicial():
    global logado
    logado = False
    return render_template('login.html')

@app.route('/adm')
def adm():
    if logado == True:
        with open('001/usuarios.json') as usuariosTemp:
            usuarios = json.load(usuariosTemp)
        return render_template('admin.html', usuarios=usuarios) # uma variavel usuarios que recebe a lista usuarios

    if logado == False:
        return redirect('/')
    

@app.route('/home')
def home():
    if logado == True:
        arquivo = []
        for documento in os.listdir('001/upload'):
            arquivo.append(documento)

        return render_template('home.html', arquivos = arquivo)
    else:
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    global logado
    nome = request.form.get('nome')
    senha = request.form.get('senha')
    connectBD = mysql.connector.connect(host = 'localhost', database = 'aulayoutube', user = 'root', password = '')
    cont = 0
    if connectBD.is_connected():
        print('conectado')
        # o cursor serve para executar os codigos do bd ex: select/ from/ where
        cursor = connectBD.cursor()
        cursor.execute('select * from users;')
        # gera uma lista com os dados da tabela enviada pelo comando no cursor
        usuariosBD = cursor.fetchall()
        for usuario in usuariosBD:
            cont += 1
            usuarioNome = str(usuario[1])# o 1 representa a coluna de nomes e a 0 é o id na ordem da lista gerada no cursor
            usuarioSenha = str(usuario[2])

            if nome == 'adm' and senha == '0000':
                logado = True
                return redirect('/adm')
            
            if usuarioNome == nome and usuarioSenha == senha:
                logado = True
                return redirect('/home')
            
            if cont >= len(usuariosBD):
                flash('usuário inválido')
                return redirect('/')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    global logado
    logado = True

    return redirect('/adm')


@app.route('/excluir',  methods=['POST'])
def excluir():
    global logado
    logado = True
    usuario = request.form.get('usuarioPexcluir')
    # transformando a str usuario em dicionario para poder excluir do arquivo json
    usuarioDicio = ast.literal_eval(usuario) #ast é uma biblioteca que faz a conversão
    nome = usuarioDicio['nome']
    with open ('001/usuarios.json') as usuariosTemp:
        usuariosJson = json.load(usuariosTemp)
        for c in usuariosJson:
            if c == usuarioDicio:
                usuariosJson.remove(usuarioDicio)
                with open('001/usuarios.json', 'w') as  excluirTemp:
                    json.dump(usuariosJson, excluirTemp, indent=4)
    flash(f'{nome} Excluido')
    return redirect('/adm')

@app.route('/upload', methods=['POST'])
def upload():
    global logado
    logado = True

    arquivo = request.files.get('documento')

    if arquivo is None:
        flash('Nenhum arquivo enviado')
        return redirect('/adm')
    
    nomeArquivo = arquivo.filename.replace(" ", "-")
    arquivo.save(os.path.join('001/upload', nomeArquivo))

    flash(f'Arquivo Salvo')
    return redirect('/adm')

@app.route('/download', methods=['POST'])
def download():
    nomeArquivo = request.form.get('arquivosParaDownload')

    return send_from_directory('upload', nomeArquivo, as_attachment=True)

if __name__ in "__main__":
    app.run(debug=True) 