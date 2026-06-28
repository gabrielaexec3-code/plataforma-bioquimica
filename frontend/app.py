
import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# ======================================================
# CONFIGURAÇÃO GERAL
# ======================================================

API_URL = "https://plataforma-bioquimica-api.onrender.com"

st.set_page_config(
    page_title="ReactorOS",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================================================
# ESTILO VISUAL 
# ======================================================

st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1250px;
}

.main-title{

    font-size:58px;

    font-weight:900;

    color:#ffffff;

    letter-spacing:-2px;

    margin-bottom:0px;

}

.subtitle{

    font-size:24px;

    font-weight:600;

    color:#38bdf8;

    letter-spacing:3px;

    text-transform:uppercase;

    margin-bottom:18px;

}

.card {
    padding: 22px;
    border-radius: 18px;
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    box-shadow: 0 6px 18px rgba(15, 23, 42, 0.08);
    margin-bottom: 18px;
}

.card-title {
    font-size: 22px;
    font-weight: 700;
    color: #1d4ed8;
    margin-bottom: 8px;
}

.card-text {
    color: #1f2937;
    font-size: 16px;
    line-height: 1.8;
    text-align: justify;
    font-weight: 400;

}

.success-box {
    padding: 16px;
    border-radius: 12px;
    background-color: #ecfdf5;
    border-left: 5px solid #10b981;
    color: #065f46;
    margin-bottom: 20px;
}

.footer {
    color: #94a3b8;
    text-align: center;
    font-size: 13px;
    margin-top: 40px;
    border-top: 1px solid #334155;
    padding-top: 15px;
}

