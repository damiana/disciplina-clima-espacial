"""
Energia irradiada em raios X pelo flare X2.8 de 13/05/2013 (dados do GOES-15).

O que o programa faz:
    1. Lê o arquivo FITS com as medições do satélite.
    2. Encontra o flare na curva: início, pico e fim.
    3. Calcula a energia em três etapas:
         Etapa 1 — energia recebida por metro quadrado (J/m²)
         Etapa 2 — conversão de joules para ergs (erg/m²)
         Etapa 3 — energia emitida pelo Sol, espalhada pelo espaço (erg e J)
    4. Salva um gráfico e uma tabela na pasta resultados/.

Como executar (com o ambiente virtual ativado):
    python analise_goes.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # só salva o PNG, sem abrir janela
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from astropy.io import fits

PASTA = Path(__file__).parent
ARQUIVO_FITS = PASTA / "dados" / "go1520130513.fits"
PASTA_RESULTADOS = PASTA / "resultados"
PASTA_RESULTADOS.mkdir(exist_ok=True)

DISTANCIA_SOL_TERRA = 1.496e11   # 1 UA (unidade astronômica), em metros
JOULE_PARA_ERG = 1e7             # 1 joule = 10 milhões de ergs

# ---------------------------------------------------------------------------
# 1. LER O ARQUIVO FITS
# ---------------------------------------------------------------------------
# O FITS guarda, para o dia 13/05/2013 inteiro, uma medição a cada ~2 segundos:
#   TIME -> segundos desde 00:00 UTC do dia
#   FLUX -> energia que chega por segundo em 1 m² (W/m²), em duas faixas:
#           coluna 0 = 1–8 Å (azul)   e   coluna 1 = 0,5–4 Å (laranja)
# (a extensão EDGES do arquivo confirma qual coluna é cada faixa)
with fits.open(ARQUIVO_FITS) as arquivo:
    faixas = arquivo["EDGES"].data["EDGES"][0]
    segundos = arquivo["FLUXES"].data["TIME"][0].astype(float)
    fluxos = arquivo["FLUXES"].data["FLUX"][0].astype(float)

dados = pd.DataFrame({
    "segundos": segundos,
    "fluxo_azul": fluxos[:, 0],      # 1–8 Å: usado em todos os cálculos
    "fluxo_laranja": fluxos[:, 1],   # 0,5–4 Å: só aparece no gráfico
})
dados["hora"] = pd.Timestamp("2013-05-13") + pd.to_timedelta(dados["segundos"], unit="s")
dados = dados.set_index("hora")

# O cabeçalho diz que -99999 significa "sem medição". Removemos valores assim.
dados = dados[dados["fluxo_azul"] > 0]

print("ARQUIVO LIDO")
print(f"  Curva azul    = faixa {faixas[0][0]:g}–{faixas[0][1]:g} Å (usada no cálculo)")
print(f"  Curva laranja = faixa {faixas[1][0]:g}–{faixas[1][1]:g} Å")
print(f"  {len(dados)} medições, uma a cada ~2 segundos")

# ---------------------------------------------------------------------------
# 2. ENCONTRAR O FLARE: PICO, INÍCIO, FUNDO E FIM
# ---------------------------------------------------------------------------
# Para decidir os horários usamos médias de 1 minuto (a curva fica mais lisa).
# Para o cálculo da energia usamos as medições originais de 2 em 2 segundos.
azul_1min = dados["fluxo_azul"].resample("1min").mean()

# PICO: o maior valor perto do horário do catálogo (16:07), procurando
# 1 hora antes e 1 hora depois. O catálogo serve só para saber onde olhar.
perto = dados.loc["2013-05-13 15:07":"2013-05-13 17:07", "fluxo_azul"]
hora_pico = perto.idxmax()
fluxo_pico = perto.max()

# INÍCIO: regra da NOAA (agência dos EUA que publica a lista oficial de flares):
# o flare começa no primeiro minuto de uma subida que dura 4 minutos seguidos
# e termina pelo menos 40% acima de onde começou.
antes_do_pico = azul_1min[hora_pico - pd.Timedelta("1h"):hora_pico]
for i in range(len(antes_do_pico) - 3):
    quatro_minutos = antes_do_pico.iloc[i:i + 4].values
    subiu_sempre = all(np.diff(quatro_minutos) > 0)
    subiu_40_por_cento = quatro_minutos[-1] >= 1.4 * quatro_minutos[0]
    if subiu_sempre and subiu_40_por_cento:
        hora_inicio = antes_do_pico.index[i]
        break
fluxo_inicio = azul_1min[hora_inicio]

# CLASSE: flares X têm pico acima de 1e-4 W/m². O número depois do X diz
# quantas vezes o pico é maior que 1e-4 (com uma casa decimal, sem arredondar).
classe = f"X{np.floor(fluxo_pico / 1e-4 * 10) / 10:.1f}"

# FUNDO: o brilho em raios X que o Sol já tinha antes do flare. Usamos a
# mediana (o valor do meio) das medições dos 10 minutos anteriores ao início.
dez_min_antes = dados.loc[hora_inicio - pd.Timedelta("10min"):hora_inicio - pd.Timedelta("1s"), "fluxo_azul"]
fluxo_fundo = dez_min_antes.median()

# FIM: o primeiro minuto, depois do pico, em que o fluxo volta ao valor que
# tinha no início do flare.
depois_do_pico = azul_1min[hora_pico:]
hora_fim = depois_do_pico[depois_do_pico <= fluxo_inicio].index[0]

duracao_s = (hora_fim - hora_inicio).total_seconds()

print("\nHORÁRIOS ENCONTRADOS NOS DADOS (estimativas, em UTC)")
print(f"  Início: {hora_inicio:%H:%M}  (começa a subida rápida)")
print(f"  Pico:   {hora_pico:%H:%M:%S}  (maior valor: {fluxo_pico:.2e} W/m² -> classe {classe})")
print(f"  Fim:    {hora_fim:%H:%M}  (fluxo volta ao nível do início)")
print(f"  Duração: {duracao_s / 60:.0f} minutos")
print(f"  Fluxo de fundo: {fluxo_fundo:.2e} W/m²  (nível do Sol antes do flare)")

# ---------------------------------------------------------------------------
# ETAPA 1 — ENERGIA RECEBIDA POR METRO QUADRADO
# ---------------------------------------------------------------------------
# O fluxo diz quantos joules chegam em 1 m² A CADA SEGUNDO.
# Para saber o total do flare:
#   a) tiramos o fundo de cada medição (fica só o que o flare acrescentou);
#   b) multiplicamos cada valor pelo tempo até a medição seguinte (~2 s),
#      o que dá a energia recebida naquele pedacinho de tempo;
#   c) somamos todos os pedacinhos. Essa soma é a "integral" do fluxo.
# Detalhe: em cada pedacinho usamos a média entre as duas medições vizinhas
# (regra do trapézio), que é mais precisa do que usar só uma delas.
flare = dados.loc[hora_inicio:hora_fim]
fluxo_do_flare = flare["fluxo_azul"].values - fluxo_fundo     # W/m² = J/s por m²
tempo = flare["segundos"].values                              # s

media_entre_vizinhas = (fluxo_do_flare[:-1] + fluxo_do_flare[1:]) / 2   # J/s por m²
tempo_entre_vizinhas = np.diff(tempo)                                     # s
pedacinhos = media_entre_vizinhas * tempo_entre_vizinhas                  # J/m²
energia_por_m2_J = pedacinhos.sum()                                       # J/m²

print("\nETAPA 1 — Energia recebida por metro quadrado")
print(f"  {len(pedacinhos)} pedacinhos de ~2 s, entre {hora_inicio:%H:%M} e {hora_fim:%H:%M}")
print(f"  Exemplo de um pedacinho no pico: "
      f"{media_entre_vizinhas[np.argmax(media_entre_vizinhas)]:.2e} J/s × "
      f"{tempo_entre_vizinhas[np.argmax(media_entre_vizinhas)]:.2f} s = "
      f"{pedacinhos.max():.2e} J/m²")
print(f"  Soma de todos = {energia_por_m2_J:.3f} J/m²")

# ---------------------------------------------------------------------------
# ETAPA 2 — CONVERTER DE JOULES PARA ERGS
# ---------------------------------------------------------------------------
# Joule e erg medem a mesma coisa (energia). Astrônomos costumam usar erg.
energia_por_m2_erg = energia_por_m2_J * JOULE_PARA_ERG

print("\nETAPA 2 — Conversão para ergs")
print(f"  {energia_por_m2_J:.3f} J/m² × 10.000.000 = {energia_por_m2_erg:.3e} erg/m²")

# ---------------------------------------------------------------------------
# ETAPA 3 — ENERGIA EMITIDA PELO SOL
# ---------------------------------------------------------------------------
# O GOES recebeu a energia só em 1 m². Mas o Sol emitiu em todas as direções,
# e essa energia se espalhou por uma "bolha" (esfera) com raio igual à
# distância Sol–Terra. Supondo que todo m² dessa bolha recebeu a mesma
# quantidade, a energia total = energia por m² × área da bolha (4πd²).
area_da_esfera = 4 * np.pi * DISTANCIA_SOL_TERRA**2      # m²
energia_total_erg = energia_por_m2_erg * area_da_esfera  # erg
energia_total_J = energia_por_m2_J * area_da_esfera      # J

print("\nETAPA 3 — Energia emitida pelo Sol")
print(f"  Área da esfera = 4 × π × ({DISTANCIA_SOL_TERRA:.3e} m)² = {area_da_esfera:.3e} m²")
print(f"  {energia_por_m2_erg:.3e} erg/m² × {area_da_esfera:.3e} m² = {energia_total_erg:.2e} erg")

print("\nRESULTADO FINAL")
print(f"  Energia irradiada em raios X (faixa 1–8 Å): "
      f"{energia_total_erg:.2e} erg = {energia_total_J:.2e} J")
print("  (é só a parte em raios X de 1–8 Å, não a energia total do flare)")

# ---------------------------------------------------------------------------
# 4. SALVAR TABELA E GRÁFICO
# ---------------------------------------------------------------------------
tabela = pd.DataFrame({
    "etapa": ["1", "2", "3", "Final"],
    "o_que_fizemos": [
        "Somamos a energia recebida ao longo do flare (já sem o fundo)",
        "Convertemos para ergs",
        "Consideramos a distância Sol-Terra",
        "Energia estimada do flare (raios X, 1-8 A)",
    ],
    "resultado": [
        f"{energia_por_m2_J:.3f} J/m2",
        f"{energia_por_m2_erg:.3e} erg/m2",
        f"{energia_total_erg:.3e} erg",
        f"{energia_total_erg:.2e} erg = {energia_total_J:.2e} J",
    ],
})
tabela.to_csv(PASTA_RESULTADOS / "resultado_energia.csv", index=False)

# Medições usadas no cálculo, para quem quiser conferir numa planilha
pd.DataFrame({
    "hora_utc": flare.index.strftime("%H:%M:%S"),
    "fluxo_medido_W_m2": flare["fluxo_azul"].values,
    "fluxo_sem_fundo_W_m2": fluxo_do_flare,
}).to_csv(PASTA_RESULTADOS / "dados_flare.csv", index=False, float_format="%.4e")

# Gráfico: de 45 min antes do início até 45 min depois do fim
janela = dados.loc[hora_inicio - pd.Timedelta("45min"):hora_fim + pd.Timedelta("45min")]
fig, ax = plt.subplots(figsize=(12, 6))
ax.fill_between(flare.index, fluxo_fundo, flare["fluxo_azul"], color="#2a78d6", alpha=0.15, lw=0,
                label="Energia somada na Etapa 1 (acima do fundo)")
ax.plot(janela.index, janela["fluxo_azul"], color="#2a78d6", lw=2, label="Raios X 1–8 Å (azul)")
ax.plot(janela.index, janela["fluxo_laranja"], color="#eb6834", lw=2, label="Raios X 0,5–4 Å (laranja)")
ax.axhline(fluxo_fundo, color="#52514e", lw=1.2, ls="--", label=f"Fundo = {fluxo_fundo:.1e} W/m²")
for hora, nome, lado in [(hora_inicio, "Início", "right"), (hora_pico, "Pico", "left"), (hora_fim, "Fim", "left")]:
    ax.axvline(hora, color="#0b0b0b", lw=1, ls="-" if nome == "Pico" else "--")
    ax.text(hora, 7e-4, f" {nome} {hora:%H:%M} ", fontsize=11, va="top", ha=lado)
ax.annotate(classe, (hora_pico, fluxo_pico), xytext=(10, 2),
            textcoords="offset points", fontsize=11)
ax.set_yscale("log")   # escala log: cada marca do eixo vale 10× a anterior
ax.set_ylim(1e-8, 1e-3)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
ax.set_xlabel("Hora (UTC) — 13/05/2013")
ax.set_ylabel("Fluxo de raios X (W/m²)")
ax.set_title("Flare X2.8 visto pelo GOES-15", loc="left")
ax.grid(color="#e4e3df")
ax.spines[["top", "right"]].set_visible(False)
ax.legend(loc="lower center", frameon=False)
fig.tight_layout()
fig.savefig(PASTA_RESULTADOS / "goes_flare_x28.png", dpi=150)

print("\nArquivos salvos em resultados/: goes_flare_x28.png, resultado_energia.csv, dados_flare.csv")
