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
    "preco_atual": 0.0,
    "usuario": "",
    "email": "",
    "url": "",
    "seletor": "",
    "intervalo": 10
}

# NOVA IMPLEMENTAÇÃO: Memória de curto prazo para o Front-end
logs_sessao_atual = []

def escrever_log(mensagem, nivel="INFO"):
    """Grava o log no arquivo persistente e na memória da interface"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    linha = f"[{timestamp}] [{nivel}] {mensagem}"
    
    # 1. Salva no arquivo permanentemente (O Back-end guarda tudo)
    with open('app.log', 'a', encoding='utf-8') as f:
        f.write(linha + "\n")
        
    # 2. Salva na memória da sessão para o Front-end exibir
    logs_sessao_atual.append(linha)

# ==========================================
# 1. FUNÇÃO REAL PARA BUSCAR XPATHS
# ==========================================
def extrair_xpaths_reais(url):
    escrever_log(f"Iniciando varredura DOM (Playwright) em: {url}", "INFO")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000, wait_until='networkidle')
            
            js_code = """
            () => {
                const resultados = new Set();
                document.querySelectorAll('span, div, p, strong').forEach(el => {
                    const texto = el.innerText || '';
                    const classe = el.className || '';
                    if(texto.match(/[0-9]+[.,][0-9]{2}/) || (typeof classe === 'string' && classe.toLowerCase().includes('price'))) {
                        if(typeof classe === 'string' && classe.trim() !== '') {
                            const classPrincipal = classe.trim().split(' ')[0];
                            resultados.add(`//${el.tagName.toLowerCase()}[contains(@class, '${classPrincipal}')]`);
                        }
                    }
                });
                return Array.from(resultados).slice(0, 8);
            }
            """
            seletores_js = page.evaluate(js_code)
            browser.close()
            
            if seletores_js:
                escrever_log(f"Sucesso: {len(seletores_js)} seletores mapeados.", "SUCCESS")
                return seletores_js
            else:
                escrever_log("Nenhum seletor óbvio. Recomendado uso Heurístico.", "WARNING")
                return ["//span[@class='price']", "//div[contains(@class, 'value')]"] 
                
    except Exception as e:
        escrever_log(f"Erro na varredura inicial: {e}", "ERROR")
        return []

# ==========================================
# 2. FUNÇÃO PARA ENVIAR E-MAIL
# ==========================================
def enviar_email(destinatario, url, preco_antigo, preco_novo):
    # COLOQUE SEUS DADOS REAIS AQUI PARA FUNCIONAR
    EMAIL_BOT = "jejzksnlabd@gmail.com" 
    SENHA_BOT = "udzl zmrt gltt nncj"

    if EMAIL_BOT == "SEU_EMAIL_AQUI@gmail.com":
        escrever_log("Envio cancelado: Credenciais de e-mail não configuradas.", "WARNING")
        return

    assunto = "ALERTA: Alteração de Preço Detectada!"
    corpo = f"Mudança de preço no leilão!\n\nURL: {url}\nPreço Antigo: R$ {preco_antigo}\nNovo Preço: R$ {preco_novo}\n"
    msg = MIMEText(corpo)
    msg['Subject'] = assunto
    msg['From'] = EMAIL_BOT
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_BOT, SENHA_BOT)
            server.sendmail(EMAIL_BOT, destinatario, msg.as_string())
        escrever_log(f"[Notifier] E-mail enviado para {destinatario}", "SUCCESS")
    except Exception as e:
        escrever_log(f"[Notifier] Erro SMTP: {e}", "ERROR")

# ==========================================
# 3. LOOP DE MONITORAMENTO (Scraping Real)
# ==========================================
def loop_de_monitoramento_real():
    url = estado_bot["url"]
    seletor = estado_bot["seletor"]
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        while estado_bot["ativo"]:
            try:
                page.goto(url, timeout=30000, wait_until='domcontentloaded')
                time.sleep(2) 
                
                texto_alvo = page.locator("body").inner_text() if seletor == 'auto' else page.locator(seletor).first.inner_text()
                
                numeros = re.findall(r'\d+[.,]\d+', texto_alvo)
                if numeros:
                    preco_limpo = numeros[0].replace('.', '').replace(',', '.')
                    novo_preco = float(preco_limpo)
                    
                    if estado_bot["preco_atual"] == 0.0:
                        estado_bot["preco_atual"] = novo_preco
                        escrever_log(f"Preço base registrado: R$ {novo_preco:.2f}", "INFO")
                    
                    elif novo_preco != estado_bot["preco_atual"]:
                        preco_antigo = estado_bot["preco_atual"]
                        estado_bot["preco_atual"] = novo_preco
                        escrever_log(f"VARIAÇÃO DETECTADA! De R$ {preco_antigo:.2f} para R$ {novo_preco:.2f}", "WARNING")
                        enviar_email(estado_bot["email"], url, preco_antigo, novo_preco)
                        
            except Exception as e:
                escrever_log(f"Falha de leitura no ciclo: {str(e)[:40]}...", "ERROR")
            
            time.sleep(estado_bot["intervalo"])
            
        browser.close()

# ==========================================
# ROTAS DA API
# ==========================================
@app.route('/buscar_xpaths', methods=['POST'])
def buscar_xpaths():
    global logs_sessao_atual
    logs_sessao_atual.clear() # Limpa o terminal do front a cada nova busca!
    
    url = request.json.get('url')
    escrever_log(f"Usuário solicitou mapeamento para: {url}", "INFO")
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
        "preco_atual": 0.0
    })
    
    escrever_log(f"'{estado_bot['usuario']}' INICIOU o monitor. Intervalo: {estado_bot['intervalo']}s.", "INFO")
    threading.Thread(target=loop_de_monitoramento_real, daemon=True).start()
    return jsonify({"status": "Iniciado"})

@app.route('/parar_bot', methods=['POST'])
def parar_bot():
    estado_bot["ativo"] = False
    escrever_log(f"Monitoramento parado manualmente.", "WARNING")
    return jsonify({"status": "Parado"})

@app.route('/status', methods=['GET'])
def obter_status():
    return jsonify({"ativo": estado_bot["ativo"], "preco_atual": estado_bot["preco_atual"]})

# Nova rota para o Front-end pegar apenas os logs da sessão atual
@app.route('/logs', methods=['GET'])
def obter_logs():
    return jsonify({"logs": logs_sessao_atual})

if __name__ == '__main__':
    escrever_log("--- Servidor API (Backend) Reiniciado ---", "SYSTEM")
    app.run(port=5000, debug=True)