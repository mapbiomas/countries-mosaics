# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# countries-mosaics

Mosaicos anuais Landsat por país (MapBiomas countries-mosaics). O subprojeto ativo é
**`india/`** — pipeline v2 dos mosaicos anuais da Índia (IOLN), 30 m, uma imagem por
célula 1:250.000 por ano fenológico (abr→mar), 117 bandas, 1986–2025.

> Para **rodar**: `india/README.md` (visão geral) e `india/RUNNING.md` (passo a passo
> para quem clonou e nunca viu). O método completo é o ATBD em
> `india/docs/IOLN Landsat Mosaics ATBD.pdf`. Este arquivo **não repete** isso —
> registra o que não está lá: estado da rodada, incidentes, decisões e pendências.

## Arquitetura (big picture)

O pipeline está em `india/pipeline/` e monta **uma imagem por (célula, ano)**. A
ordem de processamento é crítica e está documentada no docstring de `build.py`:

```
mask            pixels limpos são pré-condição da correção e do BRDF
topographic     C físico (SCS+C via 6S), ANTES do BRDF (ordem C2-physics)
BRDF            depois bandpass, sobre a reflectância corrigida
SMA             roda no espaço x10000 (onde os endmembers são calibrados)
indices         rodam no espaço 0-1 (divide e multiplica de volta)
composite       percentis dry/wet ao longo do ano fenológico
static bands    terreno, coordenadas, contagens de proveniência
region mask     por último: clipa à união das regiões de classificação
```

Módulos e responsabilidades (cada um um passo ou um domínio):

- `config.py` — **tudo** que é tunável: assets, anos, bandas, tipos, thresholds,
  regimes. Nada a jusante deve hardcodar id de asset/banda. É o arquivo mais lido.
- `sources.py` — monta a coleção Landsat C2 T1 L2 (join inner com L1 p/ ângulos),
  `merge_passes` (deduplica overlap de fileira), `apply_sensor_fill` (L7 listrado).
- `masking.py` — witness mask (QA C2 + testemunha térmica), `MASK_RULE='both'`.
- `terrain.py` — terreno/iluminação; `topo_physics.py` — o C físico (tabelas 6S).
- `radiometry.py` — BRDF (Roy 2016), harmonização TM→ETM/ETM→OLI, escala x10000.
- `sma.py` — unmix espectral (gv/npv/soil/shade/ndfi); `indices.py` — índices.
- `compositing.py` — medianas, percentis dry/wet (p25/p75 por NDVI), swing/MAD.
- `build.py` — orquestração: `build_mosaic()` monta o grafo; `export()` enfileira um
  export (skip de existentes + zero-scene + active-tasks); `apply_band_types()`.
- `run.py` — driver de lab (célula/ano único, `--smoke`); `run_production.py` — driver
  nacional (11.320 cell-years, em "sentadas", com `--progress`).

Fluxo de execução: `run_production.run()` → `plan()` (283×40 pares) → para cada par
`build.export()` → `sources.build()` + `build_mosaic()` → `ee.batch.Export.image.toAsset()`.

`india/scripts/` são utilitários avulsos (verificar/exportar assets de apoio, validar
mosaicos). `india/tests/test_pipeline_contract.py` pina o contrato de bandas/propriedades
offline.

## Rodar (atalhos)

```bash
# setup (dentro de india/)
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
earthengine authenticate          # uma vez

# via notebook (recomendado p/ primeiro contato)
jupyter notebook notebooks/run_mosaics.ipynb

# via terminal (mais estável p/ rodada longa)
python -m pipeline.run_production --plan
python -m pipeline.run_production --run --confirm "QUEUE THE NATIONAL RUN"
python -m pipeline.run_production --progress

# lab / célula única
python -m pipeline.run --smoke
python -m pipeline.run --export --cell NH-43-X-C --year 2023
```

## Configuração (o que um fork muda)

Tudo em `india/pipeline/config.py`. O **modelo de fork**: inputs são assets publicados
(`projects/mapbiomas-india/assets/mosaic_v2_inputs`) que um fork **lê onde vivem, nunca
reconstrói**. Um fork muda só duas coisas: `EE_PROJECT` (billing) e `OUTPUT_COLLECTION`
(destino). **Não repontar** `ASSET_ROOT` / `INPUTS_ROOT`.

