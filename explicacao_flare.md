# Energia irradiada em raios X pelo flare X2.8 de 13/05/2013

**Dados:** satélite GOES-15, arquivo `dados/go1520130513.fits`
**Código:** `analise_goes.py` (gera o gráfico e as tabelas em `resultados/`)

**Resposta:** o flare irradiou cerca de **1,16 × 10³⁰ erg (1,16 × 10²³ J)** em raios X na faixa de 1–8 Å.

![Flare X2.8 visto pelo GOES-15](resultados/goes_flare_x28.png)

---

## 1. Entendendo o gráfico

### O que o GOES mede?

O GOES é um satélite que fica parado sobre a Terra, olhando para o Sol o tempo todo. Ele tem um sensor de **raios X**, uma luz invisível e muito energética.

A cada 2 segundos, ele mede **quanta energia de raios X chega em 1 metro quadrado, por segundo**. Isso se chama **fluxo**. A unidade é W/m² (watt por metro quadrado), e 1 watt = 1 joule por segundo.

### Curva azul e curva laranja

O sensor separa os raios X em duas faixas, como dois filtros:

- **Azul (1–8 Å):** raios X "menos fortes". É a faixa usada para classificar flares e a **única que usamos no cálculo**.
- **Laranja (0,5–4 Å):** raios X "mais fortes". Aparece só para comparação.

Å (angstrom) é uma unidade de tamanho de onda. Quanto menor a onda, mais energética é a luz.

### Por que as curvas sobem num flare?

Um flare é uma explosão na superfície do Sol. Ela aquece o gás local a milhões de graus, e um gás tão quente brilha em raios X. Por isso o fluxo sobe rápido.

Depois, o gás esfria aos poucos e o fluxo desce devagar. No gráfico, isso aparece como **subida rápida e descida lenta**.

### O que significa X2.8?

Os flares são classificados por letras, conforme o valor máximo da curva azul: **A, B, C, M e X**. Cada letra é 10 vezes mais forte que a anterior, e X é a mais forte.

O número diz quantas vezes o pico passou do mínimo da classe X (0,0001 W/m²). Nosso pico foi 0,000288 W/m², ou seja, 2,8 vezes esse mínimo. Por isso é **X2.8**.

### Escala do eixo vertical

Cada marca do eixo vale 10 vezes a anterior (escala logarítmica). Isso permite ver no mesmo gráfico valores muito pequenos e muito grandes.

### O que é o fluxo de fundo?

Mesmo sem flare, o Sol já emite um pouco de raios X. Esse é o **fundo**, a linha tracejada no gráfico: **2,26 × 10⁻⁶ W/m²**. Calculamos esse valor a partir das medições dos 10 minutos antes do início do flare.

Queremos só a energia que **o flare acrescentou**, então descontamos esse nível. É como pesar uma fruta numa balança: você desconta o peso do prato.

---

## 2. Os horários do flare

Estes horários são **estimativas** baseadas no formato da curva, e não verdades absolutas.

| | Hora (UTC) | Por quê |
|---|---|---|
| Início | **15:48** | A curva azul começa a subir rápido e sem parar |
| Pico | **16:05** | Maior valor da curva azul |
| Fim | **19:45** | A curva volta ao nível em que estava no início |
| Duração | **237 min (~4 h)** | Fim menos início |

**UTC** é o horário de referência mundial. Brasília está 3 horas atrás.

- **Início:** usamos uma regra da **NOAA**, a agência dos EUA que monitora o Sol e publica a lista oficial de flares. A regra diz: o flare começa quando a curva sobe **4 minutos seguidos** e termina pelo menos **40 % mais alta**. Isso evita confundir o flare com pequenas oscilações, como o degrauzinho das 15:38.
- **Pico:** o catálogo diz 16:07, mas nos dados o máximo está às 16:05. Usamos o catálogo só para saber onde procurar.
- **Fim:** a curva desce muito devagar, então não existe um instante exato em que o flare acaba. Escolhemos o momento em que ela volta ao nível do início. Outra escolha mudaria um pouco o resultado.

---

## 3. O cálculo da energia em três etapas

| Etapa | O que fizemos | Resultado |
|---|---|---|
| 1 | Somamos a energia recebida ao longo do flare | **0,411 J/m²** |
| 2 | Convertemos para ergs | **4,11 × 10⁶ erg/m²** |
| 3 | Consideramos a distância Sol–Terra | **1,16 × 10³⁰ erg** |
| Final | Energia estimada do flare | **1,16 × 10³⁰ erg = 1,16 × 10²³ J** |

### Etapa 1 — Energia recebida por metro quadrado: 0,411 J/m²

- **O que é:** a energia de raios X que o flare depositou em cada metro quadrado, aqui perto da Terra, durante as 4 horas.
- **Como chegamos:** o GOES diz quanta energia chega **por segundo**. Pegamos cada intervalo de 2 segundos, descontamos o fundo e multiplicamos o fluxo pelo tempo (2 s). Isso dá a energia daquele pedacinho. Depois somamos os 6.942 pedacinhos. Essa soma é o que se chama de **integrar o fluxo**.
- **Analogia:** é como uma conta de luz. O medidor sabe quanta potência a casa usa a cada instante, e a conta soma tudo ao longo do mês.
- **No gráfico:** essa soma é a **área azul clara**, entre a curva azul e a linha do fundo.

