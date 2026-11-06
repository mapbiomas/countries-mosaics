# Entrega dos mosaicos anuais Landsat — Índia (v2)

> Relatório de entrega para a equipe que aguarda os dados.
> Fonte de verdade: coleção `projects/mapbiomas-mosaics/assets/LANDSAT/LULC/INDIA/mosaics-2`.
> Data de referência: 2026-09-22.

---

## 1. Sumário executivo

A rodada nacional de produção dos mosaicos anuais Landsat da Índia está **essencialmente concluída**:

- **10.847 de 11.320 mosaicos construídos (95,8%)** do plano.
- Os 473 restantes são: **463 gaps de arquivo** (anos sem nenhuma cena usável),
  **8 células bloqueadas por um bug de tabela física** (têm dados, falham na correção),
  e **2 exports genuinamente travados** (caso raro, específico de cena).
- O produto final cobre **283 células** (grade CIM 1:250.000) × **40 anos fenológicos**
  (abril–março, 1986–2025), a **30 m**, com **117 bandas** por imagem.

### Números-chave

| Métrica | Valor |
|---|---|
| Mosaicos construídos | **10.847 / 11.320 (95,8%)** |
| Gaps de arquivo (zero cenas) | 463 |
| Bloqueados por bug de física | 8 |
| Travados (cena-específico) | 2 |
| Espaço liberado na rodada | ~25 TB |

---

## 2. O que é o produto

Um **mosaico** é uma imagem de satélite anual de uma parte da Índia, combinando toda
cena Landsat utilizável de um ano fenológico (1º de abril a 31 de março, seguindo o
calendário agrícola — o ano 2019 significa abril/2019 a março/2020).

- **Cobertura espacial:** 283 células da grade CIM 1:250.000 (~111 × 150 km cada).
- **Resolução:** 30 m.
- **Bandas:** 117 por imagem (medianas de reflectância, família SMA, índices, sazonais,
  terreno, contagens, posição).
- **Período:** 1986–2025.
- **Versão:** v2 (substitui a v1 legada).

---

## 3. Metodologia

### 3.1 Fontes

- **Landsat Collection 2, Tier 1, Level 2** (reflectância de superfície), sensores
  L5/L7/L8/L9 conforme o ano.
- Junção *inner join* com o produto **Level 1** para as bandas de ângulo
  (SZA/SAA/VZA/VAA), que o L2 não carrega.
- Filtro de nuvem: `CLOUD_COVER < 95%` a nível de cena.
- L7 listrado (SLC-off, pós-2003) entra apenas nos trimestres em que os sensores limpos
  ficaram finos (*sensor fill*), para não injetar o padrão de listras.

### 3.2 Correções radiométricas

- **BRDF** — Roy et al. (2016), c-factor com kernel RTLSR (normalização nadir).
- **Harmonização de sensores** — TM→ETM (derivada do overlap 1999–2011 da própria Índia)
  e ETM→OLI (Roy 2016), para continuidade temporal entre instrumentos.

### 3.3 Correção topográfica

