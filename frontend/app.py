import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Plataforma Bioquímica", page_icon="🧪", layout="wide")

st.title("🧪 Plataforma de Engenharia Bioquímica")
st.write("Resolvedor de exercícios: cinética, fermentação, reatores, esterilização, Fogler e Levenspiel.")

st.sidebar.title("Menu")

categoria = st.sidebar.selectbox(
    "Tipo de problema",
    [
        "Cinética Bioquímica",
        "Engenharia Enzimática",
        "Fermentação",
        "Esterilização",
        "Reatores Ideais",
        "Fogler - Volume CSTR",
        "Fogler - Volume PFR",
        "Fogler - Seletividade",
        "Fogler - Rendimento",
        "Levenspiel - Pontos",
        "Levenspiel - Área PFR",
        "Levenspiel - Área CSTR",
        "Comparação de Reatores"
    ]
)

st.sidebar.divider()


def get(endpoint, params):
    r = requests.get(f"{API_URL}{endpoint}", params=params)
    if r.status_code != 200:
        st.error(f"Erro no backend: {r.status_code}")
        st.text(r.text)
        return None
    return r.json()


def post(endpoint, payload):
    r = requests.post(f"{API_URL}{endpoint}", json=payload)
    if r.status_code != 200:
        st.error(f"Erro no backend: {r.status_code}")
        st.text(r.text)
        return None
    return r.json()


def mostrar(resultado):
    if resultado:
        st.divider()
        st.success("Cálculo realizado com sucesso!")
        st.json(resultado)
        nums = {k:v for k,v in resultado.items() if isinstance(v, (int, float))}
        if nums:
            st.subheader("Resultados numéricos principais")
            st.dataframe(pd.DataFrame([nums]), use_container_width=True)


def ler_lista(txt):
    return [float(x.strip().replace(",", ".")) for x in txt.split(";") if x.strip()]


resultado = None

# ======================================================
# CINÉTICA BIOQUÍMICA
# ======================================================

if categoria == "Cinética Bioquímica":
    modelo = st.sidebar.selectbox("Modelo", ["Monod", "Haldane/Andrews", "Contois", "Luedeking-Piret"])
    st.header(f"Cinética Bioquímica — {modelo}")

    if modelo == "Monod":
        mumax = st.number_input("μmáx", value=0.8)
        ks = st.number_input("Ks", value=2.0)
        s = st.number_input("S", value=10.0)
        if st.button("Resolver"):
            resultado = get("/bioquimica/monod", {"mumax": mumax, "ks": ks, "s": s})

    elif modelo == "Haldane/Andrews":
        mumax = st.number_input("μmáx", value=0.8)
        ks = st.number_input("Ks", value=2.0)
        s = st.number_input("S", value=10.0)
        ki = st.number_input("Ki", value=50.0)
        if st.button("Resolver"):
            resultado = get("/bioquimica/haldane", {"mumax": mumax, "ks": ks, "s": s, "ki": ki})

    elif modelo == "Contois":
        mumax = st.number_input("μmáx", value=0.8)
        s = st.number_input("S", value=10.0)
        x = st.number_input("X", value=5.0)
        ks = st.number_input("Ks", value=2.0)
        if st.button("Resolver"):
            resultado = get("/bioquimica/contois", {"mumax": mumax, "s": s, "x": x, "ks": ks})

    else:
        alpha = st.number_input("α", value=0.5)
        beta = st.number_input("β", value=0.1)
        mu = st.number_input("μ", value=0.6)
        x = st.number_input("X", value=10.0)
        if st.button("Resolver"):
            resultado = get("/bioquimica/luedeking-piret", {"alpha": alpha, "beta": beta, "mu": mu, "x": x})


# ======================================================
# ENGENHARIA ENZIMÁTICA
# ======================================================

