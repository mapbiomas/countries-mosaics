# Mosaicos travados na exportacao — relatorio final

> Encerrado em 2026-09-22. Documenta o incidente de "travamento" de exportacao, a causa raiz e a resolucao.

## Conclusao (uma frase)

O "travamento" era **contencao de fila**, nao bug: com a fila cheia as celulas densas ficavam sem workers e demoravam horas; com a fila vazia, cada uma completa em ~2h. Relancar resolveu **69 das 71** (97%).

## Causa raiz (medida, nao especulada)

- As tarefas canceladas em 6h tinham **EECU alto** (35k–450k s) — estavam **computando**, nao paradas. O auto-cancel em 6h cortava tarefas ainda em andamento.
- Teste isolado `NG-43-X-D_2017` (250 granulos): **completou em 1.8h** (479k EECU, ~74 EECU/s) com a fila vazia — vs ~13–21 EECU/s quando a fila estava cheia.
- `cloud<60/40/30` **nao resolveu**: 215/196/182 granulos ainda estouram o teto de memoria interativo, e as tabelas pre-computadas (overpass/witness) seguem a 250.
- `shardSize=32` **nao resolveu**: o limite e no grafo, nao no tile do export.

## Residuo: 2 travamentos reais (cena-especifico)

Alem da contencao, ha um residuo de ~2 celulas que **estagnam no meio do export** (EECU congelado), provavelmente por uma cena especifica:

- `NH-44-V-A_2021` (245 granulos): estagnou a ~44% (EECU congelado em 211k por ~10h).
- `NI-43-Z-D_2019` (251 granulos): estagnou a ~73% (EECU congelado em 348k por ~13h).

Taxa: **2 / 11.320 = 0,02%**.

## Estado final

| | Qtd |
|---|---|
| Concluido | **10.847 / 11.320 (95,8%)** |
| Gaps de arquivo (pre-2000, sem dados) | 471 |
| Travadas reais (nao resolvidas) | 2 |

## Lista das 71 celulas-anos travadas (historico)

> A grande maioria foi resolvida relancando; a lista fica como registro do incidente.

| granulos | celula | ano | horas travada |
|---|---|---|---|
| 299 | `NI-44-Y-C` | 2021 | 6h |
| 298 | `NG-43-V-B` | 2022 | 25h |
| 285 | `NI-43-Z-D` | 2021 | 6h |
| 282 | `NG-45-Y-C` | 2024 | 14h |
| 277 | `NI-43-Z-C` | 2021 | 7h |
| 276 | `NG-45-Y-D` | 2024 | 13h |
| 276 | `NG-43-X-C` | 2021 | 17h |
| 275 | `NG-45-Y-C` | 2023 | 14h |
| 271 | `NI-44-Y-D` | 2022 | 6h |
| 271 | `NI-44-Y-D` | 2015 | 6h |
| 268 | `NJ-43-Z-A` | 2023 | 7h |
| 267 | `NI-44-Y-D` | 2025 | 6h |
| 266 | `NI-44-Y-D` | 2020 | 6h |
| 265 | `NI-44-Y-D` | 2019 | 6h |
| 265 | `NI-44-Y-C` | 2024 | 6h |
| 264 | `NI-43-Z-C` | 2017 | 6h |
| 262 | `NI-44-Y-D` | 2017 | 7h |
| 262 | `NI-44-Y-D` | 2016 | 6h |
| 262 | `NI-43-Z-D` | 2022 | 6h |
| 262 | `NI-43-Z-D` | 2017 | 6h |
| 262 | `NI-43-Y-D` | 2017 | 6h |
| 261 | `NI-44-Y-C` | 2017 | 6h |
| 260 | `NG-43-V-C` | 2019 | 24h |
| 259 | `NI-44-Y-C` | 2016 | 6h |
| 258 | `NI-43-Y-B` | 2021 | 6h |
| 258 | `NH-44-V-B` | 2021 | 6h |
| 257 | `NG-42-X-C` | 2019 | 35h |
| 255 | `NI-44-Y-C` | 2020 | 6h |
| 255 | `NG-45-Y-D` | 2021 | 13h |
| 255 | `NG-43-V-D` | 2016 | 22h |
| 254 | `NG-43-V-D` | 2019 | 22h |
| 252 | `NI-43-Z-D` | 2016 | 6h |
| 252 | `NI-43-Z-C` | 2016 | 6h |
| 252 | `NI-43-Y-D` | 2016 | 6h |
| 251 | `NJ-43-Z-D` | 2021 | 7h |
| 251 | `NI-43-Z-D` | 2019 | 6h |
| 250 | `NG-43-X-D` | 2017 | 16h |
| 250 | `NI-44-Y-D` | 2014 | 6h |
| 247 | `NG-42-X-B` | 2015 | 37h |
| 245 | `NI-43-Z-D` | 2025 | 7h |
| 245 | `NH-44-V-A` | 2021 | 7h |
| 242 | `NI-43-Z-C` | 2020 | 7h |
| 225 | `NG-43-X-A` | 2019 | 20h |
| 219 | `NJ-43-Z-A` | 2020 | 6h |
| 212 | `NG-45-V-A` | 2022 | 23h |
| 192 | `NG-46-Z-D` | 2020 | 16h |
| 186 | `NI-43-Z-D` | 2008 | 7h |
| 177 | `NH-43-Y-D` | 2017 | 7h |
| 169 | `NH-43-Y-C` | 2013 | 7h |
| 168 | `NG-42-Z-A` | 2019 | 31h |
| 156 | `NG-45-V-A` | 2020 | 23h |
| 143 | `NH-46-Z-A` | 2008 | 6h |
| 136 | `NH-46-Z-C` | 2018 | 6h |
| 128 | `NG-45-V-C` | 2005 | 22h |
| 125 | `NI-43-V-A` | 2010 | 6h |
| 115 | `NH-46-Z-D` | 2018 | 6h |
| 114 | `NH-45-Z-C` | 2005 | 6h |
| 93 | `NG-45-Y-B` | 1992 | 17h |
| 82 | `NJ-43-Y-C` | 2012 | 6h |
| 76 | `NG-46-X-B` | 2000 | 25h |
| 75 | `NG-45-Y-B` | 1989 | 17h |
| 70 | `NH-43-X-A` | 1994 | 12h |
| 67 | `NG-45-Y-C` | 2000 | 15h |
| 66 | `NH-44-Y-B` | 2012 | 6h |
| 61 | `NH-42-Z-D` | 1993 | 15h |
| 58 | `NF-45-X-D` | 1992 | 47h |
| 53 | `NI-43-Z-A` | 2002 | 6h |
| 44 | `NI-43-V-A` | 1995 | 6h |
| 38 | `NF-45-X-D` | 1988 | 47h |
| 28 | `NH-44-V-C` | 2001 | 6h |
| 24 | `NH-44-V-B` | 1991 | 6h |
