import streamlit as st
import docx
import PyPDF2
import re
from collections import Counter
from langdetect import detect

st.title("Normalização de Texto - TP2")

def extrair_texto_bruto(ficheiro, extensao):
    texto_extraido = ""
    if extensao == 'txt':
        texto_extraido = ficheiro.read().decode('utf-8', errors='replace')
    elif extensao == 'docx':
        doc = docx.Document(ficheiro)
        texto_extraido = "\n".join([para.text for para in doc.paragraphs])
    elif extensao == 'pdf':
        leitor = PyPDF2.PdfReader(ficheiro)
        for pagina in leitor.pages:
            texto = pagina.extract_text()
            if texto:
                texto_extraido += texto + "\n"
    return texto_extraido

def limpar_texto(texto_bruto, aplicar_espacos, aplicar_quebras, aplicar_cabecalhos):
    texto_limpo = texto_bruto

    if aplicar_espacos:
        texto_limpo = re.sub(r'[ \t]+', ' ', texto_limpo)
    
    if aplicar_quebras:
        texto_limpo = re.sub(r'(?<!\n)\n(?!\n)', ' ', texto_limpo)
        texto_limpo = re.sub(r'\n\s*\n', '\n\n', texto_limpo)
        
    if aplicar_cabecalhos:
        linhas = texto_limpo.split('\n')
        contagem = Counter(linhas)
        linhas_limpas = [
            linha for linha in linhas 
            if contagem[linha] <= 2 or len(linha.strip()) > 80 or len(linha.strip()) == 0
        ]
        texto_limpo = '\n'.join(linhas_limpas)

    return texto_limpo.strip()

def segmentar_texto(texto, tamanho_chunk=1000):
    return [texto[i:i + tamanho_chunk] for i in range(0, len(texto), tamanho_chunk)]

def criar_prompt(chunk, idioma):
    instrucao = {
        "pt": "Normaliza o seguinte texto, corrigindo erros de pontuação e gramática, mantendo o sentido original:",

    }
    prefixo = instrucao.get(idioma, ingit add .strucao["pt"])
    return f"{prefixo}\n\nTEXTO:\n{chunk}"

st.sidebar.header("Configurações da Pipeline")
opt_espacos = st.sidebar.checkbox("Normalizar espaços", value=True)
opt_quebras = st.sidebar.checkbox("Corrigir quebras de linha", value=True)
opt_cabecalhos = st.sidebar.checkbox("Remover cabeçalhos/rodapés", value=True)

ficheiro_carregado = st.file_uploader(
    "Insira o documento a processar (TXT, PDF, DOCX):", 
    type=['txt', 'pdf', 'docx']
)

if ficheiro_carregado is not None:
    extensao = ficheiro_carregado.name.split('.')[-1].lower()
    
    texto_bruto = extrair_texto_bruto(ficheiro_carregado, extensao)
    
    texto_limpo = limpar_texto(texto_bruto, opt_espacos, opt_quebras, opt_cabecalhos)
    
    try:
        idioma_detetado = detect(texto_limpo)
    except:
        idioma_detetado = "pt"
        
    blocos = segmentar_texto(texto_limpo)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Texto Bruto")
        st.text_area("bruto", texto_bruto, height=400, key="t_bruto", label_visibility="collapsed")
    with col2:
        st.subheader("Texto Limpo")
        st.text_area("limpo", texto_limpo, height=400, key="t_limpo", label_visibility="collapsed")
        
    st.write("---")
    st.subheader("Resultados da Preparação (Tarefa 3)")
    st.write(f"**Idioma detetado:** {idioma_detetado}")
    st.write(f"**Número de blocos gerados:** {len(blocos)}")
    
    if blocos:
        st.text_area("Exemplo de Prompt Final (Bloco 1):", criar_prompt(blocos[0], idioma_detetado), height=200)