elif categoria == "Engenharia Enzimática":
    modelo = st.sidebar.selectbox("Modelo", ["Michaelis-Menten", "Ajuste Lineweaver-Burk", "Ajuste Hanes-Woolf", "Ajuste Eadie-Hofstee", "Comparativo dos 3 ajustes"])
    st.header(f"Engenharia Enzimática — {modelo}")

    if modelo == "Michaelis-Menten":
        vmax = st.number_input("Vmax", value=100.0)
        km = st.number_input("Km", value=5.0)
        s = st.number_input("S", value=20.0)
        if st.button("Resolver"):
            resultado = get("/enzimatica/michaelis", {"vmax": vmax, "km": km, "s": s})

    else:
        st.write("Digite os dados experimentais separados por ponto e vírgula `;`.")
        s_texto = st.text_input("Valores de S", "1;2;4;6;8;10")
        v_texto = st.text_input("Valores de v", "0.9;1.5;2.2;2.6;2.9;3.1")

        if st.button("Ajustar modelos"):
            try:
                S = ler_lista(s_texto)
                v = ler_lista(v_texto)
                if modelo == "Ajuste Lineweaver-Burk":
                    endpoint = "/enzimatica/lineweaver-burk"
                elif modelo == "Ajuste Hanes-Woolf":
                    endpoint = "/enzimatica/hanes-woolf"
                elif modelo == "Ajuste Eadie-Hofstee":
                    endpoint = "/enzimatica/eadie-hofstee"
                else:
                    endpoint = "/enzimatica/comparativo"

                resultado = post(endpoint, {"S": S, "v": v})

                if resultado and modelo == "Comparativo dos 3 ajustes":
                    st.success("Comparativo realizado!")
                    st.subheader("Melhor modelo")
                    st.success(resultado["melhor_modelo"])
                    st.subheader("Tabela comparativa")
                    st.dataframe(pd.DataFrame(resultado["tabela_comparativa"]), use_container_width=True)
                    st.subheader("Ranking")
                    st.dataframe(pd.DataFrame(resultado["ranking"]), use_container_width=True)
                    st.subheader("Detalhes")
                    st.json(resultado["resultados_detalhados"])
                    resultado = None

            except Exception as e:
                st.error(f"Erro: {e}")


# ======================================================
# FERMENTAÇÃO
# ======================================================

elif categoria == "Fermentação":
    modelo = st.sidebar.selectbox("Modelo", ["Fermentador contínuo", "Rendimento celular", "Rendimento de produto", "Produtividade", "Washout"])
    st.header(f"Fermentação — {modelo}")

    if modelo == "Fermentador contínuo":
        mumax = st.number_input("μmáx", value=0.8)
        ks = st.number_input("Ks", value=2.0)
        s = st.number_input("S", value=10.0)
        s0 = st.number_input("S0", value=100.0)
        yxs = st.number_input("Yx/s", value=0.5)
        if st.button("Resolver"):
            resultado = get("/bioquimica/fermentador-continuo", {"mumax": mumax, "ks": ks, "s": s, "s0": s0, "yxs": yxs})

    elif modelo == "Rendimento celular":
        x0 = st.number_input("X0", value=0.0)
        x = st.number_input("X", value=30.0)
        s0 = st.number_input("S0", value=100.0)
        s = st.number_input("S", value=40.0)
        if st.button("Resolver"):
            resultado = get("/bioquimica/rendimento-celular", {"x0": x0, "x": x, "s0": s0, "s": s})

    elif modelo == "Rendimento de produto":
        p0 = st.number_input("P0", value=0.0)
        p = st.number_input("P", value=50.0)
        s0 = st.number_input("S0", value=100.0)
        s = st.number_input("S", value=40.0)
        if st.button("Resolver"):
            resultado = get("/bioquimica/rendimento-produto", {"p0": p0, "p": p, "s0": s0, "s": s})

    elif modelo == "Produtividade":
        produto_formado = st.number_input("Produto formado", value=100.0)
        volume = st.number_input("Volume", value=10.0)
        tempo = st.number_input("Tempo", value=5.0)
        if st.button("Resolver"):
            resultado = get("/bioquimica/produtividade", {"produto_formado": produto_formado, "volume": volume, "tempo": tempo})

    else:
        mumax = st.number_input("μmáx", value=0.8)
        if st.button("Resolver"):
            resultado = get("/bioquimica/washout", {"mumax": mumax})


# ======================================================
# ESTERILIZAÇÃO
# ======================================================