Em fórmula:

$$\text{energia por m}^2 = \int \left[F(t) - F_{\text{fundo}}\right] dt$$

### Etapa 2 — Conversão para ergs: 4,11 × 10⁶ erg/m²

- **O que é:** o mesmo valor da Etapa 1, em outra unidade.
- **Como chegamos:** joule e erg medem energia, assim como metro e centímetro medem distância. **1 joule = 10 milhões de ergs**, então:

  0,411 J/m² × 10.000.000 = **4,11 × 10⁶ erg/m²**

- **Por que:** em astronomia, energias costumam ser dadas em erg.

### Etapa 3 — Energia emitida pelo Sol: 1,16 × 10³⁰ erg

- **Por que precisamos dela:** o GOES capturou só o que caiu em 1 m². O Sol, porém, emitiu para todos os lados.
- **Analogia:** uma lâmpada no meio de uma sala ilumina todas as paredes, não só o ponto onde você está. A luz do flare também se espalhou como uma bolha crescendo. Quando chegou à Terra, essa bolha tinha raio igual à distância Sol–Terra: d = 1,496 × 10¹¹ m (150 milhões de km).
- **Como chegamos:** a área de uma esfera é 4πd²:

  4 × π × (1,496 × 10¹¹ m)² = **2,81 × 10²³ m²**

  Supondo que cada m² da bolha recebeu a mesma energia, multiplicamos:

  4,11 × 10⁶ erg/m² × 2,81 × 10²³ m² = **1,16 × 10³⁰ erg**

- **Hipótese importante:** essa multiplicação supõe que o flare brilhou igual em todas as direções (emissão isotrópica).

### Resultado final: 1,16 × 10³⁰ erg = 1,16 × 10²³ J

- **Para ter ideia do tamanho:** é aproximadamente a eletricidade que a humanidade inteira consome em cerca de 1.000 anos (o consumo mundial é de cerca de 10²⁰ J por ano).
- **Atenção:** isso é só a energia em **raios X de 1–8 Å**. O flare também emitiu outros tipos de luz e lançou partículas e material no espaço. A energia total dele é maior.

---

## 4. Limitações

- Os horários de início e fim são escolhas baseadas na curva. Um fim diferente muda o resultado.
- O fundo foi considerado constante, mas na realidade ele varia um pouco ao longo das horas.
- Supomos que o flare emitiu igualmente em todas as direções e usamos a distância média Sol–Terra.
- Se o fundo **não** for subtraído, o resultado sobe para cerca de 1,25 × 10³⁰ erg (≈ 7 % a mais).

---

## 5. O código

O script `analise_goes.py` segue a mesma ordem desta explicação:

1. Ler o arquivo FITS.
2. Achar o pico, o início, o fundo e o fim.
3. Calcular as Etapas 1, 2 e 3.
4. Salvar o gráfico e as tabelas em `resultados/`.

Na Etapa 1, a soma dos pedacinhos está escrita por extenso no código, sem função pronta, para mostrar exatamente o que é a integral.

Para executar:

```bash
source .venv/bin/activate
python analise_goes.py
```

---

## 6. Roteiro para a apresentação (3–5 minutos)

> Eu escolhi analisar um flare solar, que é uma explosão na superfície do Sol. Esse aconteceu em 13 de maio de 2013 e foi classificado como X2.8, uma das categorias mais fortes.
>
> Usei dados do satélite GOES-15, que fica em órbita da Terra medindo os raios X que vêm do Sol. A cada 2 segundos, ele registra quanta energia de raios X chega em um metro quadrado. Os dados vêm num arquivo FITS, que é um formato muito usado em astronomia, e eu li esse arquivo com Python.
>
> *(mostrar o gráfico)* Aqui está a curva. A linha azul é a faixa de raios X usada para classificar flares. Dá para ver o padrão típico: uma subida muito rápida e uma descida lenta, que dura horas. O flare começou às 15:48, quando a curva passou a subir sem parar. O pico foi às 16:05, com um valor 2,8 vezes acima do mínimo da classe X, e é daí que vem o nome X2.8. E considerei que terminou às 19:45, quando a curva voltou ao nível do começo. Esses horários são estimativas, porque a curva desce aos poucos.
>
> A linha tracejada é o fundo: o Sol já emitia um pouco de raios X antes do flare. Eu desconto esse valor para contar só a energia do flare.
>
> O cálculo teve três etapas. Primeiro, como o satélite mede energia por segundo, eu somei a energia de cada intervalo de 2 segundos durante as 4 horas, que é a área azul do gráfico. Deu 0,41 joule por metro quadrado. Segundo, converti para ergs, a unidade mais usada em astronomia: 1 joule são 10 milhões de ergs, então ficou 4,1 milhões de ergs por metro quadrado. Terceiro, como o Sol emitiu para todos os lados, igual a uma lâmpada no meio de uma sala, essa energia se espalhou por uma esfera do tamanho da distância Sol–Terra. Multiplicando pela área dessa esfera, chego à energia total.
>
> O resultado foi cerca de 1,2 × 10³⁰ ergs, ou 1,2 × 10²³ joules. Isso é mais ou menos a eletricidade que a humanidade inteira usa em mil anos, emitida em 4 horas. E isso é só a parte em raios X: a energia total do flare foi ainda maior.