- Produção: `PRODUCTION_COLLECTION = projects/mapbiomas-mosaics/assets/LANDSAT/LULC/INDIA/mosaics-2`.
- Nome de asset de produção: `CÉLULA_ANO` (ex. `NB-46-X-A_2018`), sem sufixo/versão.
- Janela fenológica: 1 abr Y → 31 mar Y+1. Anos 1986–2025 (40 anos × 283 células = 11.320).

## Monitoramento (comandos + modelo canônico de status)

Tudo o que foi usado para acompanhar a rodada e os problemas. O objetivo é que o
relatório de status **saia igual toda vez** — usar o script, não trechos ad-hoc.

### Relatório de status canônico

```bash
cd india
python scripts/monitor_status.py                 # produção, janela 6h, travado >8h
python scripts/monitor_status.py --hours 12      # janela de vazão diferente
python scripts/monitor_status.py --collection projects/.../mosaics-2
```

Formato fixo (não mudar; se precisar de algo novo, adicionar um bloco, nunca reordenar):

```
agora (UTC): YYYY-MM-DD HH:MM

=== TAREFAS ===
done: N | running: N | pending: N | failed: N
progresso: XX.X%
SUCCEEDED/h (últimas Nh): {HH:00 -> N, ...}
média últimas 4h: N/h
restante a concluir: N mosaicos
ETA (a N/h): Nh = N.N dias

=== ESPAÇO ===
uso: X.XX TB / Y.YY TB | livre: Z.ZZ GB

=== TRAVADOS (>8.0h) ===
  CÉLULA_ANO  N.Nh          (ou "nenhum")
```

**Semântica (importante p/ não se enganar):**
- `done` vem da **coleção** (`listAssets`), não de `listOperations` — é a fonte da
  verdade do que realmente está entregue. `listOperations` tem teto e descarta ops
  antigas, então **sub-conta** o done.
- `failed` conta operações `FAILED` no histórico de `listOperations` — pode incluir
  falhas já recuperadas (ex.: as 41 de quota foram re-enfileiradas e concluídas). O
  número que importa para "o que falta" é `total - done - running - pending`.
- Total fixo = **11.320** (283 células × 40 anos). `remaining = 11.320 - done`.

### Detecção de travados (stuck vs. lento)

Um export "preso" é um `RUNNING` muito além da mediana (~41 min). O divisor de águas é
o **EECU**, não o wall-clock:

- `batchEecuUsageSeconds` **subindo** → está computando (lento, mas saudável). Deixar rodar.
- EECU **congelado** por horas → travado de verdade (estagna no meio do export). Cancelar.

Thresholds usados: **>8h** marca straggler; **>48h** cancela (auto-cancel). Medidas reais:
`NG-43-X-D_2017` completou em 1,8h com ~479k EECU; `NH-44-V-A_2021` estagnou em ~211k (44%);
`NI-43-Z-D_2019` estagnou em ~348k (73%). Consulta direta de uma operação:

```python
ee.Initialize(project='mapbiomas-mosaics')
meta = ee.data.getOperation('projects/mapbiomas-mosaics/operations/<ID>').get('metadata', {})
# state, startTime, endTime, batchEecuUsageSeconds
```

Cancelar: `ee.data.cancelOperation('projects/mapbiomas-mosaics/operations/<ID>')`.

### Reenfileirar o que falta (retomada)

Re-executar o driver retoma sozinho (skip de existentes + em-voo + zero-scene). Para
reenfileirar só um subconjunto (ex.: as travadas, as falhas, os gaps), o padrão é:
listar `listOperations`/`listAssets`, calcular `plan - coleção`, e passar o `existing`
(set de basenames da coleção) ao `build.export(..., existing=existing)` — assim o skip é
em memória, não um `getAsset` por cell-year. O driver `run_production.run()` já faz isso.

### Reconciliação (o que falta e por quê)

`plan (283×40) − coleção` = faltantes. Classificar por causa:
- **travada** (CANCELLED com `RUNNING ≥6h`) → reprocessar;
- **failed** (`FAILED`) → re-enfileirar (quota/transitório);
- **gap** (zero-scene, anos pré-2000) → aceitar, não relançar.

## Cuidados / gotchas (aprendidos em produção, não óbvios no README)

- **`build.export` recusa** label/variant/lite quando o destino é a coleção de produção
  (regra 2026-09-01) — impossível escrever build de lab sob nome de produto.