elif categoria == "Esterilização":
    modelo = st.sidebar.selectbox(
        "Modelo",
        [
            "Espera térmica",
            "Aquecimento com vapor direto",
            "Resfriamento com serpentina",
            "Processo descontínuo completo",
            "Arrhenius kd",
            "Verificação contínua",
            "Comparação descontínuo x contínuo"
        ]
    )
    st.header(f"Esterilização — {modelo}")

    if modelo == "Espera térmica":
        volume = st.number_input("Volume do fermentador (m³)", value=30.0)
        n0 = st.number_input("Concentração inicial N0 (esporos/m³)", value=1e12, format="%.2e")
        nf = st.number_input("N final total permitido", value=1.0)
        kd = st.number_input("kd (min⁻¹)", value=2.0)
        if st.button("Resolver"):
            resultado = get("/esterilizacao/espera-termica", {"volume_m3": volume, "n0_por_m3": n0, "n_final_total": nf, "kd_min": kd})

    elif modelo == "Aquecimento com vapor direto":
        volume = st.number_input("Volume (m³)", value=30.0)
        rho = st.number_input("Densidade (kg/m³)", value=1000.0)
        cp = st.number_input("Cp (kJ/kg.K)", value=4.18)
        ti = st.number_input("Temperatura inicial (°C)", value=25.0)
        tf = st.number_input("Temperatura final (°C)", value=121.0)
        vazao = st.number_input("Vazão de vapor (kg/h)", value=5000.0)
        latente = st.number_input("Calor latente (kJ/kg)", value=2200.0)
        if st.button("Resolver"):
            resultado = get("/esterilizacao/aquecimento-vapor-direto", {"volume_m3": volume, "densidade_kg_m3": rho, "cp_kj_kg_k": cp, "ti_c": ti, "tf_c": tf, "vazao_vapor_kg_h": vazao, "calor_latente_kj_kg": latente})

    elif modelo == "Resfriamento com serpentina":
        volume = st.number_input("Volume (m³)", value=30.0)
        rho = st.number_input("Densidade (kg/m³)", value=1000.0)
        cp = st.number_input("Cp (kJ/kg.K)", value=4.18)
        ti = st.number_input("Temperatura inicial do resfriamento (°C)", value=121.0)
        tf = st.number_input("Temperatura final desejada (°C)", value=30.0)
        tagua = st.number_input("Temperatura da água (°C)", value=20.0)
        u = st.number_input("U (kJ/h.m².K)", value=2500.0)
        area = st.number_input("Área da serpentina (m²)", value=20.0)
        if st.button("Resolver"):
            resultado = get("/esterilizacao/resfriamento-serpentina", {"volume_m3": volume, "densidade_kg_m3": rho, "cp_kj_kg_k": cp, "ti_c": ti, "tf_c": tf, "tagua_c": tagua, "u_kj_h_m2_k": u, "area_m2": area})

    elif modelo == "Processo descontínuo completo":
        st.write("Valores padrão preenchidos conforme a questão da imagem.")
        if st.button("Calcular processo descontínuo completo"):
            resultado = get("/esterilizacao/descontinua-completa", {})

    elif modelo == "Arrhenius kd":
        k0 = st.number_input("k0 (h⁻¹)", value=5.7e39, format="%.2e")
        ed = st.number_input("Ed (kJ/kmol)", value=2.83e5, format="%.2e")
        r = st.number_input("R (kJ/kmol.K)", value=8.314)
        temp = st.number_input("Temperatura (°C)", value=130.0)
        if st.button("Resolver"):
            resultado = get("/esterilizacao/arrhenius-kd", {"k0_h": k0, "ed_kj_kmol": ed, "r_kj_kmol_k": r, "temp_c": temp})

    elif modelo == "Verificação contínua":
        st.write("Valores padrão conforme a questão: 130 °C, 5 min, N0=10¹²/m³ e volume de 30 m³.")
        if st.button("Verificar processo contínuo"):
            resultado = get("/esterilizacao/continuo-verificacao", {})

    else:
        st.write("Compara tempo descontínuo e suficiência do processo contínuo.")
        if st.button("Comparar"):
            resultado = get("/esterilizacao/comparacao", {})