/* Cards de resultados */
div[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #cbd5e1;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

div[data-testid="stMetric"] label {
    color: #1e3a8a !important;
    font-weight: 700 !important;
    font-size: 13px !important;
}

div[data-testid="stMetricValue"] > div {
    color: #0f172a !important;
    font-weight: 800 !important;
    font-size: 26px !important;
}

div[data-testid="stMetricDelta"] {
    color: #16a34a !important;
}
</style>
""", unsafe_allow_html=True)


# ======================================================
# NOMES ACADÊMICOS, UNIDADES E FORMATAÇÃO
# ======================================================

UNIDADES = {
    "mu": "h⁻¹", "mumax": "h⁻¹", "Ks": "g/L", "Ki": "g/L", "S": "g/L",
    "v": "mol/(L.h)", "Vmax": "mol/(L.h)", "Km": "mol/L", "slope": "-", "intercept": "-", "r2": "-", "erro": "-", "erro_quadratico": "-",
    "X": "g/L", "P": "g/L", "D": "h⁻¹", "Yxs": "g/g", "Yps": "g/g", "Ypx": "g/g",
    "produtividade": "g/(L.h)", "produtividade_biomassa": "g/(L.h)", "produto_formado": "g/L", "biomassa_formada": "g/L", "substrato_consumido": "g/L",
    "N0": "UFC", "N": "UFC", "N0_total": "UFC", "N_final": "UFC", "k": "h⁻¹", "kd": "h⁻¹", "kd_min": "min⁻¹",
    "tempo": "min", "tempo_min": "min", "tempo_h": "h", "energia_kj": "kJ", "massa_kg": "kg",
    "CA": "mol/L", "CB": "mol/L", "ca0": "mol/L", "conversao_X": "-", "x": "-", "X_final": "-",
    "V": "L", "volume": "L", "volume_L": "L", "volume_m3": "m³", "tau": "h", "FA0": "mol/h",
    "menos_ra": "mol/(L.h)", "area": "L", "area_pfr": "L", "area_cstr": "L", "seletividade": "-", "rendimento": "%",
    "temperatura": "°C", "T": "K"
}

NOMES = {
    "mu": "Velocidade específica de crescimento (μ)",
    "mumax": "Velocidade máxima de crescimento (μmáx)",
    "Ks": "Constante de saturação (Ks)",
    "Ki": "Constante de inibição (Ki)",
    "S": "Concentração de substrato (S)",
    "v": "Velocidade da reação (v)",
    "Vmax": "Velocidade máxima da reação (Vmax)",
    "Km": "Constante de Michaelis-Menten (Km)",
    "slope": "Coeficiente angular",
    "intercept": "Coeficiente linear",
    "r2": "Coeficiente de determinação (R²)",
    "erro": "Erro do ajuste",
    "erro_quadratico": "Erro quadrático",
    "X": "Concentração celular (X)",
    "P": "Concentração de produto (P)",
    "D": "Taxa de diluição (D)",
    "Yxs": "Rendimento biomassa/substrato (Yx/s)",
    "Yps": "Rendimento produto/substrato (Yp/s)",
    "Ypx": "Rendimento produto/biomassa (Yp/x)",
    "produtividade": "Produtividade volumétrica",
    "produtividade_biomassa": "Produtividade de biomassa",
    "produto_formado": "Produto formado",
    "biomassa_formada": "Biomassa formada",
    "substrato_consumido": "Substrato consumido",
    "N0": "Carga microbiana inicial (N₀)",
    "N": "Carga microbiana final (N)",
    "N0_total": "Carga microbiana inicial total (N₀)",
    "N_final": "Carga microbiana final",
    "k": "Constante cinética (k)",
    "kd": "Constante de morte térmica (kd)",
    "kd_min": "Constante de morte térmica (kd)",
    "tempo": "Tempo de processo",
    "tempo_min": "Tempo de processo",
    "tempo_h": "Tempo de processo",
    "energia_kj": "Energia térmica",
    "massa_kg": "Massa do meio",
    "CA": "Concentração do reagente A (CA)",
    "CB": "Concentração do produto B (CB)",
    "ca0": "Concentração inicial de A (CA₀)",
    "conversao_X": "Conversão do reagente (X)",
    "x": "Conversão",
    "X_final": "Conversão final",
    "volume_reator": "Volume do reator",
    "volume": "Volume",
    "volume_L": "Volume do reator",
    "volume_m3": "Volume",
    "tau": "Tempo espacial (τ)",
    "FA0": "Vazão molar inicial (FA₀)",
    "menos_ra": "Velocidade de reação (-rA)",
    "area": "Área de projeto",
    "area_pfr": "Área equivalente PFR",
    "area_cstr": "Área equivalente CSTR",
    "seletividade": "Seletividade",
    "rendimento": "Rendimento",
    "temperatura": "Temperatura",
    "T": "Temperatura absoluta"
}


def formatar_numero(v):
    """
    Formatação brasileira:
    - número inteiro: 4 -> 4,00
    - número decimal: 4.123456 -> 4,1235
    - número >= 10^4 ou < 10^-5: notação científica com 3 casas decimais
    """
    if abs(v) >= 1e4 or (abs(v) < 1e-5 and v != 0):
        mantissa, expoente = f"{v:.3e}".split("e")
        expoente = int(expoente)
        mantissa = mantissa.replace(".", ",")
        return f"{mantissa} × 10^{expoente}"

    if float(v).is_integer():
        valor = f"{v:,.2f}"
    else:
        valor = f"{v:,.4f}"

    return valor.replace(",", "X").replace(".", ",").replace("X", ".")


# Padronização para busca sem diferença entre maiúsculas e minúsculas
UNIDADES = {str(k).lower(): v for k, v in UNIDADES.items()}
NOMES = {str(k).lower(): v for k, v in NOMES.items()}

# Complemento de nomes e unidades para resultados
NOMES.update({
    "ks": "Constante de saturação (Ks)",
    "ki": "Constante de inibição (Ki)",
    "s": "Concentração de substrato (S)",
    "vmax": "Velocidade máxima da reação (Vmax)",
    "km": "Constante de Michaelis-Menten (Km)",
    "yxs": "Rendimento biomassa/substrato (Yx/s)",
    "x0": "Concentração celular inicial (X₀)",
    "p0": "Concentração inicial de produto (P₀)",
    "s0": "Concentração inicial de substrato (S₀)",
    "tempo_total_min": "Tempo total de processo",
    "tempo_aquecimento": "Tempo de aquecimento",
    "tempo_resfriamento": "Tempo de resfriamento",
    "tempo_espera": "Tempo de espera térmica",
    "volume_m3": "Volume",
    "massa": "Massa",
    "energia": "Energia térmica",
    "temperatura": "Temperatura",
    "ca": "Concentração do reagente A (CA)",
    "cb": "Concentração do produto B (CB)",
    "ca0": "Concentração inicial de A (CA₀)",
    "cb0": "Concentração inicial de B (CB₀)",
    "conversao": "Conversão",
    "x_final": "Conversão final",
    "tau_total": "Tempo espacial total (τ)",
    "tempo_batelada": "Tempo de batelada",
    "fa0": "Vazão molar inicial (FA₀)",
    "volume_cstr": "Volume do CSTR",
    "volume_pfr": "Volume do PFR",
    "produto_desejado": "Produto desejado",
    "produto_indesejado": "Produto indesejado",
    "produto_obtido": "Produto obtido",
    "produto_teorico": "Produto teórico",
    "delta_t": "Variação de temperatura (ΔT)",
    "delta_h": "Variação de entalpia (ΔH)",
    "cp": "Capacidade calorífica (Cp)",
    "k0": "Fator pré-exponencial (k₀)",
    "ed": "Energia de ativação (Ed)",
    "r": "Constante universal dos gases (R)",
    "tagua": "Temperatura da água",
    "u": "Coeficiente global de troca térmica (U)",
    "area": "Área de troca térmica",
    "rho": "Densidade do meio",
    "latente": "Calor latente",
    "vazao": "Vazão de vapor",
    "nf": "Carga microbiana final",
})

UNIDADES.update({
    # Cinética e crescimento
    "mu": "h⁻¹",
    "mumax": "h⁻¹",
    "ks": "g/L",
    "ki": "g/L",
    "s": "g/L",
    "x": "g/L",

    # Engenharia enzimática
   "vmax": "mol/(L·s)",
   "v": "mol/(L·s)",
   "km": "mol/L",
   "s": "mol/L",

    # Fermentação
    "x0": "g/L",
    "p0": "g/L",
    "s0": "g/L",
    "p": "g/L",
    "yxs": "gX/gS",
    "yps": "gP/gS",
    "ypx": "gP/gX",
    "produtividade": "g/(L·h)",
    "produto_formado": "g/L",
    "volume": "L",
    "tempo": "h",

    # Esterilização e transferência de calor
    "tempo_min": "min",
    "tempo_total_min": "min",
    "tempo_aquecimento": "min",
    "tempo_resfriamento": "min",
    "tempo_espera": "min",
    "kd": "min⁻¹",
    "kd_min": "min⁻¹",
    "k0": "h⁻¹",
    "volume_m3": "m³",
    "massa": "kg",
    "massa_kg": "kg",
    "energia": "kJ",
    "energia_kj": "kJ",
    "temperatura": "°C",
    "temp": "°C",
    "temp_c": "°C",
    "ti": "°C",
    "tf": "°C",
    "tagua": "°C",
    "delta_t": "°C",
    "rho": "kg/m³",
    "cp": "kJ/(kg·K)",
    "vazao": "kg/h",
    "latente": "kJ/kg",
    "u": "kJ/(h·m²·K)",
    "area": "m²",
    "ed": "kJ/kmol",
    "r": "kJ/(kmol·K)",
    "n0": "UFC/m³",
    "nf": "UFC",

    # Reatores
    "ca": "mol/L",
    "cb": "mol/L",
    "ca0": "mol/L",
    "cb0": "mol/L",
    "fa0": "mol/h",
    "menos_ra": "mol/(L·h)",
    "tau": "h",
    "tau_total": "h",
    "tempo_batelada": "h",
    "k": "h⁻¹",
    "k1": "h⁻¹",
    "k2": "h⁻¹",
    "volume_cstr": "L",
    "volume_pfr": "L",
    "produto_obtido": "mol",
    "produto_teorico": "mol",
    "produto_desejado": "mol",
    "produto_indesejado": "mol",
    "conversao": "%",
    "x_final": "%",
    "ordem": "-",
})

# Unidades exibidas nos campos de entrada
UNIDADES_ENTRADA = {
    # Cinética bioquímica
    "mumax": "h⁻¹",
    "mu": "h⁻¹",
    "ks": "g/L",
    "ki": "g/L",
    "s": "g/L",
    "x": "g/L",
    "alpha": "gP/gX",
    "beta": "gP/(gX·h)",

    # Engenharia enzimática
   "vmax": "mol/(L·s)",
   "km": "mol/L",
   "s": "mol/L",

    # Fermentação
    "s0": "g/L",
    "x0": "g/L",
    "p0": "g/L",
    "p": "g/L",
    "yxs": "gX/gS",
    "produto_formado": "g/L",
    "volume": "L",
    "tempo": "h",
    "volume_fermentacao": "L",

    # Esterilização
    "volume_m3": "m³",
    "n0": "UFC/m³",
    "nf": "UFC",
    "kd_min": "min⁻¹",
    "rho": "kg/m³",
    "cp_kj": "kJ/(kg·K)",
    "ti": "°C",
    "tf": "°C",
    "tagua": "°C",
    "vazao": "kg/h",
    "latente": "kJ/kg",
    "u": "kJ/(h·m²·K)",
    "area": "m²",
    "k0": "h⁻¹",
    "ed": "kJ/kmol",
    "r": "kJ/(kmol·K)",
    "temp": "°C",

    # Reatores
    "ca0": "mol/L",
    "ca": "mol/L",
    "cb0": "mol/L",
    "fa0": "mol/h",
    "menos_ra": "mol/(L·h)",
    "k": "h⁻¹",
    "k1": "h⁻¹",
    "k2": "h⁻¹",
    "tau": "h",
    "tau_total": "h",
    "tempo_batelada": "h",
    "x_final": "%",
    "conversao": "%",
    "produto_obtido": "mol",
    "produto_teorico": "mol",
    "produto_desejado": "mol",
    "produto_indesejado": "mol",
    "delta_h": "J/mol",
    "cp_j": "J/(mol·K)",
    "t0": "K",
}





NOMES.update({
    "coef_c": "Coeficiente estequiométrico de C",
    "coef_d": "Coeficiente estequiométrico de D",
    "ordem_c": "Ordem parcial em C",
    "ordem_d": "Ordem parcial em D",
    "cc": "Concentração do produto C (CC)",
    "cd": "Concentração do produto D (CD)",
})

UNIDADES.update({
    "coef_c": "-",
    "coef_d": "-",
    "ordem_c": "-",
    "ordem_d": "-",
    "cc": "mol/L",
    "cd": "mol/L",
})

UNIDADES_ENTRADA.update({
    "coef_c": "-",
    "coef_d": "-",
    "ordem_c": "-",
    "ordem_d": "-",
    "cc": "mol/L",
    "cd": "mol/L",
})

# Complemento para reações elementares e não elementares
NOMES.update({
    "coef_a": "Coeficiente estequiométrico de A",
    "coef_b": "Coeficiente estequiométrico de B",
    "coef_i": "Coeficiente de inerte",
    "ordem_a": "Ordem parcial em A",
    "ordem_b": "Ordem parcial em B",
    "ordem_global": "Ordem global da reação",
    "unidade_k": "Unidade da constante cinética",
})

UNIDADES.update({
    "coef_a": "-",
    "coef_b": "-",
    "coef_i": "-",
    "ordem_a": "-",
    "ordem_b": "-",
    "ordem_global": "-",
})

UNIDADES_ENTRADA.update({
    "coef_a": "-",
    "coef_b": "-",
    "coef_i": "-",
    "ordem_a": "-",
    "ordem_b": "-",
})

# Complemento para Cinética das Reações Químicas
NOMES.update({
    "ra_negativo": "Taxa de consumo do reagente A (-rA)",
    "ca": "Concentração do reagente A (CA)",
    "cb": "Concentração do reagente B (CB)",
    "cc": "Concentração do produto C (CC)",
    "cd": "Concentração do produto D (CD)",
    "ca0": "Concentração inicial do reagente A (CA₀)",
    "cb0": "Concentração inicial do reagente B (CB₀)",
    "fa": "Vazão molar de A (FA)",
    "fa0": "Vazão molar inicial de A (FA₀)",
    "k": "Constante cinética (k)",
    "k1": "Constante direta (k₁)",
    "k2": "Constante inversa (k₂)",
    "ordem": "Ordem da reação (n)",
    "epsilon": "Fator de variação volumétrica (ε)",
    "dxdt": "Taxa de variação celular (dX/dt)",
    "velocidade_especifica": "Velocidade específica (μ)",
    "v0": "Vazão volumétrica inicial (v₀)",
    "vazao_volumetrica": "Vazão volumétrica",
    "volume_reator": "Volume do reator",
    "keq": "Constante de equilíbrio (K)",
    "ea": "Energia de ativação (Ea)",
    "r_gases": "Constante universal dos gases (R)",
    "temperatura_k": "Temperatura absoluta (T)",
    "tempo_espacial": "Tempo espacial (τ)",
    "conversao": "Conversão do reagente A (X)",
    "volume_relativo": "Variação relativa de volume (V/V₀)",
})

UNIDADES.update({
    "ra_negativo": "mol/(L·h)",
    "ca": "mol/L",
    "cb": "mol/L",
    "cc": "mol/L",
    "cd": "mol/L",
    "ca0": "mol/L",
    "cb0": "mol/L",
    "fa": "mol/h",
    "fa0": "mol/h",
    "k": "conforme a ordem",
    "k1": "h⁻¹",
    "k2": "h⁻¹",
    "ordem": "-",
    "epsilon": "-",
    "dxdt": "g/(L·h)",
    "velocidade_especifica": "h⁻¹",
    "v0": "L/h",
    "vazao_volumetrica": "L/h",
    "volume_reator": "L",
    "keq": "-",
    "ea": "J/mol",
    "r_gases": "J/(mol·K)",
    "temperatura_k": "K",
    "tempo_espacial": "h",
    "conversao": "-",
    "volume_relativo": "-",
})

UNIDADES_ENTRADA.update({
    "ra_negativo": "mol/(L·h)",
    "ca": "mol/L",
    "cb": "mol/L",
    "cc": "mol/L",
    "cd": "mol/L",
    "ca0": "mol/L",
    "cb0": "mol/L",
    "fa": "mol/h",
    "fa0": "mol/h",
    "k": "conforme a ordem",
    "k1": "h⁻¹",
    "k2": "h⁻¹",
    "ordem": "-",
    "epsilon": "-",
    "dxdt": "g/(L·h)",
    "v0": "L/h",
    "vazao_volumetrica": "L/h",
    "volume_reator": "L",
    "keq": "-",
    "ea": "J/mol",
    "r_gases": "J/(mol·K)",
    "temperatura_k": "K",
    "conversao": "-",
})

def rotulo(campo):
    chave = str(campo).lower()
    nome = NOMES.get(chave, campo)
    unidade = UNIDADES_ENTRADA.get(chave, "")
    if unidade:
        return f"{nome} [{unidade}]"
    return nome

def unidade_k_por_ordem(ordem_global):
    """
    Unidade de k considerando:
    - taxa (-rA) em mol/(L·h)
    - concentração em mol/L
    - ordem global n
    """
    try:
        n = float(ordem_global)
    except Exception:
        return "conforme a ordem"

    if abs(n) < 1e-12:
        return "mol/(L·h)"
    if abs(n - 1) < 1e-12:
        return "h⁻¹"
    if abs(n - 2) < 1e-12:
        return "L/(mol·h)"

    expoente = n - 1
    if abs(expoente - round(expoente)) < 1e-12:
        expoente_txt = str(int(round(expoente)))
    else:
        expoente_txt = f"{expoente:.2f}".replace(".", ",")

    return f"L^{expoente_txt}/(mol^{expoente_txt}·h)"


def rotulo_k(ordem_global):
    return f"Constante cinética (k) [{unidade_k_por_ordem(ordem_global)}]"


def componente_ativo(coef):
    return float(coef) > 0


def calcular_taxa_multicomponente(k, ca, cb, coef_a, coef_b, ordem_a, ordem_b):
    """
    Calcula -rA = k CA^ordem_A CB^ordem_B,
    considerando somente componentes com coeficiente estequiométrico > 0.
    """
    taxa = k

    if componente_ativo(coef_a):
        taxa *= ca ** ordem_a

    if componente_ativo(coef_b):
        taxa *= cb ** ordem_b

    return taxa


def grafico_taxa_multicomponente(k, ca_ref, cb_ref, coef_a, coef_b, ordem_a, ordem_b):
    """
    Gráfico didático da taxa:
    - Se A existir, varia CA mantendo CB fixo.
    - Se A não existir e B existir, varia CB.
    """
    if componente_ativo(coef_a):
        ca = np.linspace(0.001, max(10, ca_ref * 3), 160)
        cb = cb_ref
        taxa = []
        for ca_i in ca:
            taxa.append(calcular_taxa_multicomponente(k, ca_i, cb, coef_a, coef_b, ordem_a, ordem_b))
        df = pd.DataFrame({"Concentração CA": ca, "-rA": taxa})
        grafico_linha(
            df,
            "Concentração CA",
            "-rA",
            "Representação gráfica — -rA em função de CA",
            "Somente componentes com coeficiente estequiométrico maior que zero entram no cálculo."
        )

    elif componente_ativo(coef_b):
        cb = np.linspace(0.001, max(10, cb_ref * 3), 160)
        ca = ca_ref
        taxa = []
        for cb_i in cb:
            taxa.append(calcular_taxa_multicomponente(k, ca, cb_i, coef_a, coef_b, ordem_a, ordem_b))
        df = pd.DataFrame({"Concentração CB": cb, "-rA": taxa})
        grafico_linha(
            df,
            "Concentração CB",
            "-rA",
            "Representação gráfica — -rA em função de CB",
            "Como A não participa, a taxa foi representada em função de CB."
        )

# ======================================================
# FUNÇÕES DE COMUNICAÇÃO COM A API
# ======================================================

def get(endpoint, params=None):
    if params is None:
        params = {}
    try:
        with st.spinner("Processando cálculo..."):
            r = requests.get(f"{API_URL}{endpoint}", params=params, timeout=90)
        if r.status_code != 200:
            st.error(f"Erro no backend: {r.status_code}")
            st.text(r.text)
            return None
        return r.json()
    except Exception as erro:
        st.error(f"Erro de conexão com a API: {erro}")
        return None


def post(endpoint, payload):
    try:
        with st.spinner("Processando ajuste dos dados experimentais..."):
            r = requests.post(f"{API_URL}{endpoint}", json=payload, timeout=90)
        if r.status_code != 200:
            st.error(f"Erro no backend: {r.status_code}")
            st.text(r.text)
            return None
        return r.json()
    except Exception as erro:
        st.error(f"Erro de conexão com a API: {erro}")
        return None


def ler_lista(txt):
    return [float(x.strip().replace(",", ".")) for x in txt.split(";") if x.strip()]


def mostrar_json_opcional(resultado):
    with st.expander("Ver resposta técnica da API"):
        st.json(resultado)


def mostrar_metricas(resultado):
    numeros = {
        k: v
        for k, v in resultado.items()
        if isinstance(v, (int, float))
    }

    if numeros:
        st.subheader("Resultados numéricos principais")
        cols = st.columns(min(len(numeros), 4))

        for i, (k, v) in enumerate(numeros.items()):
            with cols[i % len(cols)]:
                chave = str(k).lower()
                unidade = UNIDADES.get(chave, "")
                nome = NOMES.get(chave, k)
                valor = formatar_numero(v)

                st.metric(
                    label=nome,
                    value=f"{valor} {unidade}"
                )


def mostrar_resultado(resultado):
    if resultado:
        st.markdown('<div class="success-box">Cálculo realizado com sucesso.</div>', unsafe_allow_html=True)
        mostrar_metricas(resultado)
        mostrar_json_opcional(resultado)


# ======================================================
# FUNÇÕES GRÁFICAS
# ======================================================

def grafico_linha(df, x, y, titulo, descricao=None):
    st.subheader(titulo)
    if descricao:
        st.caption(descricao)
    st.line_chart(df, x=x, y=y, use_container_width=True)


def grafico_pontos(df, x, y, titulo, descricao=None):
    st.subheader(titulo)
    if descricao:
        st.caption(descricao)
    st.scatter_chart(df, x=x, y=y, use_container_width=True)


def grafico_monod(mumax, ks):
    S = np.linspace(0.01, max(100, ks * 20), 160)
    mu = mumax * S / (ks + S)
    df = pd.DataFrame({"Substrato S": S, "Velocidade específica μ": mu})
    grafico_linha(
        df,
        "Substrato S",
        "Velocidade específica μ",
        "Representação gráfica — Modelo de Monod",
        "Curva típica de saturação: o aumento de S eleva μ até se aproximar de μmáx."
    )


def grafico_haldane(mumax, ks, ki):
    S = np.linspace(0.01, max(100, np.sqrt(ks * ki) * 6), 180)
    mu = mumax * S / (ks + S + (S**2 / ki))
    df = pd.DataFrame({"Substrato S": S, "Velocidade específica μ": mu})
    grafico_linha(
        df,
        "Substrato S",
        "Velocidade específica μ",
        "Representação gráfica — Haldane/Andrews",
        "Modelo com inibição por substrato: após certo ponto, o aumento de S reduz μ."
    )


def grafico_contois(mumax, ks, x):
    S = np.linspace(0.01, max(100, ks * max(x, 1) * 20), 160)
    mu = mumax * S / (ks * x + S)
    df = pd.DataFrame({"Substrato S": S, "Velocidade específica μ": mu})
    grafico_linha(
        df,
        "Substrato S",
        "Velocidade específica μ",
        "Representação gráfica — Contois",
        "Modelo dependente da concentração celular X, comum em sistemas com alta densidade de biomassa."
    )


def grafico_luedeking_piret(alpha, beta, x):
    mu = np.linspace(0, 2, 120)
    rp = alpha * mu * x + beta * x
    df = pd.DataFrame({"μ": mu, "rP": rp})
    grafico_linha(
        df,
        "μ",
        "rP",
        "Representação gráfica — Luedeking-Piret",
        "Taxa de formação de produto em função da velocidade específica de crescimento."
    )


def grafico_michaelis(vmax, km):
    S = np.linspace(0.01, max(100, km * 20), 160)
    v = vmax * S / (km + S)
    df = pd.DataFrame({"Substrato S": S, "Velocidade v": v})
    grafico_linha(
        df,
        "Substrato S",
        "Velocidade v",
        "Representação gráfica — Michaelis-Menten",
        "Curva de saturação enzimática: v se aproxima de Vmax quando S é elevado."
    )


def graficos_ajuste_enzimatico(S, v):
    S = np.array(S, dtype=float)
    v = np.array(v, dtype=float)

    df_mm = pd.DataFrame({"S": S, "v experimental": v})
    grafico_pontos(
        df_mm,
        "S",
        "v experimental",
        "Dados experimentais — v × S",
        "Pontos experimentais usados para estimar Vmax e Km."
    )

    df_lb = pd.DataFrame({"1/S": 1 / S, "1/v": 1 / v})
    grafico_pontos(
        df_lb,
        "1/S",
        "1/v",
        "Linearização — Lineweaver-Burk",
        "Forma linear: 1/v em função de 1/S."
    )

    df_hw = pd.DataFrame({"S": S, "S/v": S / v})
    grafico_pontos(
        df_hw,
        "S",
        "S/v",
        "Linearização — Hanes-Woolf",
        "Forma linear: S/v em função de S."
    )

    df_eh = pd.DataFrame({"v/S": v / S, "v": v})
    grafico_pontos(
        df_eh,
        "v/S",
        "v",
        "Linearização — Eadie-Hofstee",
        "Forma linear: v em função de v/S."
    )


def grafico_fermentador_continuo(mumax, ks, s0, yxs):
    S = np.linspace(0.01, max(s0, ks * 20), 160)
    mu = mumax * S / (ks + S)
    X = yxs * np.maximum(s0 - S, 0)
    produtividade = mu * X
    df = pd.DataFrame({
        "Substrato S": S,
        "μ": mu,
        "Biomassa X": X,
        "Produtividade": produtividade
    })
    grafico_linha(
        df,
        "Substrato S",
        ["μ", "Produtividade"],
        "Fermentador contínuo — μ e produtividade em função de S",
        "Mostra o efeito da concentração de substrato sobre crescimento e produtividade estimada."
    )


def grafico_produtividade(volume, produto_formado):
    tempo = np.linspace(0.1, 20, 120)
    produtividade = produto_formado / (volume * tempo)
    df = pd.DataFrame({"Tempo": tempo, "Produtividade volumétrica": produtividade})
    grafico_linha(
        df,
        "Tempo",
        "Produtividade volumétrica",
        "Produtividade volumétrica em função do tempo",
        "Para produto fixo, o aumento do tempo reduz a produtividade média."
    )


def grafico_esterilizacao_termico(t_aquec=15, t_espera=10, t_resf=45, ti=25, test=121, tf=30):
    tempo = [0, t_aquec, t_aquec + t_espera, t_aquec + t_espera + t_resf]
    temperatura = [ti, test, test, tf]
    df = pd.DataFrame({"Tempo (min)": tempo, "Temperatura (°C)": temperatura})
    grafico_linha(
        df,
        "Tempo (min)",
        "Temperatura (°C)",
        "Perfil térmico simplificado — esterilização descontínua",
        "Representa aquecimento, espera térmica e resfriamento."
    )


def grafico_morte_microbiana(kd, n0_total=1e12, tempo_max=20):
    t = np.linspace(0, tempo_max, 160)
    N = n0_total * np.exp(-kd * t)
    df = pd.DataFrame({"Tempo (min)": t, "Sobreviventes N": N})
    grafico_linha(
        df,
        "Tempo (min)",
        "Sobreviventes N",
        "Morte microbiana — primeira ordem",
        "Representação da redução exponencial de microrganismos durante a espera térmica."
    )


def grafico_batch_primeira_ordem(ca0, k):
    t = np.linspace(0, 20, 160)
    ca = ca0 * np.exp(-k * t)
    x = 1 - ca / ca0
    df = pd.DataFrame({"Tempo": t, "CA": ca, "Conversão X": x})
    grafico_linha(df, "Tempo", ["CA", "Conversão X"], "Batelada — concentração e conversão")


def grafico_cstr_primeira_ordem(k):
    tau = np.linspace(0.01, 20, 160)
    x = k * tau / (1 + k * tau)
    df = pd.DataFrame({"Tempo espacial τ": tau, "Conversão X": x})
    grafico_linha(df, "Tempo espacial τ", "Conversão X", "CSTR — conversão em função de τ")


def grafico_pfr_primeira_ordem(k):
    tau = np.linspace(0.01, 20, 160)
    x = 1 - np.exp(-k * tau)
    df = pd.DataFrame({"Tempo espacial τ": tau, "Conversão X": x})
    grafico_linha(df, "Tempo espacial τ", "Conversão X", "PFR — conversão em função de τ")


def grafico_comparacao_reatores(k):
    tau = np.linspace(0.01, 20, 160)
    x_cstr = k * tau / (1 + k * tau)
    x_pfr = 1 - np.exp(-k * tau)
    x_batelada = 1 - np.exp(-k * tau)
    df = pd.DataFrame({
        "Tempo ou τ": tau,
        "CSTR": x_cstr,
        "PFR": x_pfr,
        "Batelada": x_batelada
    })
    grafico_linha(
        df,
        "Tempo ou τ",
        ["CSTR", "PFR", "Batelada"],
        "Comparação gráfica — CSTR × PFR × Batelada",
        "Para primeira ordem, PFR e batelada apresentam o mesmo perfil matemático em função do tempo espacial/tempo."
    )


def grafico_levenspiel(fa0, ca0, k):
    X = np.linspace(0.01, 0.95, 160)
    CA = ca0 * (1 - X)
    menos_ra = k * CA
    y = fa0 / menos_ra
    df = pd.DataFrame({"Conversão X": X, "FA0/(-rA)": y})
    grafico_linha(
        df,
        "Conversão X",
        "FA0/(-rA)",
        "Representação gráfica de projeto — FA0/(-rA) × X",
        "A área sob a curva representa o volume de um PFR; a área retangular representa o volume de um CSTR."
    )


def grafico_rendimento():
    substrato = np.linspace(1, 100, 120)
    y1 = 0.4 * substrato
    y2 = 0.6 * substrato
    df = pd.DataFrame({
        "Substrato consumido": substrato,
        "Produto/Biomassa — Y = 0,4": y1,
        "Produto/Biomassa — Y = 0,6": y2
    })
    grafico_linha(
        df,
        "Substrato consumido",
        ["Produto/Biomassa — Y = 0,4", "Produto/Biomassa — Y = 0,6"],
        "Representação gráfica de rendimento",
        "Mostra a relação entre substrato consumido e produto ou biomassa formada."
    )


def grafico_seletividade():
    desejado = np.linspace(1, 100, 120)
    indesejado_baixo = desejado / 4
    indesejado_alto = desejado / 1.5
    df = pd.DataFrame({
        "Produto desejado": desejado,
        "Indesejado — alta seletividade": indesejado_baixo,
        "Indesejado — baixa seletividade": indesejado_alto
    })
    grafico_linha(
        df,
        "Produto desejado",
        ["Indesejado — alta seletividade", "Indesejado — baixa seletividade"],
        "Representação gráfica de seletividade",
        "Quanto menor a formação de produto indesejado para o mesmo produto desejado, maior a seletividade."
    )




def texto_coeficiente(valor, especie):
    valor = float(valor)
    if valor <= 0:
        return ""
    if abs(valor - 1) < 1e-12:
        return especie
    if float(valor).is_integer():
        return f"{int(valor)}{especie}"
    return f"{formatar_numero(valor)}{especie}"


def montar_reacao_irreversivel(coef_a, coef_b, coef_i=0):
    partes = []
    if componente_ativo(coef_a):
        partes.append(texto_coeficiente(coef_a, "A"))
    if componente_ativo(coef_b):
        partes.append(texto_coeficiente(coef_b, "B"))
    if componente_ativo(coef_i):
        partes.append(texto_coeficiente(coef_i, "I"))
    if not partes:
        return "Sem reagente → Produtos"
    return " + ".join(partes) + " → Produtos"


def montar_reacao_reversivel(coef_a, coef_b, coef_c, coef_d):
    reagentes = []
    produtos = []
    if componente_ativo(coef_a):
        reagentes.append(texto_coeficiente(coef_a, "A"))
    if componente_ativo(coef_b):
        reagentes.append(texto_coeficiente(coef_b, "B"))
    if componente_ativo(coef_c):
        produtos.append(texto_coeficiente(coef_c, "C"))
    if componente_ativo(coef_d):
        produtos.append(texto_coeficiente(coef_d, "D"))
    if not reagentes:
        reagentes = ["Sem reagente"]
    if not produtos:
        produtos = ["Sem produto"]
    return " + ".join(reagentes) + " ⇌ " + " + ".join(produtos)


def expoente_latex(valor):
    valor = float(valor)
    if abs(valor) < 1e-12:
        return ""
    if abs(valor - 1) < 1e-12:
        return ""
    if valor.is_integer():
        return f"^{{{int(valor)}}}"
    return f"^{{{valor:.2f}}}"


def montar_lei_velocidade_irreversivel(ordem_a, ordem_b, coef_a, coef_b):
    termos = []
    if componente_ativo(coef_a):
        termos.append("C_A" + expoente_latex(ordem_a))
    if componente_ativo(coef_b):
        termos.append("C_B" + expoente_latex(ordem_b))
    if not termos:
        return r"-r_A = 0"
    return r"-r_A = k" + "".join(termos)


def montar_lei_velocidade_reversivel(ordem_a, ordem_b, ordem_c, ordem_d, coef_a, coef_b, coef_c, coef_d):
    ida = []
    volta = []
    if componente_ativo(coef_a):
        ida.append("C_A" + expoente_latex(ordem_a))
    if componente_ativo(coef_b):
        ida.append("C_B" + expoente_latex(ordem_b))
    if componente_ativo(coef_c):
        volta.append("C_C" + expoente_latex(ordem_c))
    if componente_ativo(coef_d):
        volta.append("C_D" + expoente_latex(ordem_d))
    ida_txt = "".join(ida) if ida else "1"
    volta_txt = "".join(volta) if volta else "1"
    return r"-r_A = k_1" + ida_txt + r" - k_2" + volta_txt


def calcular_taxa_reversivel_geral(k1, k2, ca, cb, cc, cd, coef_a, coef_b, coef_c, coef_d, ordem_a, ordem_b, ordem_c, ordem_d):
    termo_ida = k1
    termo_volta = k2
    if componente_ativo(coef_a):
        termo_ida *= ca ** ordem_a
    if componente_ativo(coef_b):
        termo_ida *= cb ** ordem_b
    if componente_ativo(coef_c):
        termo_volta *= cc ** ordem_c
    if componente_ativo(coef_d):
        termo_volta *= cd ** ordem_d
    return termo_ida - termo_volta

# ======================================================
# FUNÇÕES GRÁFICAS - CINÉTICA DAS REAÇÕES QUÍMICAS
# ======================================================

def grafico_taxa_irreversivel(k, n):
    ca = np.linspace(0.001, 10, 160)
    ra = k * ca**n
    df = pd.DataFrame({"Concentração CA": ca, "-rA": ra})
    grafico_linha(
        df,
        "Concentração CA",
        "-rA",
        "Representação gráfica — taxa irreversível",
        "Mostra a influência de CA e da ordem da reação sobre a taxa -rA."
    )


def grafico_taxa_reversivel_primeira(k1, k2, ca0, cb0):
    X = np.linspace(0, 0.95, 160)
    ca = ca0 * (1 - X)
    cb = cb0 + ca0 * X
    ra = k1 * ca - k2 * cb
    df = pd.DataFrame({"Conversão X": X, "-rA": ra, "CA": ca, "CB": cb})
    grafico_linha(
        df,
        "Conversão X",
        ["-rA", "CA", "CB"],
        "Reação reversível de 1ª ordem — taxa e concentrações",
        "A taxa diminui com o avanço da reação e tende a zero no equilíbrio."
    )


def grafico_taxa_reversivel_segunda(k1, k2, ca0, cb0):
    X = np.linspace(0, 0.95, 160)
    ca = ca0 * (1 - X)
    cb = np.maximum(cb0 - ca0 * X, 0)
    cc = ca0 * X
    cd = ca0 * X
    ra = k1 * ca * cb - k2 * cc * cd
    df = pd.DataFrame({"Conversão X": X, "-rA": ra, "CA": ca, "CB": cb})
    grafico_linha(
        df,
        "Conversão X",
        ["-rA", "CA", "CB"],
        "Reação reversível de 2ª ordem — taxa e concentrações",
        "Representação para A + B ⇌ C + D com estequiometria 1:1."
    )


def grafico_volume_constante(ca0, k, n):
    X = np.linspace(0, 0.95, 160)
    ca = ca0 * (1 - X)
    ra = k * ca**n
    df = pd.DataFrame({"Conversão X": X, "CA": ca, "-rA": ra})
    grafico_linha(
        df,
        "Conversão X",
        ["CA", "-rA"],
        "Volume constante — concentração e taxa em função da conversão",
        "Para volume constante, CA = CA₀(1-X)."
    )


def grafico_volume_variavel(ca0, epsilon, k, n):
    X = np.linspace(0, 0.95, 160)
    ca = ca0 * (1 - X) / (1 + epsilon * X)
    ra = k * ca**n
    volume_relativo = 1 + epsilon * X
    df = pd.DataFrame({"Conversão X": X, "CA": ca, "-rA": ra, "V/V0": volume_relativo})
    grafico_linha(
        df,
        "Conversão X",
        ["CA", "-rA", "V/V0"],
        "Volume variável — concentração, taxa e V/V₀",
        "Para sistemas gasosos, CA = CA₀(1-X)/(1+εX)."
    )


def grafico_arrhenius(k0, ea, r_gases):
    T = np.linspace(280, 900, 160)
    k = k0 * np.exp(-ea / (r_gases * T))
    df = pd.DataFrame({"Temperatura T": T, "Constante cinética k": k})
    grafico_linha(
        df,
        "Temperatura T",
        "Constante cinética k",
        "Arrhenius — constante cinética em função da temperatura",
        "O aumento da temperatura eleva k para reações com Ea positiva."
    )


def grafico_conversao_fa(fa0):
    X = np.linspace(0, 0.99, 160)
    fa = fa0 * (1 - X)
    df = pd.DataFrame({"Conversão X": X, "FA": fa})
    grafico_linha(
        df,
        "Conversão X",
        "FA",
        "Conversão — vazão molar de A em função de X",
        "FA = FA₀(1-X)."
    )
# ======================================================
# CABEÇALHO
# ======================================================

from pathlib import Path

BASE_DIR = Path(__file__).parent
LOGO_PATH = BASE_DIR / "logo.png"

st.markdown("""
<div class="main-title">
ReactorOS
</div>

<div class="subtitle">
Engineering Operating System
</div>

<div style="
margin-top:20px;
color:#cbd5e1;
font-size:18px;
font-weight:500;
line-height:1.7;
">
Sistema integrado para modelagem, simulação, otimização e resolução
de problemas em Engenharia Química, Engenharia Bioquímica e Processos Industriais.
</div>
""", unsafe_allow_html=True)


# ======================================================
# MODELOS DA SIDEBAR
# ======================================================

modelos_por_categoria = {
    "Cinética Bioquímica": [
        "Monod",
        "Haldane/Andrews",
        "Contois",
        "Luedeking-Piret"
    ],
    "Engenharia Enzimática": [
        "Michaelis-Menten",
        "Ajuste Lineweaver-Burk",
        "Ajuste Hanes-Woolf",
        "Ajuste Eadie-Hofstee",
        "Comparativo dos 3 ajustes"
    ],
    "Fermentação": [
        "Fermentador contínuo",
        "Rendimento celular",
        "Rendimento de produto",
        "Produtividade",
        "Washout"
    ],
    "Esterilização": [
        "Espera térmica",
        "Aquecimento com vapor direto",
        "Resfriamento com serpentina",
        "Processo descontínuo completo",
        "Arrhenius kd",
        "Verificação contínua",
        "Comparação descontínuo x contínuo"
    ],
    "Reatores Ideais": [
        "Batelada primeira ordem",
        "Batelada segunda ordem",
        "CSTR",
        "PFR"
    ]
}


# ======================================================
# SIDEBAR REACTOROS
# ======================================================

st.sidebar.markdown("""
<div style="
text-align:center;
margin-top:-45px;
margin-bottom:8px;
">
""", unsafe_allow_html=True)

if LOGO_PATH.exists():
    st.sidebar.image(str(LOGO_PATH), width=60)

st.sidebar.markdown("""
<h1 style="
color:#ffffff;
font-size:22px;
font-weight:800;
margin-top:2px;
margin-bottom:0;
text-align:center;
">
ReactorOS
</h1>

<p style="
color:#38bdf8;
font-size:9px;
font-weight:600;
letter-spacing:1px;
margin-top:0;
margin-bottom:18px;
text-align:center;
">
Engineering Operating System
</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.title("Menu de Navegação")

pagina = st.sidebar.radio(
    "Selecione a página",
    ["Aplicação", "Sobre o Projeto", "Como usar"]
)

st.sidebar.divider()

categoria = None
modelo = None
modulo_projeto = None
tipo_reator_projeto = None
modulo_cinetica_quimica = None
tipo_taxa_reacao = None
modelo_irreversivel = None
modelo_reversivel = None

if pagina == "Aplicação":

    categoria = st.sidebar.selectbox(
        "Área de estudo",
        [
            "Cinética Bioquímica",
            "Engenharia Enzimática",
            "Fermentação",
            "Esterilização",
            "Reatores Ideais",
            "Projeto de Reatores",
            "Cinética das Reações Químicas"
        ]
    )

    if categoria in modelos_por_categoria:
        modelo = st.sidebar.selectbox(
            "Modelo",
            modelos_por_categoria[categoria]
        )

    if categoria == "Projeto de Reatores":
        modulo_projeto = st.sidebar.selectbox(
            "Subtópico",
            [
                "Área",
                "Volume",
                "Comparação de Reatores",
                "Rendimento",
                "Seletividade"
            ]
        )

        if modulo_projeto in ["Área", "Volume"]:
            tipo_reator_projeto = st.sidebar.selectbox(
                "Tipo de reator",
                ["PFR", "CSTR"]
            )

    if categoria == "Cinética das Reações Químicas":
        modulo_cinetica_quimica = st.sidebar.selectbox(
            "Subtópico",
            [
                "Taxa de reação (-rA)",
                "Reações irreversíveis",
                "Reações reversíveis",
                "Volume constante",
                "Volume variável",
                "Velocidade específica (μ)",
                "Arrhenius",
                "Conversão",
                "Tempo espacial (τ)"
            ]
        )

        if modulo_cinetica_quimica == "Taxa de reação (-rA)":
            tipo_taxa_reacao = st.sidebar.selectbox(
                "Tipo de expressão cinética",
                ["Reação elementar", "Reação não elementar"]
            )

        if modulo_cinetica_quimica == "Reações irreversíveis":
            modelo_irreversivel = st.sidebar.selectbox(
                "Modelo da reação irreversível",
                [
                    "A → Produtos",
                    "2A → Produtos",
                    "A + B → Produtos",
                    "A + 2B → Produtos",
                    "2A + B → Produtos",
                    "Reação geral (aA + bB → produtos)",
                    "Reação não elementar"
                ]
            )

        if modulo_cinetica_quimica == "Reações reversíveis":
            modelo_reversivel = st.sidebar.selectbox(
                "Modelo da reação reversível",
                [
                    "A ⇌ B",
                    "A + B ⇌ C + D",
                    "Reação geral"
                ]
            )

st.sidebar.markdown("<br>" * 8, unsafe_allow_html=True)

st.sidebar.divider()

st.sidebar.markdown("""
<div style="
text-align:center;
color:#94a3b8;
font-size:13px;
line-height:1.8;
margin-bottom:10px;
">

<b>Desenvolvido por ReactorSoft</b><br><br>
Engenharia Química<br><br>
<b>ReactorOS v1.0</b><br><br>
© 2026 ReactorSoft Technologies

</div>
""", unsafe_allow_html=True)
# ======================================================
# PÁGINA SOBRE
# ======================================================

if pagina == "Sobre o Projeto":

    st.markdown("""<div class="card">
<div class="card-title">Objetivo da plataforma</div>
<div class="card-text">
Desenvolver um ambiente computacional interativo para apoiar a resolução, análise e interpretação de problemas de Engenharia das Reações Químicas e Bioquímica, integrando modelos matemáticos clássicos, fundamentos teóricos e representações gráficas aplicadas.
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="card">
<div class="card-title">Módulos Desenvolvidos</div>
<div class="card-text">
• Cinética Bioquímica<br>
• Engenharia Enzimática<br>
• Fermentação Industrial<br>
• Esterilização<br>
• Bioprocessos<br>
• Reatores Ideais<br>
• Projeto de Reatores<br>
• Cinética das Reações Químicas<br>
• Comparação entre modelos<br>
• Representações gráficas
</div>
</div>""", unsafe_allow_html=True)

    st.markdown("""<div class="card">
<div class="card-title">Arquitetura Computacional</div>
<div class="card-text">
<b>Linguagem:</b> Python<br>
<b>Interface gráfica:</b> Streamlit<br>
<b>Backend científico:</b> FastAPI<br>
<b>Hospedagem:</b> Render<br>
<b>Versionamento:</b> GitHub<br>
<b>Bibliotecas:</b> NumPy, SciPy e Pandas<br>
<b>Apoio ao desenvolvimento:</b> ChatGPT
</div>
</div>""", unsafe_allow_html=True)


# ======================================================
# COMO USAR
# ======================================================

elif pagina == "Como usar":

    st.markdown("""<div class="card">
<div class="card-title">Como utilizar a plataforma</div>
<div class="card-text">
1. Selecione <b>Aplicação</b> no menu lateral.<br>
2. Escolha a área de estudo.<br>
3. Selecione o modelo desejado.<br>
4. Preencha as variáveis de entrada.<br>
5. Clique em <b>Resolver</b> ou <b>Ajustar modelos</b>.<br>
6. Analise os resultados numéricos, equações, gráficos e resposta técnica da API.
</div>
</div>""", unsafe_allow_html=True)

    st.info("Na primeira execução, o backend gratuito no Render pode demorar alguns segundos para responder.")

# ======================================================
# APLICAÇÃO
# ======================================================

else:
    resultado = None

    # --------------------------------------------------
    # CINÉTICA BIOQUÍMICA
    # --------------------------------------------------
  
     elif categoria == "Cinética Bioquímica":

        st.header(f"Cinética Bioquímica — {modelo}")

        if modelo == "Monod":
            st.latex(r"\mu=\frac{\mu_{max}S}{K_s+S}")
            col1, col2, col3 = st.columns(3)
            with col1:
                mumax = st.number_input(rotulo("mumax"), value=0.8)
            with col2:
                ks = st.number_input(rotulo("ks"), value=2.0)
            with col3:
                s = st.number_input(rotulo("s"), value=10.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/bioquimica/monod", {"mumax": mumax, "ks": ks, "s": s})
            mostrar_resultado(resultado)
            if resultado:
                grafico_monod(mumax, ks)

        elif modelo == "Haldane/Andrews":
            st.latex(r"\mu=\frac{\mu_{max}S}{K_s+S+\frac{S^2}{K_i}}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                mumax = st.number_input(rotulo("mumax"), value=0.8)
            with col2:
                ks = st.number_input(rotulo("ks"), value=2.0)
            with col3:
                s = st.number_input(rotulo("s"), value=10.0)
            with col4:
                ki = st.number_input(rotulo("ki"), value=50.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/bioquimica/haldane", {"mumax": mumax, "ks": ks, "s": s, "ki": ki})
            mostrar_resultado(resultado)
            if resultado:
                grafico_haldane(mumax, ks, ki)

        elif modelo == "Contois":
            st.latex(r"\mu=\frac{\mu_{max}S}{K_sX+S}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                mumax = st.number_input(rotulo("mumax"), value=0.8)
            with col2:
                s = st.number_input(rotulo("s"), value=10.0)
            with col3:
                x = st.number_input(rotulo("x"), value=5.0)
            with col4:
                ks = st.number_input(rotulo("ks"), value=2.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/bioquimica/contois", {"mumax": mumax, "s": s, "x": x, "ks": ks})
            mostrar_resultado(resultado)
            if resultado:
                grafico_contois(mumax, ks, x)

        else:
            st.latex(r"r_P=\alpha \mu X+\beta X")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                alpha = st.number_input(rotulo("alpha"), value=0.5)
            with col2:
                beta = st.number_input(rotulo("beta"), value=0.1)
            with col3:
                mu = st.number_input(rotulo("mu"), value=0.6)
            with col4:
                x = st.number_input(rotulo("x"), value=10.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/bioquimica/luedeking-piret", {"alpha": alpha, "beta": beta, "mu": mu, "x": x})
            mostrar_resultado(resultado)
            if resultado:
                grafico_luedeking_piret(alpha, beta, x)

    # --------------------------------------------------
    # ENGENHARIA ENZIMÁTICA
    # --------------------------------------------------
    elif categoria == "Engenharia Enzimática":
        st.header(f"Engenharia Enzimática — {modelo}")

        if modelo == "Michaelis-Menten":
            st.latex(r"v=\frac{V_{max}S}{K_m+S}")
            col1, col2, col3 = st.columns(3)
            with col1:
                vmax = st.number_input(rotulo("vmax"), value=100.0)
            with col2:
                km = st.number_input(rotulo("km"), value=5.0)
            with col3:
                s = st.number_input(rotulo("s"), value=20.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/enzimatica/michaelis", {"vmax": vmax, "km": km, "s": s})
            mostrar_resultado(resultado)
            if resultado:
                grafico_michaelis(vmax, km)

        else:
            if modelo == "Ajuste Lineweaver-Burk":
                st.latex(r"\frac{1}{v}=\frac{K_m}{V_{max}}\frac{1}{S}+\frac{1}{V_{max}}")
                endpoint = "/enzimatica/lineweaver-burk"
            elif modelo == "Ajuste Hanes-Woolf":
                st.latex(r"\frac{S}{v}=\frac{1}{V_{max}}S+\frac{K_m}{V_{max}}")
                endpoint = "/enzimatica/hanes-woolf"
            elif modelo == "Ajuste Eadie-Hofstee":
                st.latex(r"v=-K_m\frac{v}{S}+V_{max}")
                endpoint = "/enzimatica/eadie-hofstee"
            else:
                st.info("Compara Lineweaver-Burk, Hanes-Woolf e Eadie-Hofstee pelo menor erro no modelo original.")
                endpoint = "/enzimatica/comparativo"

            st.write("Digite os dados experimentais separados por ponto e vírgula `;`.")
            col1, col2 = st.columns(2)
            with col1:
                s_texto = st.text_input("Valores de S", "1;2;4;6;8;10")
            with col2:
                v_texto = st.text_input("Valores de v", "0.9;1.5;2.2;2.6;2.9;3.1")

            if st.button("Ajustar modelos", type="primary"):
                try:
                    S = ler_lista(s_texto)
                    v = ler_lista(v_texto)
                    resultado = post(endpoint, {"S": S, "v": v})

                    if resultado:
                        if modelo == "Comparativo dos 3 ajustes":
                            st.markdown('<div class="success-box">Comparativo realizado com sucesso.</div>', unsafe_allow_html=True)
                            st.subheader("Melhor modelo")
                            st.success(resultado["melhor_modelo"])
                            st.subheader("Tabela comparativa")
                            st.dataframe(pd.DataFrame(resultado["tabela_comparativa"]), use_container_width=True)
                            st.subheader("Ranking por menor erro")
                            st.dataframe(pd.DataFrame(resultado["ranking"]), use_container_width=True)
                            mostrar_json_opcional(resultado["resultados_detalhados"])
                        else:
                            mostrar_resultado(resultado)

                        graficos_ajuste_enzimatico(S, v)

                except Exception as e:
                    st.error(f"Erro ao interpretar os dados: {e}")

    # --------------------------------------------------
    # FERMENTAÇÃO
    # --------------------------------------------------
   elif categoria == "Fermentação":

        if modelo == "Fermentador contínuo":
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                mumax = st.number_input(rotulo("mumax"), value=0.8)
            with col2:
                ks = st.number_input(rotulo("ks"), value=2.0)
            with col3:
                s = st.number_input(rotulo("s"), value=10.0)
            with col4:
                s0 = st.number_input(rotulo("s0"), value=100.0)
            with col5:
                yxs = st.number_input(rotulo("yxs"), value=0.5)

            if st.button("Resolver", type="primary"):
                resultado = get("/bioquimica/fermentador-continuo", {"mumax": mumax, "ks": ks, "s": s, "s0": s0, "yxs": yxs})
            mostrar_resultado(resultado)
            if resultado:
                grafico_fermentador_continuo(mumax, ks, s0, yxs)

        elif modelo == "Rendimento celular":
            st.latex(r"Y_{X/S}=\frac{X-X_0}{S_0-S}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                x0 = st.number_input(rotulo("x0"), value=0.0)
            with col2:
                x = st.number_input(rotulo("x"), value=30.0)
            with col3:
                s0 = st.number_input(rotulo("s0"), value=100.0)
            with col4:
                s = st.number_input(rotulo("s"), value=40.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/bioquimica/rendimento-celular", {"x0": x0, "x": x, "s0": s0, "s": s})
            mostrar_resultado(resultado)
            if resultado:
                grafico_rendimento()

        elif modelo == "Rendimento de produto":
            st.latex(r"Y_{P/S}=\frac{P-P_0}{S_0-S}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                p0 = st.number_input(rotulo("p0"), value=0.0)
            with col2:
                p = st.number_input(rotulo("p"), value=50.0)
            with col3:
                s0 = st.number_input(rotulo("s0"), value=100.0)
            with col4:
                s = st.number_input(rotulo("s"), value=40.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/bioquimica/rendimento-produto", {"p0": p0, "p": p, "s0": s0, "s": s})
            mostrar_resultado(resultado)
            if resultado:
                grafico_rendimento()

        elif modelo == "Produtividade":
            st.latex(r"P_v=\frac{\text{produto formado}}{Vt}")
            produto_formado = st.number_input(rotulo("produto_formado"), value=100.0)
            volume = st.number_input(rotulo("volume"), value=10.0)
            tempo = st.number_input(rotulo("tempo"), value=5.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/bioquimica/produtividade", {"produto_formado": produto_formado, "volume": volume, "tempo": tempo})
            mostrar_resultado(resultado)
            if resultado:
                grafico_produtividade(volume, produto_formado)

        else:
            mumax = st.number_input(rotulo("mumax"), value=0.8)
            if st.button("Resolver", type="primary"):
                resultado = get("/bioquimica/washout", {"mumax": mumax})
            mostrar_resultado(resultado)

    # --------------------------------------------------
    # ESTERILIZAÇÃO
    # --------------------------------------------------
   elif categoria == "Esterilização":

        st.header(f"Esterilização — {modelo}")

        if modelo == "Espera térmica":
            st.latex(r"t=\frac{\ln(N_0/N)}{k_d}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                volume = st.number_input(rotulo("volume_m3"), value=30.0)
            with col2:
                n0 = st.number_input(rotulo("n0"), value=1e12, format="%.2e")
            with col3:
                nf = st.number_input(rotulo("nf"), value=1.0)
            with col4:
                kd = st.number_input(rotulo("kd_min"), value=2.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/esterilizacao/espera-termica", {"volume_m3": volume, "n0_por_m3": n0, "n_final_total": nf, "kd_min": kd})
            mostrar_resultado(resultado)
            if resultado:
                grafico_morte_microbiana(kd, volume * n0)

        elif modelo == "Aquecimento com vapor direto":
            st.latex(r"t=\frac{mC_p(T_f-T_i)}{\dot{m}_{vapor}\lambda}")
            volume = st.number_input(rotulo("volume_m3"), value=30.0)
            rho = st.number_input(rotulo("rho"), value=1000.0)
            cp = st.number_input(rotulo("cp_kj"), value=4.18)
            ti = st.number_input(rotulo("ti"), value=25.0)
            tf = st.number_input(rotulo("tf"), value=121.0)
            vazao = st.number_input(rotulo("vazao"), value=5000.0)
            latente = st.number_input(rotulo("latente"), value=2200.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/esterilizacao/aquecimento-vapor-direto", {
                    "volume_m3": volume,
                    "densidade_kg_m3": rho,
                    "cp_kj_kg_k": cp,
                    "ti_c": ti,
                    "tf_c": tf,
                    "vazao_vapor_kg_h": vazao,
                    "calor_latente_kj_kg": latente
                })
            mostrar_resultado(resultado)
            if resultado:
                grafico_esterilizacao_termico(t_aquec=resultado.get("tempo_min", 15), t_espera=0, t_resf=0, ti=ti, test=tf, tf=tf)

        elif modelo == "Resfriamento com serpentina":
            st.latex(r"t=\frac{mC_p}{UA}\ln\left(\frac{T_i-T_c}{T_f-T_c}\right)")
            volume = st.number_input(rotulo("volume_m3"), value=30.0)
            rho = st.number_input(rotulo("rho"), value=1000.0)
            cp = st.number_input(rotulo("cp_kj"), value=4.18)
            ti = st.number_input(rotulo("ti"), value=121.0)
            tf = st.number_input(rotulo("tf"), value=30.0)
            tagua = st.number_input(rotulo("tagua"), value=20.0)
            u = st.number_input(rotulo("u"), value=2500.0)
            area = st.number_input(rotulo("area"), value=20.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/esterilizacao/resfriamento-serpentina", {
                    "volume_m3": volume,
                    "densidade_kg_m3": rho,
                    "cp_kj_kg_k": cp,
                    "ti_c": ti,
                    "tf_c": tf,
                    "tagua_c": tagua,
                    "u_kj_h_m2_k": u,
                    "area_m2": area
                })
            mostrar_resultado(resultado)
            if resultado:
                grafico_esterilizacao_termico(t_aquec=0, t_espera=0, t_resf=resultado.get("tempo_min", 45), ti=ti, test=ti, tf=tf)

        elif modelo == "Processo descontínuo completo":
            st.info("Valores preenchidos conforme a questão de esterilização do fermentador de 30 m³.")
            if st.button("Calcular processo descontínuo completo", type="primary"):
                resultado = get("/esterilizacao/descontinua-completa")
            mostrar_resultado(resultado)
            if resultado:
                aq = resultado.get("aquecimento", {}).get("tempo_min", 15)
                esp = resultado.get("espera_termica", {}).get("tempo_min", 10)
                resf = resultado.get("resfriamento", {}).get("tempo_min", 45)
                grafico_esterilizacao_termico(aq, esp, resf)
                grafico_morte_microbiana(2.0, 30 * 1e12, max(esp * 2, 20))

        elif modelo == "Arrhenius kd":
            st.latex(r"k_d=k_0e^{-E_d/(RT)}")
            k0 = st.number_input(rotulo("k0"), value=5.7e39, format="%.2e")
            ed = st.number_input(rotulo("ed"), value=2.83e5, format="%.2e")
            r = st.number_input(rotulo("r"), value=8.314)
            temp = st.number_input(rotulo("temp"), value=130.0)

            if st.button("Resolver", type="primary"):
                resultado = get("/esterilizacao/arrhenius-kd", {"k0_h": k0, "ed_kj_kmol": ed, "r_kj_kmol_k": r, "temp_c": temp})
            mostrar_resultado(resultado)

        elif modelo == "Verificação contínua":
            st.info("Verifica se o processo contínuo a 130 °C por 5 minutos atende ao critério de esterilidade.")
            if st.button("Verificar processo contínuo", type="primary"):
                resultado = get("/esterilizacao/continuo-verificacao")
            mostrar_resultado(resultado)
            if resultado:
                kd_min = resultado.get("kd", {}).get("kd_min", 2.0)
                grafico_morte_microbiana(kd_min, resultado.get("N0_total", 30e12), 10)

        else:
            st.info("Compara o processo descontínuo com o processo contínuo em termos de tempo térmico e critério de esterilidade.")
            if st.button("Comparar", type="primary"):
                resultado = get("/esterilizacao/comparacao")
            mostrar_resultado(resultado)
            if resultado:
                grafico_esterilizacao_termico()

    # --------------------------------------------------
    # REATORES IDEAIS
    # --------------------------------------------------
   elif categoria == "Reatores Ideais":
        st.header(f"Reatores Ideais — {modelo}")

        if modelo == "Batelada primeira ordem":
            st.latex(r"C_A=C_{A0}e^{-kt}")
            ca0 = st.number_input(rotulo("ca0"), value=10.0)
            k = st.number_input(rotulo("k"), value=0.3)
            t = st.number_input(rotulo("tempo"), value=5.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/reatores/batelada-primeira-ordem", {"ca0": ca0, "k": k, "t": t})
            mostrar_resultado(resultado)
            if resultado:
                grafico_batch_primeira_ordem(ca0, k)

        elif modelo == "Batelada segunda ordem":
            st.latex(r"\frac{1}{C_A}-\frac{1}{C_{A0}}=kt")
            ca0 = st.number_input(rotulo("ca0"), value=10.0)
            k = st.number_input(rotulo("k"), value=0.03)
            t = st.number_input(rotulo("tempo"), value=5.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/reatores/batelada-segunda-ordem", {"ca0": ca0, "k": k, "t": t})
            mostrar_resultado(resultado)
            if resultado:
                grafico_batch_primeira_ordem(ca0, k)

        elif modelo == "Tempo batelada primeira ordem":
            st.latex(r"t=\frac{-\ln(1-X)}{k}")
            k = st.number_input(rotulo("k"), value=0.3)
            x = st.number_input(rotulo("x"), value=0.8)
            if st.button("Resolver", type="primary"):
                resultado = get("/reatores/batelada-tempo-primeira-ordem", {"k": k, "x": x})
            mostrar_resultado(resultado)
            if resultado:
                grafico_batch_primeira_ordem(10, k)

        elif modelo == "CSTR primeira ordem":
            st.latex(r"X=\frac{k\tau}{1+k\tau}")
            ca0 = st.number_input(rotulo("ca0"), value=10.0)
            k = st.number_input(rotulo("k"), value=0.3)
            tau = st.number_input(rotulo("tau"), value=5.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/reatores/cstr-primeira-ordem", {"ca0": ca0, "k": k, "tau": tau})
            mostrar_resultado(resultado)
            if resultado:
                grafico_cstr_primeira_ordem(k)

        elif modelo == "CSTR segunda ordem":
            st.latex(r"\tau=\frac{X}{kC_{A0}(1-X)^2}")
            ca0 = st.number_input(rotulo("ca0"), value=10.0)
            k = st.number_input(rotulo("k"), value=0.03)
            tau = st.number_input(rotulo("tau"), value=5.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/reatores/cstr-segunda-ordem", {"ca0": ca0, "k": k, "tau": tau})
            mostrar_resultado(resultado)
            if resultado:
                grafico_cstr_primeira_ordem(k)

        elif modelo == "PFR primeira ordem":
            st.latex(r"X=1-e^{-k\tau}")
            ca0 = st.number_input(rotulo("ca0"), value=10.0)
            k = st.number_input(rotulo("k"), value=0.3)
            tau = st.number_input(rotulo("tau"), value=5.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/reatores/pfr-primeira-ordem", {"ca0": ca0, "k": k, "tau": tau})
            mostrar_resultado(resultado)
            if resultado:
                grafico_pfr_primeira_ordem(k)

        elif modelo == "PFR segunda ordem":
            st.latex(r"X=\frac{kC_{A0}\tau}{1+kC_{A0}\tau}")
            ca0 = st.number_input(rotulo("ca0"), value=10.0)
            k = st.number_input(rotulo("k"), value=0.03)
            tau = st.number_input(rotulo("tau"), value=5.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/reatores/pfr-segunda-ordem", {"ca0": ca0, "k": k, "tau": tau})
            mostrar_resultado(resultado)
            if resultado:
                grafico_pfr_primeira_ordem(k)

        elif modelo == "CSTR em série":
            ca0 = st.number_input(rotulo("ca0"), value=10.0)
            k = st.number_input(rotulo("k"), value=0.3)
            tau_total = st.number_input(rotulo("tau_total"), value=5.0)
            n = st.number_input("Número de reatores [-]", min_value=1, value=3, step=1)
            if st.button("Resolver", type="primary"):
                resultado = get("/reatores/cstr-em-serie", {"ca0": ca0, "k": k, "tau_total": tau_total, "n": n})
            mostrar_resultado(resultado)

        elif modelo == "Reação reversível":
            ca0 = st.number_input(rotulo("ca0"), value=10.0)
            cb0 = st.number_input(rotulo("cb0"), value=0.0)
            k1 = st.number_input(rotulo("k1"), value=0.4)
            k2 = st.number_input(rotulo("k2"), value=0.1)
            t = st.number_input(rotulo("tempo"), value=5.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/reatores/reacao-reversivel", {"ca0": ca0, "cb0": cb0, "k1": k1, "k2": k2, "t": t})
            mostrar_resultado(resultado)

        else:
            st.latex(r"T=T_0+\frac{-\Delta H\cdot X}{C_p}")
            t0 = st.number_input(rotulo("t0"), value=300.0)
            delta_h = st.number_input(rotulo("delta_h"), value=-50000.0)
            x = st.number_input(rotulo("x"), value=0.7)
            cp = st.number_input(rotulo("cp_j"), value=1000.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/energia/adiabatico", {"t0": t0, "delta_h": delta_h, "x": x, "cp": cp})
            mostrar_resultado(resultado)

    # --------------------------------------------------
    # PROJETO DE REATORES
    # --------------------------------------------------
    elif categoria == "Projeto de Reatores":

        if modulo_projeto == "Volume" and tipo_reator_projeto == "CSTR":
            st.header("Projeto de Reatores — Volume — CSTR")
            st.latex(r"V=\frac{F_{A0}X}{-r_A}")
            fa0 = st.number_input(rotulo("fa0"), value=10.0)
            x = st.number_input(rotulo("x"), value=0.8)
            menos_ra = st.number_input(rotulo("menos_ra"), value=2.0)
            ca0 = st.number_input("Concentração inicial de A para gráfico (CA₀) [mol/L]", value=5.0)
            k = st.number_input("Constante cinética para gráfico (k) [h⁻¹]", value=0.2)
            if st.button("Resolver", type="primary"):
                resultado = get("/fogler-volume-cstr", {"fa0": fa0, "x": x, "menos_ra": menos_ra})
            mostrar_resultado(resultado)
            if resultado:
                grafico_levenspiel(fa0, ca0, k)

        elif modulo_projeto == "Volume" and tipo_reator_projeto == "PFR":
            st.header("Projeto de Reatores — Volume — PFR")
            st.latex(r"V=\int_0^X \frac{F_{A0}}{-r_A}dX")
            fa0 = st.number_input(rotulo("fa0"), value=10.0)
            ca0 = st.number_input(rotulo("ca0"), value=5.0)
            k = st.number_input(rotulo("k"), value=0.2)
            ordem = st.number_input(rotulo("ordem"), value=1.0)
            x_final = st.number_input(rotulo("x_final"), value=0.8)
            if st.button("Resolver", type="primary"):
                resultado = get("/fogler-volume-pfr", {"fa0": fa0, "ca0": ca0, "k": k, "ordem": ordem, "x_final": x_final})
            mostrar_resultado(resultado)
            if resultado:
                grafico_levenspiel(fa0, ca0, k)

        elif modulo_projeto == "Área" and tipo_reator_projeto == "PFR":
            st.header("Projeto de Reatores — Área — PFR")
            st.latex(r"V_{PFR}=\int_0^X \frac{F_{A0}}{-r_A}dX")
            fa0 = st.number_input(rotulo("fa0"), value=10.0)
            ca0 = st.number_input(rotulo("ca0"), value=5.0)
            k = st.number_input(rotulo("k"), value=0.2)
            x_final = st.number_input(rotulo("x_final"), value=0.8)
            if st.button("Resolver", type="primary"):
                resultado = get("/levenspiel-area-pfr", {"fa0": fa0, "ca0": ca0, "k": k, "x_final": x_final})
            mostrar_resultado(resultado)
            if resultado:
                grafico_levenspiel(fa0, ca0, k)

        elif modulo_projeto == "Área" and tipo_reator_projeto == "CSTR":
            st.header("Projeto de Reatores — Área — CSTR")
            st.latex(r"V_{CSTR}=X\left(\frac{F_{A0}}{-r_A}\right)_{saída}")
            fa0 = st.number_input(rotulo("fa0"), value=10.0)
            ca0 = st.number_input(rotulo("ca0"), value=5.0)
            k = st.number_input(rotulo("k"), value=0.2)
            x_final = st.number_input(rotulo("x_final"), value=0.8)
            if st.button("Resolver", type="primary"):
                resultado = get("/levenspiel-area-cstr", {"fa0": fa0, "ca0": ca0, "k": k, "x_final": x_final})
            mostrar_resultado(resultado)
            if resultado:
                grafico_levenspiel(fa0, ca0, k)

        elif modulo_projeto == "Comparação de Reatores":
            st.header("Projeto de Reatores — Comparação de Reatores")
            ca0 = st.number_input(rotulo("ca0"), value=10.0)
            k = st.number_input(rotulo("k"), value=0.3)
            tau = st.number_input(rotulo("tau"), value=5.0)
            tempo_batelada = st.number_input(rotulo("tempo_batelada"), value=5.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/comparacao/cstr-pfr-batelada", {"ca0": ca0, "k": k, "tau": tau, "tempo_batelada": tempo_batelada})
            mostrar_resultado(resultado)
            if resultado:
                grafico_comparacao_reatores(k)

        elif modulo_projeto == "Rendimento":
            st.header("Projeto de Reatores — Rendimento")
            produto_obtido = st.number_input(rotulo("produto_obtido"), value=75.0)
            produto_teorico = st.number_input(rotulo("produto_teorico"), value=100.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/fogler-rendimento", {"produto_obtido": produto_obtido, "produto_teorico": produto_teorico})
            mostrar_resultado(resultado)
            if resultado:
                grafico_rendimento()

        elif modulo_projeto == "Seletividade":
            st.header("Projeto de Reatores — Seletividade")
            produto_desejado = st.number_input(rotulo("produto_desejado"), value=80.0)
            produto_indesejado = st.number_input(rotulo("produto_indesejado"), value=20.0)
            if st.button("Resolver", type="primary"):
                resultado = get("/fogler-seletividade", {"produto_desejado": produto_desejado, "produto_indesejado": produto_indesejado})
            mostrar_resultado(resultado)
            if resultado:
                grafico_seletividade()


    # ==================================================
    # CINÉTICA DAS REAÇÕES QUÍMICAS
    # ==================================================
    elif categoria == "Cinética das Reações Químicas":

        if modulo_cinetica_quimica == "Taxa de reação (-rA)":
            st.header("Cinética das Reações Químicas — Taxa de reação (-rA)")

            st.markdown("""
            Neste módulo, o cálculo considera apenas espécies com **coeficiente estequiométrico maior que zero**.
            Se o coeficiente de B for zero, B não participa da reação e sua concentração pode ser considerada igual a zero.
            """)

            tipo_taxa = tipo_taxa_reacao or "Reação elementar"

            col1, col2, col3 = st.columns(3)
            with col1:
                coef_a = st.number_input(rotulo("coef_a"), min_value=0.0, value=1.0)
            with col2:
                coef_b = st.number_input(rotulo("coef_b"), min_value=0.0, value=0.0)
            with col3:
                coef_i = st.number_input(rotulo("coef_i"), min_value=0.0, value=0.0)

            if tipo_taxa == "Reação elementar":
                ordem_a = coef_a if componente_ativo(coef_a) else 0.0
                ordem_b = coef_b if componente_ativo(coef_b) else 0.0
            else:
                col_ord1, col_ord2 = st.columns(2)
                with col_ord1:
                    ordem_a = st.number_input(rotulo("ordem_a"), min_value=0.0, value=1.0 if componente_ativo(coef_a) else 0.0)
                with col_ord2:
                    ordem_b = st.number_input(rotulo("ordem_b"), min_value=0.0, value=1.0 if componente_ativo(coef_b) else 0.0)
                if not componente_ativo(coef_a):
                    ordem_a = 0.0
                if not componente_ativo(coef_b):
                    ordem_b = 0.0

            reacao_txt = montar_reacao_irreversivel(coef_a, coef_b, coef_i)
            lei_txt = montar_lei_velocidade_irreversivel(ordem_a, ordem_b, coef_a, coef_b)
            st.latex(reacao_txt.replace("→", r"\rightarrow"))
            st.latex(lei_txt)

            ordem_global = ordem_a + ordem_b
            st.info(f"Ordem global calculada: {formatar_numero(ordem_global)} | Unidade de k: {unidade_k_por_ordem(ordem_global)}")

            colc1, colc2, colk = st.columns(3)
            with colc1:
                ca = st.number_input(rotulo("ca"), min_value=0.0, value=2.0 if componente_ativo(coef_a) else 0.0)
            with colc2:
                cb = st.number_input(rotulo("cb"), min_value=0.0, value=2.0 if componente_ativo(coef_b) else 0.0)
            with colk:
                k = st.number_input(rotulo_k(ordem_global), value=0.3)

            if not componente_ativo(coef_a):
                ca = 0.0
            if not componente_ativo(coef_b):
                cb = 0.0

            if st.button("Resolver", type="primary"):
                ra_negativo = calcular_taxa_multicomponente(k, ca, cb, coef_a, coef_b, ordem_a, ordem_b)
                resultado = {
                    "modelo": tipo_taxa,
                    "equacao": lei_txt,
                    "coef_a": coef_a,
                    "coef_b": coef_b,
                    "coef_i": coef_i,
                    "ca": ca,
                    "cb": cb,
                    "ordem_a": ordem_a,
                    "ordem_b": ordem_b,
                    "ordem_global": ordem_global,
                    "k": k,
                    "ra_negativo": ra_negativo
                }
                st.markdown(f"**Unidade calculada de k:** `{unidade_k_por_ordem(ordem_global)}`")

            mostrar_resultado(resultado)
            if resultado:
                grafico_taxa_multicomponente(k, ca, cb, coef_a, coef_b, ordem_a, ordem_b)

        elif modulo_cinetica_quimica == "Reações irreversíveis":
            modelo_irrev = modelo_irreversivel or "A → Produtos"
            st.header(f"Cinética das Reações Químicas — Reações irreversíveis — {modelo_irrev}")

            if modelo_irrev == "A → Produtos":
                coef_a, coef_b, coef_i = 1.0, 0.0, 0.0
                tipo_taxa = "Reação elementar"
            elif modelo_irrev == "2A → Produtos":
                coef_a, coef_b, coef_i = 2.0, 0.0, 0.0
                tipo_taxa = "Reação elementar"
            elif modelo_irrev == "A + B → Produtos":
                coef_a, coef_b, coef_i = 1.0, 1.0, 0.0
                tipo_taxa = "Reação elementar"
            elif modelo_irrev == "A + 2B → Produtos":
                coef_a, coef_b, coef_i = 1.0, 2.0, 0.0
                tipo_taxa = "Reação elementar"
            elif modelo_irrev == "2A + B → Produtos":
                coef_a, coef_b, coef_i = 2.0, 1.0, 0.0
                tipo_taxa = "Reação elementar"
            elif modelo_irrev == "Reação geral (aA + bB → produtos)":
                tipo_taxa = "Reação elementar"
                col1, col2, col3 = st.columns(3)
                with col1:
                    coef_a = st.number_input(rotulo("coef_a"), min_value=0.0, value=1.0)
                with col2:
                    coef_b = st.number_input(rotulo("coef_b"), min_value=0.0, value=1.0)
                with col3:
                    coef_i = st.number_input(rotulo("coef_i"), min_value=0.0, value=0.0)
            else:
                tipo_taxa = "Reação não elementar"
                col1, col2, col3 = st.columns(3)
                with col1:
                    coef_a = st.number_input(rotulo("coef_a"), min_value=0.0, value=1.0)
                with col2:
                    coef_b = st.number_input(rotulo("coef_b"), min_value=0.0, value=1.0)
                with col3:
                    coef_i = st.number_input(rotulo("coef_i"), min_value=0.0, value=0.0)

            if tipo_taxa == "Reação elementar":
                ordem_a = coef_a if componente_ativo(coef_a) else 0.0
                ordem_b = coef_b if componente_ativo(coef_b) else 0.0
                st.caption("Modelo elementar: as ordens parciais são iguais aos coeficientes estequiométricos.")
            else:
                st.caption("Modelo não elementar: as ordens parciais são experimentais e podem ser diferentes dos coeficientes estequiométricos.")
                coloa, colob = st.columns(2)
                with coloa:
                    ordem_a = st.number_input(rotulo("ordem_a"), min_value=0.0, value=1.0 if componente_ativo(coef_a) else 0.0)
                with colob:
                    ordem_b = st.number_input(rotulo("ordem_b"), min_value=0.0, value=1.0 if componente_ativo(coef_b) else 0.0)
                if not componente_ativo(coef_a):
                    ordem_a = 0.0
                if not componente_ativo(coef_b):
                    ordem_b = 0.0

            reacao_txt = montar_reacao_irreversivel(coef_a, coef_b, coef_i)
            lei_txt = montar_lei_velocidade_irreversivel(ordem_a, ordem_b, coef_a, coef_b)

            st.latex(reacao_txt.replace("→", r"\rightarrow"))
            st.latex(lei_txt)

            ordem_global = ordem_a + ordem_b
            st.info(f"Ordem global: {formatar_numero(ordem_global)} | Unidade de k: {unidade_k_por_ordem(ordem_global)}")

            colc1, colc2, colk = st.columns(3)
            with colc1:
                ca = st.number_input(rotulo("ca"), min_value=0.0, value=2.0 if componente_ativo(coef_a) else 0.0)
            with colc2:
                cb = st.number_input(rotulo("cb"), min_value=0.0, value=2.0 if componente_ativo(coef_b) else 0.0)
            with colk:
                k = st.number_input(rotulo_k(ordem_global), value=0.3)

            if not componente_ativo(coef_a):
                ca = 0.0
            if not componente_ativo(coef_b):
                cb = 0.0

            if st.button("Resolver", type="primary"):
                ra_negativo = calcular_taxa_multicomponente(k, ca, cb, coef_a, coef_b, ordem_a, ordem_b)
                resultado = {
                    "modelo": modelo_irrev,
                    "tipo": tipo_taxa,
                    "equacao": lei_txt,
                    "coef_a": coef_a,
                    "coef_b": coef_b,
                    "coef_i": coef_i,
                    "ca": ca,
                    "cb": cb,
                    "ordem_a": ordem_a,
                    "ordem_b": ordem_b,
                    "ordem_global": ordem_global,
                    "k": k,
                    "ra_negativo": ra_negativo
                }
                st.markdown(f"**Unidade calculada de k:** `{unidade_k_por_ordem(ordem_global)}`")

            mostrar_resultado(resultado)
            if resultado:
                grafico_taxa_multicomponente(k, ca, cb, coef_a, coef_b, ordem_a, ordem_b)

        elif modulo_cinetica_quimica == "Reações reversíveis":
            modelo_rev = modelo_reversivel or "A ⇌ B"
            st.header(f"Cinética das Reações Químicas — Reações reversíveis — {modelo_rev}")

            if modelo_rev == "A ⇌ B":
                coef_a, coef_b, coef_c, coef_d = 1.0, 0.0, 1.0, 0.0
                ordem_a, ordem_b, ordem_c, ordem_d = 1.0, 0.0, 1.0, 0.0
            elif modelo_rev == "A + B ⇌ C + D":
                coef_a, coef_b, coef_c, coef_d = 1.0, 1.0, 1.0, 1.0
                ordem_a, ordem_b, ordem_c, ordem_d = 1.0, 1.0, 1.0, 1.0
            else:
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    coef_a = st.number_input(rotulo("coef_a"), min_value=0.0, value=1.0)
                with col2:
                    coef_b = st.number_input(rotulo("coef_b"), min_value=0.0, value=1.0)
                with col3:
                    coef_c = st.number_input(rotulo("coef_c"), min_value=0.0, value=1.0)
                with col4:
                    coef_d = st.number_input(rotulo("coef_d"), min_value=0.0, value=1.0)

                st.caption("Para a reação geral reversível, as ordens podem ser ajustadas como elementares ou não elementares.")
                usar_ordem_nao_elementar = st.checkbox("Usar ordens não elementares", value=False)

                if usar_ordem_nao_elementar:
                    coloa, colob, coloc, colod = st.columns(4)
                    with coloa:
                        ordem_a = st.number_input(rotulo("ordem_a"), min_value=0.0, value=1.0 if componente_ativo(coef_a) else 0.0)
                    with colob:
                        ordem_b = st.number_input(rotulo("ordem_b"), min_value=0.0, value=1.0 if componente_ativo(coef_b) else 0.0)
                    with coloc:
                        ordem_c = st.number_input(rotulo("ordem_c"), min_value=0.0, value=1.0 if componente_ativo(coef_c) else 0.0)
                    with colod:
                        ordem_d = st.number_input(rotulo("ordem_d"), min_value=0.0, value=1.0 if componente_ativo(coef_d) else 0.0)
                else:
                    ordem_a = coef_a if componente_ativo(coef_a) else 0.0
                    ordem_b = coef_b if componente_ativo(coef_b) else 0.0
                    ordem_c = coef_c if componente_ativo(coef_c) else 0.0
                    ordem_d = coef_d if componente_ativo(coef_d) else 0.0

            reacao_txt = montar_reacao_reversivel(coef_a, coef_b, coef_c, coef_d)
            lei_txt = montar_lei_velocidade_reversivel(ordem_a, ordem_b, ordem_c, ordem_d, coef_a, coef_b, coef_c, coef_d)
            st.latex(reacao_txt.replace("⇌", r"\rightleftharpoons"))
            st.latex(lei_txt)

            ordem_ida = ordem_a + ordem_b
            ordem_volta = ordem_c + ordem_d

            st.info(
                f"Ordem direta: {formatar_numero(ordem_ida)} | Unidade de k₁: {unidade_k_por_ordem(ordem_ida)}  —  "
                f"Ordem inversa: {formatar_numero(ordem_volta)} | Unidade de k₂: {unidade_k_por_ordem(ordem_volta)}"
            )

            colk1, colk2 = st.columns(2)
            with colk1:
                k1 = st.number_input(f"Constante direta (k₁) [{unidade_k_por_ordem(ordem_ida)}]", value=0.4)
            with colk2:
                k2 = st.number_input(f"Constante inversa (k₂) [{unidade_k_por_ordem(ordem_volta)}]", value=0.1)

            colca, colcb, colcc, colcd = st.columns(4)
            with colca:
                ca = st.number_input(rotulo("ca"), min_value=0.0, value=2.0 if componente_ativo(coef_a) else 0.0)
            with colcb:
                cb = st.number_input(rotulo("cb"), min_value=0.0, value=2.0 if componente_ativo(coef_b) else 0.0)
            with colcc:
                cc = st.number_input(rotulo("cc"), min_value=0.0, value=0.5 if componente_ativo(coef_c) else 0.0)
            with colcd:
                cd = st.number_input(rotulo("cd"), min_value=0.0, value=0.5 if componente_ativo(coef_d) else 0.0)

            if not componente_ativo(coef_a): ca = 0.0
            if not componente_ativo(coef_b): cb = 0.0
            if not componente_ativo(coef_c): cc = 0.0
            if not componente_ativo(coef_d): cd = 0.0

            if st.button("Resolver", type="primary"):
                ra_negativo = calcular_taxa_reversivel_geral(
                    k1, k2, ca, cb, cc, cd,
                    coef_a, coef_b, coef_c, coef_d,
                    ordem_a, ordem_b, ordem_c, ordem_d
                )
                keq = k1 / k2 if k2 != 0 else np.inf
                resultado = {
                    "modelo": modelo_rev,
                    "equacao": lei_txt,
                    "coef_a": coef_a,
                    "coef_b": coef_b,
                    "coef_c": coef_c,
                    "coef_d": coef_d,
                    "ca": ca,
                    "cb": cb,
                    "cc": cc,
                    "cd": cd,
                    "ordem_a": ordem_a,
                    "ordem_b": ordem_b,
                    "ordem_c": ordem_c,
                    "ordem_d": ordem_d,
                    "k1": k1,
                    "k2": k2,
                    "keq": keq,
                    "ra_negativo": ra_negativo
                }

            mostrar_resultado(resultado)
            if resultado:
                if modelo_rev == "A ⇌ B":
                    grafico_taxa_reversivel_primeira(k1, k2, ca, cc)
                else:
                    grafico_taxa_reversivel_segunda(k1, k2, ca, cb)

        elif modulo_cinetica_quimica == "Volume constante":
            st.header("Cinética das Reações Químicas — Volume constante")
            st.latex(r"C_A=C_{A0}(1-X)")
            st.latex(r"-r_A=kC_A^aC_B^b")

            col1, col2, col3 = st.columns(3)
            with col1:
                coef_a = st.number_input(rotulo("coef_a"), min_value=0.0, value=1.0)
            with col2:
                coef_b = st.number_input(rotulo("coef_b"), min_value=0.0, value=0.0)
            with col3:
                coef_i = st.number_input(rotulo("coef_i"), min_value=0.0, value=0.0)

            col2a, col2b, col2c = st.columns(3)
            with col2a:
                ca0 = st.number_input(rotulo("ca0"), value=5.0)
            with col2b:
                cb0 = st.number_input(rotulo("cb0"), value=0.0 if not componente_ativo(coef_b) else 5.0)
            with col2c:
                conversao = st.number_input(rotulo("conversao"), min_value=0.0, max_value=0.999, value=0.6)

            if not componente_ativo(coef_b):
                cb0 = 0.0

            ordem_a = coef_a if componente_ativo(coef_a) else 0.0
            ordem_b = coef_b if componente_ativo(coef_b) else 0.0
            ordem_global = ordem_a + ordem_b
            st.info(f"Ordem global elementar: {formatar_numero(ordem_global)} | Unidade de k: {unidade_k_por_ordem(ordem_global)}")

            k = st.number_input(rotulo_k(ordem_global), value=0.3)

            if st.button("Resolver", type="primary"):
                ca = ca0 * (1 - conversao) if componente_ativo(coef_a) else 0.0
                cb = cb0 - (coef_b / coef_a) * ca0 * conversao if componente_ativo(coef_a) and componente_ativo(coef_b) and coef_a != 0 else cb0
                cb = max(cb, 0.0)
                ra_negativo = calcular_taxa_multicomponente(k, ca, cb, coef_a, coef_b, ordem_a, ordem_b)
                resultado = {
                    "modelo": "Sistema de volume constante",
                    "equacao": "CA = CA0(1-X); -rA = k CA^a CB^b",
                    "coef_a": coef_a,
                    "coef_b": coef_b,
                    "coef_i": coef_i,
                    "ca0": ca0,
                    "cb0": cb0,
                    "conversao": conversao,
                    "ca": ca,
                    "cb": cb,
                    "ordem_global": ordem_global,
                    "k": k,
                    "ra_negativo": ra_negativo
                }
                st.markdown(f"**Unidade calculada de k:** `{unidade_k_por_ordem(ordem_global)}`")

            mostrar_resultado(resultado)
            if resultado:
                grafico_volume_constante(ca0, k, max(ordem_global, 0))

        elif modulo_cinetica_quimica == "Volume variável":
            st.header("Cinética das Reações Químicas — Volume variável")
            st.latex(r"C_A=\frac{C_{A0}(1-X)}{1+\varepsilon X}")
            st.latex(r"-r_A=kC_A^aC_B^b")

            col1, col2, col3 = st.columns(3)
            with col1:
                coef_a = st.number_input(rotulo("coef_a"), min_value=0.0, value=1.0)
            with col2:
                coef_b = st.number_input(rotulo("coef_b"), min_value=0.0, value=0.0)
            with col3:
                coef_i = st.number_input(rotulo("coef_i"), min_value=0.0, value=0.0)

            col2a, col2b, col2c = st.columns(3)
            with col2a:
                ca0 = st.number_input(rotulo("ca0"), value=5.0)
            with col2b:
                cb0 = st.number_input(rotulo("cb0"), value=0.0 if not componente_ativo(coef_b) else 5.0)
            with col2c:
                epsilon = st.number_input(rotulo("epsilon"), value=0.5)

            col3a, col3b = st.columns(2)
            with col3a:
                conversao = st.number_input(rotulo("conversao"), min_value=0.0, max_value=0.999, value=0.6)
            with col3b:
                ordem_global_manual = st.checkbox("Usar ordens não elementares", value=False)

            if not componente_ativo(coef_b):
                cb0 = 0.0

            if ordem_global_manual:
                coloa, colob = st.columns(2)
                with coloa:
                    ordem_a = st.number_input(rotulo("ordem_a"), min_value=0.0, value=1.0 if componente_ativo(coef_a) else 0.0)
                with colob:
                    ordem_b = st.number_input(rotulo("ordem_b"), min_value=0.0, value=1.0 if componente_ativo(coef_b) else 0.0)
                if not componente_ativo(coef_a):
                    ordem_a = 0.0
                if not componente_ativo(coef_b):
                    ordem_b = 0.0
            else:
                ordem_a = coef_a if componente_ativo(coef_a) else 0.0
                ordem_b = coef_b if componente_ativo(coef_b) else 0.0

            ordem_global = ordem_a + ordem_b
            st.info(f"Ordem global: {formatar_numero(ordem_global)} | Unidade de k: {unidade_k_por_ordem(ordem_global)}")

            k = st.number_input(rotulo_k(ordem_global), value=0.3)

            if st.button("Resolver", type="primary"):
                volume_relativo = 1 + epsilon * conversao
                ca = ca0 * (1 - conversao) / volume_relativo if componente_ativo(coef_a) else 0.0
                cb = (cb0 - (coef_b / coef_a) * ca0 * conversao) / volume_relativo if componente_ativo(coef_a) and componente_ativo(coef_b) and coef_a != 0 else cb0 / volume_relativo
                cb = max(cb, 0.0)
                ra_negativo = calcular_taxa_multicomponente(k, ca, cb, coef_a, coef_b, ordem_a, ordem_b)
                resultado = {
                    "modelo": "Sistema de volume variável",
                    "equacao": "CA = CA0(1-X)/(1+epsilon X); -rA = k CA^ordem_A CB^ordem_B",
                    "coef_a": coef_a,
                    "coef_b": coef_b,
                    "coef_i": coef_i,
                    "ca0": ca0,
                    "cb0": cb0,
                    "conversao": conversao,
                    "epsilon": epsilon,
                    "volume_relativo": volume_relativo,
                    "ca": ca,
                    "cb": cb,
                    "ordem_a": ordem_a,
                    "ordem_b": ordem_b,
                    "ordem_global": ordem_global,
                    "k": k,
                    "ra_negativo": ra_negativo
                }
                st.markdown(f"**Unidade calculada de k:** `{unidade_k_por_ordem(ordem_global)}`")

            mostrar_resultado(resultado)
            if resultado:
                grafico_volume_variavel(ca0, epsilon, k, max(ordem_global, 0))

        elif modulo_cinetica_quimica == "Velocidade específica (μ)":
            st.header("Cinética das Reações Químicas — Velocidade específica (μ)")
            st.latex(r"\mu=\frac{1}{X}\frac{dX}{dt}")
            col1, col2 = st.columns(2)
            with col1:
                x = st.number_input(rotulo("x"), value=5.0)
            with col2:
                dxdt = st.number_input(rotulo("dxdt"), value=1.2)

            if st.button("Resolver", type="primary"):
                velocidade_especifica = dxdt / x if x != 0 else np.nan
                resultado = {
                    "modelo": "Velocidade específica",
                    "equacao": "mu = (1/X)(dX/dt)",
                    "x": x,
                    "dxdt": dxdt,
                    "velocidade_especifica": velocidade_especifica
                }
            mostrar_resultado(resultado)

        elif modulo_cinetica_quimica == "Arrhenius":
            st.header("Cinética das Reações Químicas — Arrhenius")
            st.latex(r"k=k_0e^{-E_a/(RT)}")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                k0 = st.number_input(rotulo("k0"), value=1.0e7, format="%.3e")
            with col2:
                ea = st.number_input(rotulo("ea"), value=50000.0)
            with col3:
                r_gases = st.number_input(rotulo("r_gases"), value=8.314)
            with col4:
                temperatura_k = st.number_input(rotulo("temperatura_k"), value=350.0)

            if st.button("Resolver", type="primary"):
                k = k0 * np.exp(-ea / (r_gases * temperatura_k))
                resultado = {
                    "modelo": "Equação de Arrhenius",
                    "equacao": "k = k0 exp(-Ea/RT)",
                    "k0": k0,
                    "ea": ea,
                    "r_gases": r_gases,
                    "temperatura_k": temperatura_k,
                    "k": k
                }
            mostrar_resultado(resultado)
            if resultado:
                grafico_arrhenius(k0, ea, r_gases)

        elif modulo_cinetica_quimica == "Conversão":
            st.header("Cinética das Reações Químicas — Conversão")
            st.latex(r"X=\frac{F_{A0}-F_A}{F_{A0}}")
            col1, col2 = st.columns(2)
            with col1:
                fa0 = st.number_input(rotulo("fa0"), value=10.0)
            with col2:
                fa = st.number_input(rotulo("fa"), value=3.0)

            if st.button("Resolver", type="primary"):
                conversao = (fa0 - fa) / fa0 if fa0 != 0 else np.nan
                resultado = {
                    "modelo": "Conversão",
                    "equacao": "X = (FA0 - FA)/FA0",
                    "fa0": fa0,
                    "fa": fa,
                    "conversao": conversao
                }
            mostrar_resultado(resultado)
            if resultado:
                grafico_conversao_fa(fa0)

        elif modulo_cinetica_quimica == "Tempo espacial (τ)":
            st.header("Cinética das Reações Químicas — Tempo espacial (τ)")
            st.latex(r"\tau=\frac{V}{v_0}")
            col1, col2 = st.columns(2)
            with col1:
                volume_reator = st.number_input(rotulo("volume_reator"), value=100.0)
            with col2:
                v0 = st.number_input(rotulo("v0"), value=20.0)

            if st.button("Resolver", type="primary"):
                tempo_espacial = volume_reator / v0 if v0 != 0 else np.nan
                resultado = {
                    "modelo": "Tempo espacial",
                    "equacao": "tau = V/v0",
                    "volume_reator": volume_reator,
                    "v0": v0,
                    "tempo_espacial": tempo_espacial
                }
            mostrar_resultado(resultado)

# ======================================================
# RODAPÉ
# ======================================================

st.markdown(f"""
<div class="footer">
ReactorOS • Desenvolvida por ReactorSoft • {datetime.now().year}<br>
Sistema acadêmico para resolução, análise e visualização de problemas de Engenharia Química.
</div>
""", unsafe_allow_html=True)