- **Retomada**: o loop pula assets que já existem E os que estão em export (via
  `_active_export_descriptions`, 1 `listOperations`/min). Re-executar nunca duplica.
- **Fila tem teto** por conta (não por projeto): quando enche, o driver para sozinho
  ("too many/quota/rate limit/exceeded"). Rodada é feita **em sentadas**.
- **`priority` não é permitido** neste projeto (`Custom priority can only be set on tasks
  in registered commercial projects`) — não dá pra saltar a fila.
- **`shardSize` é o nome legado de `tileSize`** (a API converte internamente).
- **Autenticação**: esta sessão às vezes roda com `ANTHROPIC_AUTH_TOKEN` setado, o que
  **bloqueia leitura/publicação de Artifacts claude.ai**. Para artefatos: `unset
  ANTHROPIC_AUTH_TOKEN` + reiniciar + `/login` (ou colar o conteúdo manualmente).
- **Zero-scene**: cell-year sem grânulos usáveis é pulado como "honest gap" (não é erro).

## Estado da rodada nacional (2026-09-22)

Coleção `mosaics-2`, 10.847/11.320 construídos (**95,8%**).

| Desfecho | Qtd | Detalhe |
|---|---|---|
| Construídos | 10.847 | 95,8% |
| Gaps de arquivo | 463 | pré-2000 sem cenas (zero-scene); 1986 é o pior (30/283) |
| Travados reais | 2 | `NH-44-V-A_2021`, `NI-43-Z-D_2019` — estagnam no export (EECU congela) |
| Bug de física | 8 | overpass table vazia → `NoneType has no len()` (ver abaixo) |

> Os 473 não construídos = **463 + 8 + 2**. Este arquivo já disse "471 gaps", que não
> fecha contra 11.320; a conta correta é a da tabela e a de
> `india/docs/entrega_dados_relatorio.md`.

### Incidente "travamento de export" (causa raiz medida)
- Exports ficavam `RUNNING` 6–47h (mediana ~41 min). Pior caso: 28/50 slots parados.
- **Causa = contenção de fila, não bug.** Canceladas tinham EECU alto (35k–450k s) =
  estavam computando; o auto-cancel de 6h cortava trabalho ainda em andamento.
- Teste decisivo: `NG-43-X-D_2017` (250 grânulos) completou em **1,8h** com fila vazia
  (~74 EECU/s) vs ~13–21 EECU/s sob contenção.
- `shardSize=32` e `cloud<60/40/30` NÃO resolveram (limite no grafo; 182 grânulos ainda
  estouram e tabelas overpass/witness seguem a 250).
- **Resolução:** relançar com fila vazia → 69/71 completaram em ~2h. Auto-cancel subiu
  de 6h → 48h.

### Bug de física (8 células bloqueadas)
`NC-43-Y-C` (1989,2000,2010), `NC-44-Y-C_1989`, `NG-46-Z-D_1986`, `NH-44-X-C_1987`,
`NI-43-V-C_1986`, `NI-44-Y-D_1988` — têm 1–6 grânulos mas overpass table vazia → o passo
de correção topográfica (`topo_physics`) faz `len()` em `None` e crasha. **Fix provável:**
tratar lista vazia como "sem correção" — destravaria as 8 de graça. Ainda NÃO feito.

## Pendências / follow-ups

1. **2 travadas reais** — investigar a cena específica que estagna o export a 44%/73%.
2. **8 células do bug de física** — fix do `topo_physics` (overpass vazio).
3. **`WARNING ... ship UNCORRECTED`** — alguns passes L5/L7 sem linha na tabela 6S
   (topo não aplicado) em certas células/anos; checar impacto de qualidade.
4. **Espaço** — liberamos ~25 TB (Indonesia/DRC/MA-legado); `.../INDIA/mosaics-1` (v1,
   ~47 TB) segue existindo e é candidata a retirada futura se o v2 a substituir.

## Relatório de entrega (feito — 2026-09-22)

Entregue. **O contrato de conteúdo é `india/docs/REPORT.md`** — ler antes de mexer na
página ou de escrever o próximo relatório; lá estão as seções na ordem, a fonte de cada
número, as regras do design system e como reconstruir. Aqui só o mapa dos arquivos:

| Arquivo | O que é |
|---|---|
| `https://claude.ai/artifact/UC6xhNbzn6NaY5RFFaojPC` | publicado (privado; compartilhar pelo menu Share) |
| `india/docs/REPORT.md` | **o contrato** — seções, números, imagens, build |
| `india/docs/delivery_report.html` | fonte da página; precisa de `ds/` e `img/` irmãos |
| `india/docs/delivery_report.standalone.html` | tudo embutido (~4,5 MB), abre com duplo clique — é a cópia versionada |
| `india/docs/make_report_thumbs.py` | gera as imagens (Earth Engine); `--coverage ANO` mede pixels válidos por célula |
| `india/docs/build_report.py` | fonte + assets → arquivo único |
| `india/docs/run_daily_throughput.py` → `.csv` | vazão dia a dia da rodada, lida dos assets entregues |

### Vazão da rodada (medida — serve para planejar a próxima)

A rodada nacional levou **18 dias** (4–21 set 2026): **10.847 mosaicos**, **26,09 TB**,
586.791 cenas Landsat. Pico 1.225/dia (8 set), **mediana 620/dia** — planejar pela
mediana, não pelo pico. 10.799 dos 10.847 caíram nos primeiros 14 dias; o resto é cauda
de stragglers. Médias úteis: **2,40 GB por mosaico**, ~54 cenas por imagem.

- Reprocessar a nação inteira: **~18 dias, ~27 TB**.
- Um ano novo (283 células): **~meio dia, ~0,7 TB**.
- A fila tem teto por conta, então a rodada é feita **em sentadas** — as submissões
  aparecem em blocos (2.394 no dia 8, 2.711 no dia 14) e os dias seguintes são o backlog
  drenando.
- **Não usar `listOperations`** para reconstruir isso: tem teto e descarta ops antigas.
  Os assets carregam `updateTime` (concluído) e `properties.built_utc` (enfileirado).

Decisões que não devem ser refeitas do zero (o porquê está no `REPORT.md`): relatório em
**inglês**; design system MapBiomas com o **bundle real**, não reimplementado; parágrafos
justificados na coluna inteira; grid nacional **4 × 10** com stretch fixo; células de
amostra escolhidas por **cobertura medida** (>99%), nunca a olho — célula de litoral sai
recortada pela máscara de região e parece defeito.

- Esboço antigo, superado: `india/docs/run_closeout_report.html` (candidato a remoção).
- `india/docs/run_thumbnails.json` também está superado — as miniaturas agora saem de
  `make_report_thumbs.py`, em JPEG e com cobertura verificada.

## Metodologia (resumo — autoridade é o ATBD e `india/pipeline/config.py`)

- **Fontes:** Landsat Collection 2 **Tier 1 Level 2** (L5/L7/L8/L9), join inner com L1
  para ângulos (SZA/SAA/VZA/VAA); `CLOUD_COVER < 95`; L7 listrado preenche trimestres
  finos (`apply_sensor_fill`).
- **Radiometria:** BRDF Roy 2016 (c-factor RTLSR); harmonização TM→ETM (derivada do
  overlap 1999–2011 da Índia) e ETM→OLI (Roy 2016).
- **Topografia:** SCS+C com C físico (tabelas 6S por sensor, MERRA-2 AOT/WV);
  `TOPO_C_ESTIMATOR = 'physics'`.
- **Máscara:** witness mask (QA C2 + testemunha térmica), `MASK_RULE = 'both'`.
- **Composição:** mediana + dry/wet (p25/p75 por NDVI), swing (p95−p5), MAD; por pixel,
  por quartil. `merge_passes` deduplica overlap de fileira.
- **117 bandas** (contrato v2); 32 com tipos estreitos (uint8/int8). Ver
  `india/docs/band_value_ranges.md` e `band_and_property_contract.md`.
- **SMA:** 24 bandas (gv/npv/soil/shade/ndfi); endmembers herdados da Amazônia
  (não derivados p/ Índia — registrado no preflight).

## Testes

Sem `pytest` no venv; os testes offline rodam com:
```bash
cd india
python -m unittest tests.test_pipeline_contract          # suíte toda (35 testes, offline)
python -m unittest tests.test_pipeline_contract.BandContractTests.test_117_bands   # um teste
```

Verificação rápida de sintaxe: `python -m py_compile pipeline/build.py`.