# ======================================================
# REATORES IDEAIS
# ======================================================

elif categoria == "Reatores Ideais":
    modelo = st.sidebar.selectbox("Modelo", ["Batelada primeira ordem", "Batelada segunda ordem", "Tempo batelada primeira ordem", "CSTR primeira ordem", "CSTR segunda ordem", "PFR primeira ordem", "PFR segunda ordem", "CSTR em série", "Reação reversível", "Balanço de energia adiabático"])
    st.header(f"Reatores Ideais — {modelo}")

    if modelo == "Batelada primeira ordem":
        ca0 = st.number_input("CA0", value=10.0)
        k = st.number_input("k", value=0.3)
        t = st.number_input("t", value=5.0)
        if st.button("Resolver"):
            resultado = get("/reatores/batelada-primeira-ordem", {"ca0": ca0, "k": k, "t": t})

    elif modelo == "Batelada segunda ordem":
        ca0 = st.number_input("CA0", value=10.0)
        k = st.number_input("k", value=0.03)
        t = st.number_input("t", value=5.0)
        if st.button("Resolver"):
            resultado = get("/reatores/batelada-segunda-ordem", {"ca0": ca0, "k": k, "t": t})

    elif modelo == "Tempo batelada primeira ordem":
        k = st.number_input("k", value=0.3)
        x = st.number_input("X", value=0.8)
        if st.button("Resolver"):
            resultado = get("/reatores/batelada-tempo-primeira-ordem", {"k": k, "x": x})

    elif modelo == "CSTR primeira ordem":
        ca0 = st.number_input("CA0", value=10.0)
        k = st.number_input("k", value=0.3)
        tau = st.number_input("τ", value=5.0)
        if st.button("Resolver"):
            resultado = get("/reatores/cstr-primeira-ordem", {"ca0": ca0, "k": k, "tau": tau})

    elif modelo == "CSTR segunda ordem":
        ca0 = st.number_input("CA0", value=10.0)
        k = st.number_input("k", value=0.03)
        tau = st.number_input("τ", value=5.0)
        if st.button("Resolver"):
            resultado = get("/reatores/cstr-segunda-ordem", {"ca0": ca0, "k": k, "tau": tau})

    elif modelo == "PFR primeira ordem":
        ca0 = st.number_input("CA0", value=10.0)
        k = st.number_input("k", value=0.3)
        tau = st.number_input("τ", value=5.0)
        if st.button("Resolver"):
            resultado = get("/reatores/pfr-primeira-ordem", {"ca0": ca0, "k": k, "tau": tau})

    elif modelo == "PFR segunda ordem":
        ca0 = st.number_input("CA0", value=10.0)
        k = st.number_input("k", value=0.03)
        tau = st.number_input("τ", value=5.0)
        if st.button("Resolver"):
            resultado = get("/reatores/pfr-segunda-ordem", {"ca0": ca0, "k": k, "tau": tau})

    elif modelo == "CSTR em série":
        ca0 = st.number_input("CA0", value=10.0)
        k = st.number_input("k", value=0.3)
        tau_total = st.number_input("τ total", value=5.0)
        n = st.number_input("Número de reatores", min_value=1, value=3, step=1)
        if st.button("Resolver"):
            resultado = get("/reatores/cstr-em-serie", {"ca0": ca0, "k": k, "tau_total": tau_total, "n": n})

    elif modelo == "Reação reversível":
        ca0 = st.number_input("CA0", value=10.0)
        cb0 = st.number_input("CB0", value=0.0)
        k1 = st.number_input("k1", value=0.4)
        k2 = st.number_input("k2", value=0.1)
        t = st.number_input("t", value=5.0)
        if st.button("Resolver"):
            resultado = get("/reatores/reacao-reversivel", {"ca0": ca0, "cb0": cb0, "k1": k1, "k2": k2, "t": t})

    else:
        t0 = st.number_input("T0", value=300.0)
        delta_h = st.number_input("ΔH", value=-50000.0)
        x = st.number_input("X", value=0.7)
        cp = st.number_input("Cp", value=1000.0)
        if st.button("Resolver"):
            resultado = get("/energia/adiabatico", {"t0": t0, "delta_h": delta_h, "x": x, "cp": cp})


