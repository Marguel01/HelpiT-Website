import csv
import os
import pandas as pd
import streamlit as st
from datetime import datetime
from reportlab.pdfgen import canvas
import smtplib
from email.message import EmailMessage

ARQUIVO_CSV = "problemas_ti.csv"
EMAIL_REMETENTE = "miguel007sil@gmail.com"
SENHA_APP = "lgrl ussd ztqy ityg"

# --- Funções ---

def inicializar_csv():
    if not os.path.isfile(ARQUIVO_CSV):
        with open(ARQUIVO_CSV, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Protocolo", "Data", "Usuário", "Setor", "Descrição", "Prioridade", "Patrimônio", "Categoria", "Local", "E-mail"])

def gerar_protocolo():
    return f"TI{datetime.now().strftime('%Y%m%d%H%M%S')}"

def registrar_problema(usuario, setor, descricao, prioridade, patrimonio, categoria, local, email):
    protocolo = gerar_protocolo()
    data = datetime.now().strftime('%d/%m/%Y %H:%M')
    with open(ARQUIVO_CSV, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([protocolo, data, usuario, setor, descricao, prioridade, patrimonio, categoria, local, email])
    return protocolo

def carregar_dados():
    if os.path.isfile(ARQUIVO_CSV):
        return pd.read_csv(ARQUIVO_CSV)
    return pd.DataFrame()

def autenticar(usuario, senha):
    return (usuario == "admin" and senha == "admin123") or \
           (usuario == "ravi" and senha == "12345678") or \
           (usuario == "marguel" and senha == "24012003") or\
           (usuario == "samuel" and senha == "0918")or\
           (usuario == "hermeson" and senha == "2604")or\
           (usuario == 'reinaldo' and senha == "Reimer190")

def gerar_pdf_chamado(chamado, caminho_pdf):
    c = canvas.Canvas(caminho_pdf)
    c.drawString(100, 800, f"Chamado aberto por: {chamado['usuario']}")
    c.drawString(100, 780, f"Data: {chamado['data']}")
    c.drawString(100, 760, f"Categoria: {chamado['categoria']}")
    c.drawString(100, 740, f"Prioridade: {chamado['prioridade']}")
    c.drawString(100, 720, f"Patrimônio: {chamado['patrimonio']}")
    c.drawString(100, 700, f"Local: {chamado['local']}")
    c.drawString(100, 680, f"E-mail: {chamado['email']}")
    c.drawString(100, 660, "Descrição:")
    text = c.beginText(100, 640)
    for linha in chamado["descricao"].split('\n'):
        text.textLine(linha)
    c.drawText(text)
    c.save()

def enviar_pdf_email(destinatario, chamado, caminho_pdf):
    msg = EmailMessage()
    msg['Subject'] = 'Novo chamado registrado'
    msg['From'] = EMAIL_REMETENTE
    msg['To'] = destinatario
    msg.set_content(f"Olá {chamado['usuario']}, seu chamado foi registrado com sucesso.\n\nVeja os detalhes no PDF em anexo.")

    with open(caminho_pdf, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='pdf', filename=os.path.basename(caminho_pdf))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_REMETENTE, SENHA_APP)
        smtp.send_message(msg)

# --- Inicialização ---
st.set_page_config(page_title="Sistema de Chamados TI",page_icon="https://i.ibb.co/s9fpKvjQ/logo-helpit.png", layout="centered")
inicializar_csv()
st.markdown("""
    <style>
        .stApp {
            background-color: #1E90FF;
        }
    </style>
""", unsafe_allow_html=True)

# Controle de sessão
if "logado" not in st.session_state:
    st.session_state.logado = False
    st.session_state.usuario = ""

# --- Login ---
if not st.session_state.logado:
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if autenticar(usuario, senha):
            st.session_state.logado = True
            st.session_state.usuario = usuario
            st.success("Login realizado com sucesso!")
            st.rerun()
        else:
            st.error("Usuário ou senha inválidos.")

# --- Sistema Principal ---
else:
    st.title("🛠️ Sistema de Problemas de TI")
    st.sidebar.write(f"👤 Usuário: {st.session_state.usuario}")
    menu = st.sidebar.selectbox("Menu", ["Registrar Problema", "Listar/Filtrar Problemas", "Buscar por Patrimônio", "Sair"])

    # --- Registrar Problema ---
    if menu == "Registrar Problema":
        st.subheader("📋 Registrar novo problema")
        with st.form("form_problema"):
            usuario = st.text_input("Nome do usuário", value=st.session_state.usuario)
            setor = st.text_input("Setor")
            descricao = st.text_area("Descrição do problema")
            prioridade = st.selectbox("Prioridade", ["Baixa", "Média", "Alta", "Crítica"])
            patrimonio = st.text_input("Número do patrimônio")
            categoria = st.selectbox("Categoria", ["Rede", "Impressora", "PC", "Software"])
            local = st.text_input("Local")
            email = st.text_input("E-mail")
            if email and "@" not in email:
                st.error("Por favor, insira um e-mail válido.")
            enviado = st.form_submit_button("Registrar")

            if enviado:
                if all([usuario, setor, descricao, prioridade, patrimonio, categoria, local, email]):
                    protocolo = registrar_problema(usuario, setor, descricao, prioridade, patrimonio, categoria, local, email)
                    st.success(f"✅ Problema registrado! Protocolo: {protocolo}")

                    # Gerar PDF
                    nome_pdf = f"chamado_{protocolo}.pdf"
                    gerar_pdf_chamado({
                        'usuario': usuario,
                        'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
                        'categoria': categoria,
                        'prioridade': prioridade,
                        'patrimonio': patrimonio,
                        'local': local,
                        'email': email,
                        'descricao': descricao
                    }, nome_pdf)

                    # Enviar e-mail com PDF
                    try:
                        enviar_pdf_email(email, {'usuario': usuario, 'data': datetime.now().strftime('%d/%m/%Y %H:%M'), 'categoria': categoria, 'prioridade': prioridade, 'patrimonio': patrimonio, 'local': local, 'email': email, 'descricao': descricao}, nome_pdf)
                        st.info(f"📧 PDF enviado para {email} com sucesso!")
                    except Exception as e:
                        st.error(f"Erro ao enviar e-mail: {e}")
                else:
                    st.warning("⚠️ Todos os campos são obrigatórios.")

    # --- Listar / Filtrar Problemas ---
    elif menu == "Listar/Filtrar Problemas":
        st.subheader("📄 Lista e Filtros de Problemas")
        df = carregar_dados()

        # 🔐 Filtrar por usuário, se não for admin
        if st.session_state.usuario != "admin":
            df = df[df["Usuário"] == st.session_state.usuario]

        if df.empty:
            st.info("Nenhum problema registrado ainda.")
        else:
            df["Data"] = pd.to_datetime(df["Data"], format='%d/%m/%Y %H:%M', errors='coerce')
            df = df.dropna(subset=["Data"])

            col1, col2 = st.columns(2)
            with col1:
                data_ini = st.date_input("Data inicial", value=df["Data"].min().date())
            with col2:
                data_fim = st.date_input("Data final", value=df["Data"].max().date())

            prioridade_filtro = st.multiselect(
                "Filtrar por prioridade",
                options=df["Prioridade"].dropna().unique(),
                default=list(df["Prioridade"].dropna().unique())
            )

            df_filtrado = df[
                (df["Data"].dt.date >= data_ini) &
                (df["Data"].dt.date <= data_fim) &
                (df["Prioridade"].isin(prioridade_filtro))
            ]

            st.markdown(f"{len(df_filtrado)} problema(s) encontrado(s)")
            st.dataframe(df_filtrado.sort_values(by="Data", ascending=False), use_container_width=True)

            csv_filtrado = df_filtrado.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Exportar resultados para CSV", data=csv_filtrado, file_name="problemas_filtrados.csv", mime="text/csv")

    # --- Buscar por Patrimônio ---
    elif menu == "Buscar por Patrimônio":
        st.subheader("🔎 Buscar por Patrimônio")
        patrimonio = st.text_input("Digite o número do patrimônio")
        if st.button("Buscar"):
            df = carregar_dados()

            # 🔐 Filtrar por usuário, se não for admin
            if st.session_state.usuario != "admin":
                df = df[df["Usuário"] == st.session_state.usuario]

            df["Data"] = pd.to_datetime(df["Data"], format='%d/%m/%Y %H:%M', errors='coerce')
            if "Patrimônio" in df.columns:
                resultados = df[df["Patrimônio"].astype(str).str.contains(patrimonio, na=False)]
            else:
                st.error("⚠️ A coluna 'Patrimônio' não foi encontrada no DataFrame.")
                st.write("Colunas disponíveis:", list(df.columns))
            

            if not resultados.empty:
                st.success(f"{len(resultados)} problema(s) encontrado(s) para o patrimônio {patrimonio}:")
                st.dataframe(resultados.sort_values(by="Data", ascending=False), use_container_width=True)
            else:
                st.warning("Nenhum problema encontrado para esse patrimônio.")

    # --- Sair ---
    elif menu == "Sair":
        st.session_state.logado = False
        st.session_state.usuario = ""
        st.success("Logout realizado com sucesso.")
        st.rerun()[theme]
base="dark"
backgroundColor="#6b6b6b"
secondaryBackgroundColor="#454546"
