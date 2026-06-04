from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from math import exp, log, sqrt
from scipy.integrate import quad
import numpy as np

app = FastAPI(
    title="Plataforma de Engenharia Bioquímica",
    description="Cinética bioquímica, engenharia enzimática, esterilização, reatores, Fogler e Levenspiel.",
    version="5.0"
)

# ============================================================
# MODELOS DE ENTRADA
# ============================================================

class DadosEnzima(BaseModel):
    S: List[float]
    v: List[float]


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def validar_dados_enzima(S, v):
    if len(S) != len(v):
        raise HTTPException(status_code=400, detail="S e v devem ter o mesmo tamanho.")
    if len(S) < 3:
        raise HTTPException(status_code=400, detail="Use pelo menos 3 pontos experimentais.")
    if np.any(S <= 0) or np.any(v <= 0):
        raise HTTPException(status_code=400, detail="Todos os valores de S e v devem ser positivos.")


def regressao_linear(x, y):
    x = np.array(x, dtype=float)
    y = np.array(y, dtype=float)
    a, b = np.polyfit(x, y, 1)
    y_calc = a * x + b
    ss_res = np.sum((y - y_calc) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r2 = 1 - ss_res / ss_tot if ss_tot != 0 else 0
    return a, b, r2


def metricas_original(S, v, Vmax, Km):
    v_pred = (Vmax * S) / (Km + S)
    sse = float(np.sum((v - v_pred) ** 2))
    rmse = float(np.sqrt(np.mean((v - v_pred) ** 2)))
    mae = float(np.mean(np.abs(v - v_pred)))
    return v_pred, sse, rmse, mae


@app.get("/")
def home():
    return {
        "mensagem": "Plataforma de Engenharia Bioquímica funcionando!",
        "versao": "5.0"
    }


# ============================================================
# CINÉTICA BIOQUÍMICA
# ============================================================

@app.get("/bioquimica/monod")
def monod(mumax: float, ks: float, s: float):
    if ks + s == 0:
        raise HTTPException(status_code=400, detail="Ks + S não pode ser zero.")
    mu = mumax * s / (ks + s)
    return {"modelo": "Monod", "equacao": "mu = mumax*S/(Ks + S)", "mu": mu, "mumax": mumax, "Ks": ks, "S": s}


@app.get("/bioquimica/haldane")
def haldane(mumax: float, ks: float, s: float, ki: float):
    if ki == 0:
        raise HTTPException(status_code=400, detail="Ki não pode ser zero.")
    den = ks + s + (s**2)/ki
    if den == 0:
        raise HTTPException(status_code=400, detail="Denominador não pode ser zero.")
    mu = mumax*s/den
    return {"modelo": "Haldane/Andrews", "equacao": "mu = mumax*S/(Ks + S + S²/Ki)", "mu": mu}


@app.get("/bioquimica/contois")
def contois(mumax: float, s: float, x: float, ks: float):
    den = ks*x + s
    if den == 0:
        raise HTTPException(status_code=400, detail="Ks*X + S não pode ser zero.")
    mu = mumax*s/den
    return {"modelo": "Contois", "equacao": "mu = mumax*S/(Ks*X + S)", "mu": mu}


@app.get("/bioquimica/luedeking-piret")
def luedeking_piret(alpha: float, beta: float, mu: float, x: float):
    rp = alpha*mu*x + beta*x
    return {"modelo": "Luedeking-Piret", "equacao": "rP = alpha*mu*X + beta*X", "taxa_formacao_produto_rP": rp}


# ============================================================
# ENGENHARIA ENZIMÁTICA
# ============================================================

@app.get("/enzimatica/michaelis")
def michaelis(vmax: float, km: float, s: float):
    if km + s == 0:
        raise HTTPException(status_code=400, detail="Km + S não pode ser zero.")
    v = vmax*s/(km+s)
    return {"modelo": "Michaelis-Menten", "equacao": "v = Vmax*S/(Km + S)", "Vmax": vmax, "Km": km, "S": s, "v": v}


@app.post("/enzimatica/lineweaver-burk")
def lineweaver_burk(dados: DadosEnzima):
    S = np.array(dados.S, dtype=float)
    v = np.array(dados.v, dtype=float)
    validar_dados_enzima(S, v)
    x = 1/S
    y = 1/v
    a, b, r2 = regressao_linear(x, y)
    if b == 0:
        raise HTTPException(status_code=400, detail="Coeficiente linear igual a zero.")
    Vmax = 1/b
    Km = a*Vmax
    v_pred, sse, rmse, mae = metricas_original(S, v, Vmax, Km)
    return {"modelo": "Lineweaver-Burk", "equacao_linear": "1/v = (Km/Vmax)(1/S) + 1/Vmax", "Vmax": float(Vmax), "Km": float(Km), "R2_linear": float(r2), "SSE_original": sse, "RMSE_original": rmse, "MAE_original": mae, "v_predito": [float(i) for i in v_pred]}


@app.post("/enzimatica/hanes-woolf")
def hanes_woolf(dados: DadosEnzima):
    S = np.array(dados.S, dtype=float)
    v = np.array(dados.v, dtype=float)
    validar_dados_enzima(S, v)
    x = S
    y = S/v
    a, b, r2 = regressao_linear(x, y)
    if a == 0:
        raise HTTPException(status_code=400, detail="Coeficiente angular igual a zero.")
    Vmax = 1/a
    Km = b*Vmax
    v_pred, sse, rmse, mae = metricas_original(S, v, Vmax, Km)
    return {"modelo": "Hanes-Woolf", "equacao_linear": "S/v = (1/Vmax)S + Km/Vmax", "Vmax": float(Vmax), "Km": float(Km), "R2_linear": float(r2), "SSE_original": sse, "RMSE_original": rmse, "MAE_original": mae, "v_predito": [float(i) for i in v_pred]}


@app.post("/enzimatica/eadie-hofstee")
def eadie_hofstee(dados: DadosEnzima):
    S = np.array(dados.S, dtype=float)
    v = np.array(dados.v, dtype=float)
    validar_dados_enzima(S, v)
    x = v/S
    y = v
    a, b, r2 = regressao_linear(x, y)
    Km = -a
    Vmax = b
    v_pred, sse, rmse, mae = metricas_original(S, v, Vmax, Km)
    return {"modelo": "Eadie-Hofstee", "equacao_linear": "v = -Km(v/S) + Vmax", "Vmax": float(Vmax), "Km": float(Km), "R2_linear": float(r2), "SSE_original": sse, "RMSE_original": rmse, "MAE_original": mae, "v_predito": [float(i) for i in v_pred]}


@app.post("/enzimatica/comparativo")
def comparativo(dados: DadosEnzima):
    resultados = {
        "Lineweaver-Burk": lineweaver_burk(dados),
        "Hanes-Woolf": hanes_woolf(dados),
        "Eadie-Hofstee": eadie_hofstee(dados)
    }
    tabela = []
    for nome, r in resultados.items():
        tabela.append({"modelo": nome, "Vmax": r["Vmax"], "Km": r["Km"], "R2_linear": r["R2_linear"], "SSE_original": r["SSE_original"], "RMSE_original": r["RMSE_original"], "MAE_original": r["MAE_original"]})
    ranking = sorted(tabela, key=lambda item: item["SSE_original"])
    return {"tipo": "Comparativo de ajustes enzimáticos", "criterio": "Melhor modelo = menor SSE na equação original de Michaelis-Menten", "melhor_modelo": ranking[0]["modelo"], "tabela_comparativa": tabela, "ranking": ranking, "resultados_detalhados": resultados}

@app.get("/bioquimica/fermentador-continuo")
def fermentador_continuo(mumax: float, ks: float, s: float, s0: float, yxs: float):
    if ks + s == 0:
        raise HTTPException(status_code=400, detail="Ks + S não pode ser zero.")

    mu = mumax * s / (ks + s)
    d = mu
    x = yxs * (s0 - s)
    produtividade_biomassa = d * x

    return {
        "modelo": "Fermentador contínuo - Monod",
        "equacoes": [
            "mu = mumax*S/(Ks + S)",
            "D = mu",
            "X = Yxs*(S0 - S)",
            "Produtividade_X = D*X"
        ],
        "mu": mu,
        "D": d,
        "X": x,
        "produtividade_biomassa": produtividade_biomassa
    }


@app.get("/bioquimica/rendimento-celular")
def rendimento_celular(x0: float, x: float, s0: float, s: float):
    substrato_consumido = s0 - s
    biomassa_formada = x - x0

    if substrato_consumido == 0:
        raise HTTPException(status_code=400, detail="S0 - S não pode ser zero.")

    yxs = biomassa_formada / substrato_consumido

    return {
        "modelo": "Rendimento celular",
        "equacao": "Yx/s = (X - X0)/(S0 - S)",
        "biomassa_formada": biomassa_formada,
        "substrato_consumido": substrato_consumido,
        "Yxs": yxs
    }


@app.get("/bioquimica/rendimento-produto")
def rendimento_produto(p0: float, p: float, s0: float, s: float):
    substrato_consumido = s0 - s
    produto_formado = p - p0

    if substrato_consumido == 0:
        raise HTTPException(status_code=400, detail="S0 - S não pode ser zero.")

    yps = produto_formado / substrato_consumido

    return {
        "modelo": "Rendimento de produto",
        "equacao": "Yp/s = (P - P0)/(S0 - S)",
        "produto_formado": produto_formado,
        "substrato_consumido": substrato_consumido,
        "Yps": yps
    }


@app.get("/bioquimica/produtividade")
def produtividade(produto_formado: float, volume: float, tempo: float):
    if volume <= 0 or tempo <= 0:
        raise HTTPException(status_code=400, detail="Volume e tempo devem ser maiores que zero.")

    produtividade = produto_formado / (volume * tempo)

    return {
        "modelo": "Produtividade volumétrica",
        "equacao": "Produtividade = produto formado/(V*t)",
        "produtividade": produtividade
    }


@app.get("/bioquimica/washout")
def washout(mumax: float):
    return {
        "modelo": "Washout",
        "conceito": "Ocorre quando D >= mu máximo efetivo.",
        "D_critico_aproximado": mumax
    }
# ============================================================
# ESTERILIZAÇÃO DE FERMENTADORES
# ============================================================

@app.get("/esterilizacao/espera-termica")
def espera_termica(
    volume_m3: float,
    n0_por_m3: float,
    n_final_total: float,
    kd_min: float
):
    """
    Morte microbiana de primeira ordem:
    N = N0*exp(-kd*t)
    t = ln(N0/N)/kd
    """
    n0_total = volume_m3 * n0_por_m3
    if n0_total <= 0 or n_final_total <= 0 or kd_min <= 0:
        raise HTTPException(status_code=400, detail="N0, N final e kd devem ser positivos.")
    t_min = log(n0_total / n_final_total) / kd_min
    return {
        "modelo": "Esterilização descontínua - espera térmica",
        "equacao": "t = ln(N0_total/N_final_total)/kd",
        "N0_total": n0_total,
        "N_final_total": n_final_total,
        "kd_min": kd_min,
        "tempo_min": t_min,
        "tempo_h": t_min/60
    }


@app.get("/esterilizacao/aquecimento-vapor-direto")
def aquecimento_vapor_direto(
    volume_m3: float,
    densidade_kg_m3: float,
    cp_kj_kg_k: float,
    ti_c: float,
    tf_c: float,
    vazao_vapor_kg_h: float,
    calor_latente_kj_kg: float
):
    """
    Aquecimento por vapor direto:
    Q = m*Cp*(Tf-Ti)
    t = Q/(vazao_vapor*lambda)
    """
    massa = volume_m3 * densidade_kg_m3
    q_kj = massa * cp_kj_kg_k * (tf_c - ti_c)
    taxa_kj_h = vazao_vapor_kg_h * calor_latente_kj_kg
    if taxa_kj_h <= 0:
        raise HTTPException(status_code=400, detail="Taxa de calor deve ser positiva.")
    tempo_h = q_kj / taxa_kj_h
    return {
        "modelo": "Aquecimento com vapor direto",
        "equacao": "t = m*Cp*(Tf-Ti)/(m_vapor_dot*lambda)",
        "massa_meio_kg": massa,
        "calor_necessario_kj": q_kj,
        "taxa_calor_kj_h": taxa_kj_h,
        "tempo_h": tempo_h,
        "tempo_min": tempo_h*60
    }


@app.get("/esterilizacao/resfriamento-serpentina")
def resfriamento_serpentina(
    volume_m3: float,
    densidade_kg_m3: float,
    cp_kj_kg_k: float,
    ti_c: float,
    tf_c: float,
    tagua_c: float,
    u_kj_h_m2_k: float,
    area_m2: float
):
    """
    Resfriamento em tanque bem misturado com fluido frio a temperatura constante:
    T(t)-Tc = (Ti-Tc)*exp[-UA*t/(mCp)]
    t = (mCp/UA)*ln((Ti-Tc)/(Tf-Tc))
    """
    massa = volume_m3 * densidade_kg_m3
    ua = u_kj_h_m2_k * area_m2
    if ua <= 0:
        raise HTTPException(status_code=400, detail="UA deve ser positivo.")
    if ti_c <= tagua_c or tf_c <= tagua_c:
        raise HTTPException(status_code=400, detail="Ti e Tf devem ser maiores que a temperatura da água.")
    tempo_h = (massa * cp_kj_kg_k / ua) * log((ti_c - tagua_c)/(tf_c - tagua_c))
    return {
        "modelo": "Resfriamento com serpentina",
        "equacao": "t = (mCp/UA)*ln[(Ti-Tc)/(Tf-Tc)]",
        "massa_meio_kg": massa,
        "UA_kj_h_k": ua,
        "tempo_h": tempo_h,
        "tempo_min": tempo_h*60
    }


@app.get("/esterilizacao/descontinua-completa")
def esterilizacao_descontinua_completa(
    volume_m3: float = 30,
    n0_por_m3: float = 1e12,
    n_final_total: float = 1,
    kd_min: float = 2.0,
    densidade_kg_m3: float = 1000,
    cp_kj_kg_k: float = 4.18,
    ti_c: float = 25,
    test_c: float = 121,
    tf_resfriamento_c: float = 30,
    vazao_vapor_kg_h: float = 5000,
    calor_latente_kj_kg: float = 2200,
    area_m2: float = 20,
    u_kj_h_m2_k: float = 2500,
    tagua_c: float = 20
):
    espera = espera_termica(volume_m3, n0_por_m3, n_final_total, kd_min)
    aquecimento = aquecimento_vapor_direto(volume_m3, densidade_kg_m3, cp_kj_kg_k, ti_c, test_c, vazao_vapor_kg_h, calor_latente_kj_kg)
    resfriamento = resfriamento_serpentina(volume_m3, densidade_kg_m3, cp_kj_kg_k, test_c, tf_resfriamento_c, tagua_c, u_kj_h_m2_k, area_m2)
    tempo_total_min = espera["tempo_min"] + aquecimento["tempo_min"] + resfriamento["tempo_min"]
    return {
        "modelo": "Esterilização descontínua completa",
        "espera_termica": espera,
        "aquecimento": aquecimento,
        "resfriamento": resfriamento,
        "tempo_total_min": tempo_total_min,
        "tempo_total_h": tempo_total_min/60
    }


@app.get("/esterilizacao/arrhenius-kd")
def arrhenius_kd(k0_h: float, ed_kj_kmol: float, r_kj_kmol_k: float, temp_c: float):
    """
    kd = k0*exp[-Ed/(R*T)]
    T em K.
    """
    temp_k = temp_c + 273.15
    kd_h = k0_h * exp(-ed_kj_kmol/(r_kj_kmol_k*temp_k))
    return {
        "modelo": "Constante de morte por Arrhenius",
        "equacao": "kd = k0*exp[-Ed/(R*T)]",
        "T_K": temp_k,
        "kd_h": kd_h,
        "kd_min": kd_h/60
    }


@app.get("/esterilizacao/continuo-verificacao")
def continuo_verificacao(
    volume_m3: float = 30,
    n0_por_m3: float = 1e12,
    n_final_total: float = 1,
    temp_c: float = 130,
    tempo_residencia_min: float = 5,
    k0_h: float = 5.7e39,
    ed_kj_kmol: float = 2.83e5,
    r_kj_kmol_k: float = 8.314
):
    kd = arrhenius_kd(k0_h, ed_kj_kmol, r_kj_kmol_k, temp_c)
    n0_total = volume_m3 * n0_por_m3
    n_final_calc = n0_total * exp(-kd["kd_min"]*tempo_residencia_min)
    log_reducao = log(n0_total/n_final_calc) if n_final_calc > 0 else float("inf")
    log_requerido = log(n0_total/n_final_total)
    suficiente = n_final_calc <= n_final_total
    return {
        "modelo": "Verificação de esterilização contínua",
        "equacoes": [
            "kd = k0*exp[-Ed/(R*T)]",
            "N = N0*exp(-kd*t)"
        ],
        "kd": kd,
        "N0_total": n0_total,
        "N_final_criterio": n_final_total,
        "N_final_calculado": n_final_calc,
        "tempo_residencia_min": tempo_residencia_min,
        "log_reducao_calculado_ln": log_reducao,
        "log_reducao_requerido_ln": log_requerido,
        "suficiente": suficiente,
        "conclusao": "Atende ao critério" if suficiente else "Não atende ao critério"
    }


@app.get("/esterilizacao/comparacao")
def comparacao_esterilizacao(
    volume_m3: float = 30,
    n0_por_m3: float = 1e12,
    n_final_total: float = 1,
    kd_min: float = 2.0,
    densidade_kg_m3: float = 1000,
    cp_kj_kg_k: float = 4.18,
    ti_c: float = 25,
    test_c: float = 121,
    tf_resfriamento_c: float = 30,
    vazao_vapor_kg_h: float = 5000,
    calor_latente_kj_kg: float = 2200,
    area_m2: float = 20,
    u_kj_h_m2_k: float = 2500,
    tagua_c: float = 20,
    temp_cont_c: float = 130,
    tempo_residencia_cont_min: float = 5,
    k0_h: float = 5.7e39,
    ed_kj_kmol: float = 2.83e5,
    r_kj_kmol_k: float = 8.314
):
    descont = esterilizacao_descontinua_completa(volume_m3, n0_por_m3, n_final_total, kd_min, densidade_kg_m3, cp_kj_kg_k, ti_c, test_c, tf_resfriamento_c, vazao_vapor_kg_h, calor_latente_kj_kg, area_m2, u_kj_h_m2_k, tagua_c)
    cont = continuo_verificacao(volume_m3, n0_por_m3, n_final_total, temp_cont_c, tempo_residencia_cont_min, k0_h, ed_kj_kmol, r_kj_kmol_k)
    return {
        "modelo": "Comparação esterilização descontínua x contínua",
        "descontinua": descont,
        "continua": cont,
        "discussao_base": [
            "Processo descontínuo tende a ter maior tempo total por incluir aquecimento, espera térmica e resfriamento.",
            "Processo contínuo pode ter menor tempo térmico, mas exige controle rigoroso de temperatura e tempo de residência.",
            "Temperaturas maiores reduzem o tempo de retenção, mas podem aumentar degradação de nutrientes.",
            "A escolha industrial depende de risco de contaminação, produtividade, consumo energético e sensibilidade do meio."
        ]
    }


# ============================================================
# REATORES IDEAIS
# ============================================================

@app.get("/reatores/batelada-primeira-ordem")
def batelada_primeira_ordem(ca0: float, k: float, t: float):
    ca = ca0*exp(-k*t)
    x = 1 - ca/ca0
    return {"reator": "Batelada", "modelo": "Primeira ordem", "equacao": "CA = CA0*exp(-k*t)", "CA": ca, "conversao_X": x}


@app.get("/reatores/batelada-segunda-ordem")
def batelada_segunda_ordem(ca0: float, k: float, t: float):
    if ca0 == 0:
        raise HTTPException(status_code=400, detail="CA0 não pode ser zero.")
    ca = 1/((1/ca0)+k*t)
    x = 1 - ca/ca0
    return {"reator": "Batelada", "modelo": "Segunda ordem", "equacao": "1/CA - 1/CA0 = k*t", "CA": ca, "conversao_X": x}


@app.get("/reatores/batelada-tempo-primeira-ordem")
def tempo_batelada_primeira_ordem(k: float, x: float):
    if k == 0 or x >= 1:
        raise HTTPException(status_code=400, detail="k deve ser positivo e X menor que 1.")
    t = -log(1-x)/k
    return {"reator": "Batelada", "modelo": "Primeira ordem", "equacao": "t = -ln(1-X)/k", "tempo": t}


@app.get("/reatores/cstr-primeira-ordem")
def cstr_primeira_ordem(ca0: float, k: float, tau: float):
    x = k*tau/(1+k*tau)
    ca = ca0*(1-x)
    return {"reator": "CSTR", "modelo": "Primeira ordem", "equacao": "X = k*tau/(1+k*tau)", "conversao_X": x, "CA_saida": ca}


@app.get("/reatores/cstr-segunda-ordem")
def cstr_segunda_ordem(ca0: float, k: float, tau: float):
    a = k*ca0*tau
    if a == 0:
        raise HTTPException(status_code=400, detail="k*CA0*tau não pode ser zero.")
    A, B, C = a, -(2*a+1), a
    delta = B**2 - 4*A*C
    x1 = (-B - sqrt(delta))/(2*A)
    x2 = (-B + sqrt(delta))/(2*A)
    candidatos = [valor for valor in [x1, x2] if 0 <= valor < 1]
    if not candidatos:
        raise HTTPException(status_code=400, detail="Sem solução física.")
    x = candidatos[0]
    ca = ca0*(1-x)
    return {"reator": "CSTR", "modelo": "Segunda ordem", "equacao": "tau = X/[k*CA0*(1-X)^2]", "conversao_X": x, "CA_saida": ca}


@app.get("/reatores/pfr-primeira-ordem")
def pfr_primeira_ordem(ca0: float, k: float, tau: float):
    x = 1 - exp(-k*tau)
    ca = ca0*(1-x)
    return {"reator": "PFR", "modelo": "Primeira ordem", "equacao": "X = 1 - exp(-k*tau)", "conversao_X": x, "CA_saida": ca}


@app.get("/reatores/pfr-segunda-ordem")
def pfr_segunda_ordem(ca0: float, k: float, tau: float):
    a = k*ca0*tau
    x = a/(1+a)
    ca = ca0*(1-x)
    return {"reator": "PFR", "modelo": "Segunda ordem", "equacao": "X = k*CA0*tau/(1+k*CA0*tau)", "conversao_X": x, "CA_saida": ca}


@app.get("/reatores/cstr-em-serie")
def cstr_em_serie(ca0: float, k: float, tau_total: float, n: int):
    tau_i = tau_total/n
    ca = ca0
    etapas = []
    for i in range(1, n+1):
        ca_entrada = ca
        ca_saida = ca_entrada/(1+k*tau_i)
        etapas.append({"reator": i, "CA_entrada": ca_entrada, "CA_saida": ca_saida, "X_acumulada": 1-ca_saida/ca0})
        ca = ca_saida
    return {"modelo": "CSTR em série", "CA_final": ca, "X_final": 1-ca/ca0, "etapas": etapas}


@app.get("/reatores/reacao-reversivel")
def reacao_reversivel(ca0: float, cb0: float, k1: float, k2: float, t: float):
    if k2 == 0:
        raise HTTPException(status_code=400, detail="k2 não pode ser zero.")
    ctotal = ca0 + cb0
    keq = k1/k2
    ca_eq = ctotal/(1+keq)
    cb_eq = ctotal - ca_eq
    ca = ca_eq + (ca0-ca_eq)*exp(-(k1+k2)*t)
    cb = ctotal - ca
    x = None if ca0 == 0 else (ca0-ca)/ca0
    return {"modelo": "Reação reversível A <-> B", "Keq": keq, "CA_equilibrio": ca_eq, "CB_equilibrio": cb_eq, "CA": ca, "CB": cb, "conversao_X": x}


@app.get("/energia/adiabatico")
def energia_adiabatico(t0: float, delta_h: float, x: float, cp: float):
    if cp == 0:
        raise HTTPException(status_code=400, detail="Cp não pode ser zero.")
    delta_t = (-delta_h*x)/cp
    return {"modelo": "Balanço de energia adiabático", "equacao": "T = T0 + (-deltaH*X)/Cp", "delta_T": delta_t, "T_saida": t0+delta_t}


# ============================================================
# FOGLER - TÓPICOS INDEPENDENTES
# ============================================================

@app.get("/fogler-volume-cstr")
def fogler_volume_cstr(fa0: float, x: float, menos_ra: float):
    if menos_ra == 0:
        raise HTTPException(status_code=400, detail="-rA não pode ser zero.")
    return {"topico": "Fogler - Volume CSTR", "equacao": "V = FA0*X/(-rA)", "volume": fa0*x/menos_ra}


@app.get("/fogler-volume-pfr")
def fogler_volume_pfr(fa0: float, ca0: float, k: float, ordem: float, x_final: float):
    if x_final <= 0 or x_final >= 1:
        raise HTTPException(status_code=400, detail="X_final deve estar entre 0 e 1.")
    def integrando(x):
        ca = ca0*(1-x)
        return fa0/(k*(ca**ordem))
    volume, erro = quad(integrando, 0, x_final)
    return {"topico": "Fogler - Volume PFR", "equacao": "V = integral FA0/(-rA)dX", "volume": volume, "erro_integracao": erro}


@app.get("/fogler-seletividade")
def fogler_seletividade(produto_desejado: float, produto_indesejado: float):
    if produto_indesejado == 0:
        raise HTTPException(status_code=400, detail="Produto indesejado não pode ser zero.")
    return {"topico": "Fogler - Seletividade", "equacao": "S = produto desejado/produto indesejado", "seletividade": produto_desejado/produto_indesejado}


@app.get("/fogler-rendimento")
def fogler_rendimento(produto_obtido: float, produto_teorico: float):
    if produto_teorico == 0:
        raise HTTPException(status_code=400, detail="Produto teórico não pode ser zero.")
    y = produto_obtido/produto_teorico
    return {"topico": "Fogler - Rendimento reacional", "equacao": "Y = produto obtido/produto teórico", "rendimento": y, "rendimento_percentual": y*100}


# ============================================================
# LEVENSPIEL - TÓPICOS INDEPENDENTES
# ============================================================

@app.get("/levenspiel-pontos")
def levenspiel_pontos(fa0: float, ca0: float, k: float, x_final: float, numero_pontos: int = 10):
    pontos = []
    for i in range(numero_pontos+1):
        x = x_final*i/numero_pontos
        ca = ca0*(1-x)
        menos_ra = k*ca
        y = None if menos_ra == 0 else fa0/menos_ra
        pontos.append({"X": x, "CA": ca, "-rA": menos_ra, "FA0_div_menos_rA": y})
    return {"topico": "Levenspiel - Pontos do gráfico", "pontos": pontos}


@app.get("/levenspiel-area-pfr")
def levenspiel_area_pfr(fa0: float, ca0: float, k: float, x_final: float):
    def integrando(x):
        return fa0/(k*ca0*(1-x))
    volume, erro = quad(integrando, 0, x_final)
    return {"topico": "Levenspiel - Área PFR", "volume_pfr": volume, "erro_integracao": erro}


@app.get("/levenspiel-area-cstr")
def levenspiel_area_cstr(fa0: float, ca0: float, k: float, x_final: float):
    ca_saida = ca0*(1-x_final)
    menos_ra = k*ca_saida
    if menos_ra == 0:
        raise HTTPException(status_code=400, detail="-rA de saída não pode ser zero.")
    return {"topico": "Levenspiel - Área CSTR", "volume_cstr": x_final*fa0/menos_ra}


@app.get("/comparacao/cstr-pfr-batelada")
def comparacao_cstr_pfr_batelada(ca0: float, k: float, tau: float, tempo_batelada: float):
    x_cstr = k*tau/(1+k*tau)
    x_pfr = 1-exp(-k*tau)
    x_batelada = 1-exp(-k*tempo_batelada)
    return {"modelo": "Comparação CSTR x PFR x Batelada", "CSTR": {"X": x_cstr, "CA_saida": ca0*(1-x_cstr)}, "PFR": {"X": x_pfr, "CA_saida": ca0*(1-x_pfr)}, "Batelada": {"X": x_batelada, "CA_final": ca0*(1-x_batelada)}, "maior_conversao": max({"CSTR": x_cstr, "PFR": x_pfr, "Batelada": x_batelada}, key={"CSTR": x_cstr, "PFR": x_pfr, "Batelada": x_batelada}.get)}