# ======================================================
# FOGLER E LEVENSPIEL INDEPENDENTES
# ======================================================

elif categoria == "Fogler - Volume CSTR":
    st.header("Fogler — Volume de CSTR")
    fa0 = st.number_input("FA0", value=10.0)
    x = st.number_input("X", value=0.8)
    menos_ra = st.number_input("-rA", value=2.0)
    if st.button("Resolver"):
        resultado = get("/fogler-volume-cstr", {"fa0": fa0, "x": x, "menos_ra": menos_ra})

elif categoria == "Fogler - Volume PFR":
    st.header("Fogler — Volume de PFR")
    fa0 = st.number_input("FA0", value=10.0)
    ca0 = st.number_input("CA0", value=5.0)
    k = st.number_input("k", value=0.2)
    ordem = st.number_input("Ordem", value=1.0)
    x_final = st.number_input("X final", value=0.8)
    if st.button("Resolver"):
        resultado = get("/fogler-volume-pfr", {"fa0": fa0, "ca0": ca0, "k": k, "ordem": ordem, "x_final": x_final})

elif categoria == "Fogler - Seletividade":
    st.header("Fogler — Seletividade")
    produto_desejado = st.number_input("Produto desejado", value=80.0)
    produto_indesejado = st.number_input("Produto indesejado", value=20.0)
    if st.button("Resolver"):
        resultado = get("/fogler-seletividade", {"produto_desejado": produto_desejado, "produto_indesejado": produto_indesejado})

elif categoria == "Fogler - Rendimento":
    st.header("Fogler — Rendimento reacional")
    produto_obtido = st.number_input("Produto obtido", value=75.0)
    produto_teorico = st.number_input("Produto teórico", value=100.0)
    if st.button("Resolver"):
        resultado = get("/fogler-rendimento", {"produto_obtido": produto_obtido, "produto_teorico": produto_teorico})

elif categoria == "Levenspiel - Pontos":
    st.header("Levenspiel — Pontos do gráfico")
    fa0 = st.number_input("FA0", value=10.0)
    ca0 = st.number_input("CA0", value=5.0)
    k = st.number_input("k", value=0.2)
    x_final = st.number_input("X final", value=0.8)
    numero_pontos = st.number_input("Número de pontos", min_value=2, value=10, step=1)
    if st.button("Resolver"):
        resultado = get("/levenspiel-pontos", {"fa0": fa0, "ca0": ca0, "k": k, "x_final": x_final, "numero_pontos": numero_pontos})

elif categoria == "Levenspiel - Área PFR":
    st.header("Levenspiel — Área PFR")
    fa0 = st.number_input("FA0", value=10.0)
    ca0 = st.number_input("CA0", value=5.0)
    k = st.number_input("k", value=0.2)
    x_final = st.number_input("X final", value=0.8)
    if st.button("Resolver"):
        resultado = get("/levenspiel-area-pfr", {"fa0": fa0, "ca0": ca0, "k": k, "x_final": x_final})

elif categoria == "Levenspiel - Área CSTR":
    st.header("Levenspiel — Área CSTR")
    fa0 = st.number_input("FA0", value=10.0)
    ca0 = st.number_input("CA0", value=5.0)
    k = st.number_input("k", value=0.2)
    x_final = st.number_input("X final", value=0.8)
    if st.button("Resolver"):
        resultado = get("/levenspiel-area-cstr", {"fa0": fa0, "ca0": ca0, "k": k, "x_final": x_final})


# ======================================================
# COMPARAÇÃO
# ======================================================

elif categoria == "Comparação de Reatores":
    st.header("Comparação CSTR × PFR × Batelada")
    ca0 = st.number_input("CA0", value=10.0)
    k = st.number_input("k", value=0.3)
    tau = st.number_input("τ", value=5.0)
    tempo_batelada = st.number_input("Tempo de batelada", value=5.0)
    if st.button("Resolver"):
        resultado = get("/comparacao/cstr-pfr-batelada", {"ca0": ca0, "k": k, "tau": tau, "tempo_batelada": tempo_batelada})


mostrar(resultado)
