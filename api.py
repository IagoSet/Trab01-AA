from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time
from datetime import datetime
from playwright.sync_api import sync_playwright
import smtplib
from email.mime.text import MIMEText
import re

app = Flask(__name__)
CORS(app)

# Estado global da automação
estado_bot = {
    "ativo": False,
    "preco_atual": "", 
    "usuario": "",
    "email": "",
    "url": "",
    "seletor": "",
    "intervalo": 10
}

logs_sessao_atual = []

def escrever_log(mensagem, nivel="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    linha = f"[{timestamp}] [{nivel}] {mensagem}"
    print(linha)
    logs_sessao_atual.append(linha)
    if len(logs_sessao_atual) > 50:
        logs_sessao_atual.pop(0)

# ==========================================
# 1. FUNÇÃO PARA BUSCAR XPATHS (Varredura Inicial)
# ==========================================
def extrair_xpaths_reais(url):
    escrever_log(f"Iniciando varredura DOM em: {url}", "INFO")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until='networkidle')
            
            # Script JS para encontrar possíveis seletores de preço/hora
            js_code = """
            () => {
                const resultados = new Set();
                document.querySelectorAll('span, div, p, strong, h1, h2').forEach(el => {
                    const texto = (el.innerText || '').trim();
                    const classe = el.className || '';
                    const ehPreco = texto.match(/[0-9]+[.,][0-9]{2}/);
                    const ehHora = texto.match(/[0-9]{2}:[0-9]{2}/);
                    if((ehPreco || ehHora) && texto.length < 50) {
                        if(typeof classe === 'string' && classe.trim() !== '') {
                            const classPrincipal = classe.trim().split(' ')[0];
                            resultados.add(`//${el.tagName.toLowerCase()}[contains(@class, '${classPrincipal}')]`);
                        }
                    }
                });
                return Array.from(resultados).slice(0, 10);
            }
            """
            seletores = page.evaluate(js_code)
            browser.close()
            return seletores if seletores else ["//div", "//span"]
    except Exception as e:
        escrever_log(f"Erro na varredura: {e}", "ERROR")
        return []

# ==========================================
# 2. FUNÇÃO PARA ENVIAR E-MAIL
# ==========================================
def enviar_email(destinatario, url, valor_antigo, valor_novo):
    EMAIL_BOT = "jejzksnlabd@gmail.com" 
    SENHA_BOT = "udzl zmrt gltt nncj"
    if EMAIL_BOT == "SEU_EMAIL_AQUI@gmail.com": return

    assunto = "ALERTA: Alteração Detectada!"
    corpo = f"Mudança detectada!\n\nURL: {url}\nValor Antigo: {valor_antigo}\nNovo Valor: {valor_novo}"
    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = EMAIL_BOT
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_BOT, SENHA_BOT)
            server.sendmail(EMAIL_BOT, destinatario, msg.as_string())
        escrever_log(f"E-mail enviado para {destinatario}", "SUCCESS")
    except Exception as e:
        escrever_log(f"Erro SMTP: {e}", "ERROR")

# ==========================================
# 3. LOOP DE MONITORAMENTO (Uso de inner_text direto)
# ==========================================
def loop_de_monitoramento_real():
    url = estado_bot["url"]
    seletor = estado_bot["seletor"]
    
    # Prepara o seletor para o Playwright
    if seletor.startswith("//") and not seletor.startswith("xpath="):
        seletor = f"xpath={seletor}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
        page = context.new_page()
        
        while estado_bot["ativo"]:
            try:
                page.goto(url, timeout=45000, wait_until='domcontentloaded')
                time.sleep(2) 
                
                if seletor == 'auto':
                    texto_alvo = page.locator("body").inner_text()
                else:
                    # Captura o texto SEM usar page.evaluate() para evitar erros de aspas no XPath
                    elemento = page.locator(seletor).first
                    elemento.wait_for(state="visible", timeout=15000)
                    texto_alvo = elemento.inner_text()
                
                if not texto_alvo:
                    escrever_log("Elemento sem texto.", "DEBUG")
                    continue

                texto_alvo = " ".join(texto_alvo.split())
                
                # Extração simples de valor
                horas = re.findall(r'\d{1,2}:\d{2}(?::\d{2})?', texto_alvo)
                precos = re.findall(r'\d+[.,]\d{2}', texto_alvo)
                
                valor_encontrado = None
                if horas: valor_encontrado = horas[0]
                elif precos: valor_encontrado = precos[0]

                if valor_encontrado:
                    if estado_bot["preco_atual"] == "":
                        estado_bot["preco_atual"] = valor_encontrado
                        escrever_log(f"Valor inicial: {valor_encontrado}", "SUCCESS")
                    elif valor_encontrado != estado_bot["preco_atual"]:
                        valor_antigo = estado_bot["preco_atual"]
                        estado_bot["preco_atual"] = valor_encontrado
                        escrever_log(f"MUDANÇA: {valor_antigo} -> {valor_encontrado}", "WARNING")
                        enviar_email(estado_bot["email"], url, valor_antigo, valor_encontrado)
                        
            except Exception as e:
                escrever_log(f"Erro monitor: {str(e)[:60]}", "ERROR")
            
            time.sleep(int(estado_bot["intervalo"]))
        browser.close()

# ==========================================
# ROTAS DA API
# ==========================================
@app.route('/buscar_xpaths', methods=['POST'])
def buscar_xpaths():
    global logs_sessao_atual
    logs_sessao_atual.clear()
    url = request.json.get('url')
    escrever_log(f"Mapeando: {url}", "INFO")
    seletores = extrair_xpaths_reais(url)
    return jsonify({"xpaths": seletores})

@app.route('/iniciar_bot', methods=['POST'])
def iniciar_bot():
    dados = request.json
    estado_bot.update({
        "ativo": True,
        "usuario": dados.get('usuario'),
        "email": dados.get('email'),
        "url": dados.get('url'),
        "seletor": dados.get('seletor'),
        "intervalo": int(dados.get('intervalo', 10)),
        "preco_atual": ""
    })
    escrever_log(f"Bot iniciado: {estado_bot['url']}", "INFO")
    threading.Thread(target=loop_de_monitoramento_real, daemon=True).start()
    return jsonify({"status": "Iniciado"})

@app.route('/parar_bot', methods=['POST'])
def parar_bot():
    estado_bot["ativo"] = False
    escrever_log("Bot parado.", "WARNING")
    return jsonify({"status": "Parado"})

@app.route('/status', methods=['GET'])
def obter_status():
    return jsonify({"ativo": estado_bot["ativo"], "preco_atual": estado_bot["preco_atual"]})

@app.route('/logs', methods=['GET'])
def obter_logs():
    return jsonify({"logs": logs_sessao_atual})

if __name__ == '__main__':
    escrever_log("--- Servidor Ativo (Porta 5000) ---", "SYSTEM")
    app.run(port=5000)