- **SCS+C** com o coeficiente **C físico** lido de tabelas 6S por sensor (com AOT e
  vapor d'água do MERRA-2 na hora da passagem), por pixel.

### 3.4 Máscara de nuvem/sombra

- **Witness mask**: bits de QA do Collection 2 combinados com uma testemunha térmica
  (histórico de céu-limpo por pixel). Regra `both` (QA + testemunha).

### 3.5 Composição

- **Mediana** por pixel, mais **percentis dry/wet** (p25/p75 ordenados por NDVI),
  **swing** (p95 − p5) e **MAD**.
- Passagens são mescladas por *pass_key* para não contar duas vezes o overlap de fileira.

### 3.6 Modelo espectral (SMA)

- Família de 24 bandas: `gv`, `npv`, `soil`, `shade`, `ndfi` (anual, dry, wet, amplitude,
  MAD). Endmembers herdados da Amazônia (não recalibrados para a Índia — registrado).

### 3.7 Bandas e tipos

- **117 bandas** (contrato v2): medianas (reflectância + SMA + índices), sazonais,
  terreno, contagens e posição.
- 32 bandas usam tipos estreitos de armazenamento (uint8/int8) para reduzir volume.

---

## 4. Resultados do processamento

### 4.1 Estado final

| Desfecho | Qtd | Participação |
|---|---|---|
| ✅ Construídos | **10.847** | 95,8% |
| ⚪ Gaps de arquivo (zero cenas) | 463 | 4,1% |
| ⛔ Bloqueados por bug de física | 8 | <0,1% |
| ⚠️ Travados (cena-específico) | 2 | <0,1% |
| **Total do plano** | **11.320** | 100% |

### 4.2 Estatísticas por ano (construídos × gap, de 283 células/ano)

| Ano | Construídos | Gap |
|---|---|---|
| 1986 | 30 | 253 |
| 1987 | 229 | 54 |
| 1988 | 220 | 63 |
| 1989 | 279 | 4 |
| 1990 | 275 | 8 |
| 1991 | 281 | 2 |
| 1992 | 281 | 2 |
| 1993 | 278 | 5 |
| 1994 | 269 | 14 |
| 1995 | 270 | 13 |
| 1996 | 274 | 9 |
| 1997 | 280 | 3 |
| 1998 | 246 | 37 |
| 1999 | 283 | 0 |
| 2000 | 282 | 1 |
| 2001–2009 | 283 | 0 |
| 2010 | 280 | 3 |
| 2011–2018 | 283 | 0 |
| 2019 | 282 | 1 |
| 2020 | 283 | 0 |
| 2021 | 282 | 1 |
| 2022–2025 | 283 | 0 |

**Leitura:** 1986 é o ano mais ralo (30/283) — arquivo só com Landsat 5, passagem única.
De 1999 em diante a cobertura é essencialmente completa (283/283), exceto 2 lacunas
pontuais em 2019 e 2021.

### 4.3 O incidente de "travamento de export"

Durante a rodada, um subconjunto de exports ficou em `RUNNING` por 6–47 horas (mediana
normal: ~41 min), chegando a parar 28 das 50 vagas de processamento e derrubando a vazão
de ~50 para ~22 mosaicos/hora.

**Causa raiz (medida, não especulada):** contenção de fila. As tarefas canceladas tinham
EECU alto (35k–450k s) — ou seja, estavam **computando**, não paradas. O auto-cancelamento
em 6h cortava trabalho ainda em andamento.

**Teste decisivo:** a célula `NG-43-X-D_2017` (250 grânulos), que havia "travado",
completou em **1,8 hora** com a fila vazia (~74 EECU/s) versus ~13–21 EECU/s sob
contenção. Mesma célula, mesmo grafo, cinco vezes mais rápida.

**Correções testadas e descartadas:** `shardSize=32` (o limite é no grafo, não no tile)
e `cloud<60/40/30` (215/196/182 grânulos ainda estouram; tabelas pré-computadas seguem a 250).

**Resolução:** relançar com a fila vazia → **69 das 71 células travadas completaram** em
~2h cada. O auto-cancelamento subiu de 6h para 48h.

### 4.4 Resíduos (não bloqueiam a entrega)

- **2 exports genuinamente travados** (`NH-44-V-A_2021`, `NI-43-Z-D_2019`): estagnam no
  meio do export (EECU congela a 44% e 73%). Provável cena específica. ~0,02% do plano.
- **8 células bloqueadas por bug de física**: têm 1–6 grânulos mas a tabela de *overpass*
  está vazia, e o passo de correção topográfica falha com `NoneType has no len()`.
  Células: `NC-43-Y-C` (1989, 2000, 2010), `NC-44-Y-C_1989`, `NG-46-Z-D_1986`,
  `NH-44-X-C_1987`, `NI-43-V-C_1986`, `NI-44-Y-D_1988`. Um guard simples destravaria as 8.
- **Aviso de qualidade**: alguns passes L5/L7 sem linha na tabela 6S são exportados sem
  correção topográfica (`... ship UNCORRECTED`), em certas células/anos.

---

## 5. Imagens dos mosaicos (amostra)

Amostra de mosaicos em cor verdadeira (RGB = medianas red/green/blue), cobrindo biomas
distintos. Os thumbnails estão embutidos em base64 no arquivo
`india/docs/run_thumbnails.json`.

| Célula-ano | Região |
|---|---|
| `NB-46-X-A_2018` | Sul |
| `NG-42-X-B_2015` | Thar |
| `NH-44-V-C_2019` | Himalaia |
| `NF-45-X-D_2018` | Nordeste |
| `NG-43-X-D_2017` | Célula densa (travada no incidente) |
| `NC-46-Y-B_2018` | Costa leste |

> Para o artefato final: ler os data-URIs de `run_thumbnails.json` e exibi-los em grade.

---

## 6. Próximos passos (follow-ups)

1. **2 travadas reais** — investigar a cena específica que estagna o export.
2. **8 células do bug de física** — corrigir `topo_physics` para tratar tabela vazia.
3. **Avisos `UNCORRECTED`** — avaliar impacto de qualidade dos passes sem linha 6S.
4. **Coleção v1 legada** (`.../INDIA/mosaics-1`, ~47 TB) — candidata a retirada se o v2
   a substituir integralmente.

---

## 7. Como acessar os dados

- **Coleção:** `projects/mapbiomas-mosaics/assets/LANDSAT/LULC/INDIA/mosaics-2`
- **Nomenclatura:** `CÉLULA_ANO` (ex.: `NB-46-X-A_2018`).
- **Decodificação das bandas:** ver a descrição da coleção
  (`india/docs/collection_description.txt`) e `india/docs/band_value_ranges.md`.
- **Visualização no Code Editor:** scripts em `india/docs/` (`viewer_year_slider.js`,
  `viewer_v1_v2_compare.js`, `visualize_stuck_mosaics.js`).
