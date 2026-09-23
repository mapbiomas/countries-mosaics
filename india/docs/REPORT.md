# Relatório de entrega — contrato de conteúdo

O que o relatório de entrega dos mosaicos precisa conter, de onde vem cada número e
como reconstruí-lo. **Ler antes de mexer na página ou de escrever o próximo relatório**:
o objetivo deste arquivo é que a próxima rodada produza o mesmo documento, e não um
documento diferente com a mesma finalidade.

- Publicado: <https://claude.ai/artifact/UC6xhNbzn6NaY5RFFaojPC> (privado; compartilhar pelo
  menu Share da própria página antes de mandar para a equipe).
- Fonte da página: `docs/delivery_report.html` — referencia `ds/` e `img/` como irmãos,
  **não abre sozinho**.
- Cópia versionada: `docs/delivery_report.standalone.html` — tudo embutido, abre com
  duplo clique. É o arquivo que o repositório guarda.

## Idioma e design

- **Inglês.** O relatório é lido pela equipe internacional; o resto do repo é pt-BR.
  Números no formato inglês (`10,847` · `95.8%`), datas `22 Sep 2026`.
- **Design system MapBiomas obrigatório**: <https://claude.ai/artifact/79QHMmzNVuF9NtFFx1Q6DH>.
  A página carrega o bundle real (`ds/bundle.css` + `ds/bundle.js` + React 18 + Lucide) e
  monta componentes de verdade — `Card`, `Panel`, `StatusPill`, `Badge`, `MetaStrip`,
  `AttributeList`, `InfoBanner`, `LucideIcon`. Não reimplementar nenhum deles.
- Consequências que já custaram tempo, não reabrir:
  - **Open Sans, quatro tamanhos** (18/16/14/12), line-height 1,5 sempre. **Não existe
    escala de heading**: título é `body-large-strong`. Nada acima de 18px.
  - **Um acento só**, `#43798A` (`--color-primary-700`). Rampas temáticas
    (`color-green-vegetation-*` etc.) são dado — só mapa, legenda e gráfico.
  - Tema **claro apenas**: o design system não documenta modo escuro.
  - Fundo da página `--color-neutral-200`, superfícies brancas. Sombra só em `Panel`.
  - **Parágrafos justificados**, com hifenização, ocupando a coluna inteira (1100px).
    Última linha à esquerda (`text-align-last`). Tabelas, legendas e rótulos ficam à
    esquerda — justificar dado em coluna estreita abre buracos.
  - Todo `<img>` precisa de `height: auto`, senão o atributo `height` vira altura
    definitiva e anula o `aspect-ratio`.

## As seções, nesta ordem

| # | Seção | Conteúdo obrigatório |
|---|---|---|
| 1 | Capa | Logo + wordmark, eyebrow, título, `StatusPill` com o %, `MetaStrip` (data, N de M cell-years, coleção), dois parágrafos de resumo, barra de cobertura |
| 2 | Números-chave | 4 `Card`: mosaicos entregues, células × anos, bandas por imagem, resolução |
| 3 | The product | O que é um mosaico: ano fenológico, unidade espacial, período, resolução; as famílias das 117 bandas |
| 4 | Method | **A ordem das operações** (8 passos, numerada — é sequência real) + cards de Sources, Radiometry, Terrain/masking, Compositing, SMA + `InfoBanner` apontando o ATBD |
| 5 | Coverage | Gráfico de colunas: células entregues por ano fenológico, contra as 283. Tooltip por coluna + `<details>` com a tabela |
| 6 | **National scale** | Grid **4 colunas × 10 linhas**, um mosaico nacional por ano, mesma extensão e mesmo stretch. Legenda de cada tile: ano + `entregues/283` |
| 7 | Outcome | Tabela de reconciliação com `StatusPill` + cards das 8 células travadas e do aviso `UNCORRECTED` |
| 8 | The images | 6 células de amostra, **todas interiores, acima de 99% de pixels válidos** |
| 9 | **Run profile** | Vazão diária: colunas de mosaicos concluídos por dia + curva acumulada no mesmo eixo x, 4 stat cards, tabela completa, e o card "Planning the next one" |
| 10 | Incident | O travamento de export: causa medida, o teste decisivo, barras de comparação EECU, resolução |
| 11 | Open items | Pendências com `StatusPill` de estado |
| 12 | Access | Caminho da coleção, nomenclatura, docs de decodificação, viewers |

## De onde vem cada número

**Não reescrever nenhum destes de cabeça.** Fontes no repo:

| Número | Valor | Fonte |
|---|---|---|
| Plano | 11.320 = 283 × 40 | `pipeline/config.py` |
| Entregues | 10.849 (95,84%) | `scripts/monitor_status.py` → `listAssets` da coleção |
| Não construídos | 471 | `11.320 − entregues` |
| Por ano | tabela 1986–2025 | `docs/run_yearly_stats.txt` |
| Gaps de arquivo | 463 | `docs/entrega_dados_relatorio.md` |
| Bug de física | 8 | idem — `NC-43-Y-C` (1989, 2000, 2010), `NC-44-Y-C_1989`, `NG-46-Z-D_1986`, `NH-44-X-C_1987`, `NI-43-V-C_1986`, `NI-44-Y-D_1988` |
| Travados | **0** | relançados 2026-09-22 com fila vazia, concluíram os dois |
| Incidente | mediana ~41 min; 6–47h; 28/50 slots; 50→22 mosaicos/h; **71/71**; 6h→48h | `docs/stuck_mosaics_report.md` |
| Relançamento final | `NH-44-V-A_2021` 3h40 / 398.599 EECU · `NI-43-Z-D_2019` 11h30 / 418.396 EECU | 2026-09-22, fila vazia |
| Teste decisivo | `NG-43-X-D_2017`, 250 grânulos, 1,8h, ~74 EECU/s vs 13–21 sob contenção | idem |
| Vazão diária | 18 dias (4–21 set 2026), pico 1.225, mediana 620/dia, 26,09 TB, 586.791 cenas | `docs/run_daily_throughput.csv` |

> **Atenção:** a conta que fecha é **463 + 8 = 471** (desde 2026-09-23, quando as duas
> células "travadas" foram relançadas e concluíram). O `CLAUDE.md` chegou a dizer "471
> gaps" quando o total era 473 — coincidência de número, conta errada. Conferir sempre
> que `entregues + gaps + bloqueadas = 11.320`.

## As imagens

Duas famílias, geradas por `docs/make_report_thumbs.py` (precisa de Earth Engine
autenticado — `earthengine authenticate` uma vez, e o venv de `india/`).

| Família | Arquivo | Tamanho | O que é |
|---|---|---|---|
| Células de amostra | `img/<CÉLULA>_<ANO>.jpg` | 560 px | 6 células, cor verdadeira |
| Grid nacional | `img/india_<ANO>.jpg` | 450 × 480 | 1986–2025, país inteiro por ano |

- **Stretch único para as duas**: `red_median, green_median, blue_median`, `min 0`,
  `max 4000`, `gamma 1.3` — os mesmos de `docs/visualize_stuck_mosaics.js`. Não inventar
  outro: as imagens precisam ser comparáveis entre si.
- **JPEG, não PNG.** As mesmas 6 células em PNG custavam 2,35 MB; em JPEG, 0,54 MB.
- **Extensão do grid nacional**: `[67.5, 6.0, 97.5, 38.0]`, fixa, para os 40 tiles
  serem comparáveis. Vem de `col.filter(year=2018).geometry().bounds()`.
- **O preto é duas coisas**, e o relatório precisa dizer isso: em volta do país é a
  máscara de região (último passo do build, descarta o que está fora da união das
  regiões de classificação); **no interior** são as células sem cena usável naquele ano
  — as faixas de 1987 e 1988 são fileiras Landsat inteiras que nunca foram baixadas.
- **As células de amostra são escolhidas por cobertura**, não por gosto. Medir a fração
  de pixels válidos antes de escolher; usar só células acima de 99%. Células de litoral
  (`NB-46-X-A` 20%, `NC-46-Y-B` 4,8%, `NF-45-X-D` 40%) aparecem recortadas e foram
  rejeitadas por isso. O trecho de `make_report_thumbs.py` que mede a cobertura fica lá
  para reusar.

## Vazão diária — de onde sai

`docs/run_daily_throughput.py` → `docs/run_daily_throughput.csv`
(colunas: `date, completed, submitted, gb_written, scenes, cumulative`).

**Não usar `listOperations` para isso.** Ele tem teto e descarta operações antigas, então
sub-conta uma rodada longa. Os próprios assets entregues carregam as duas datas:

- `updateTime` do asset — quando o Earth Engine **terminou de escrever**. É a vazão.
- `properties.built_utc` — quando o pipeline **compôs e enfileirou** o export. É a sentada.

A diferença entre as duas é a espera na fila, que é exatamente do que tratou o incidente,
por isso as duas ficam no CSV e na tabela do relatório.

> A listagem completa (`ee.data.listAssets` paginado, com as propriedades) leva **vários
> minutos** para 10.847 assets. Se só a série de submissão for necessária,
> `col.aggregate_array('built_utc')` resolve em uma chamada rápida — mas não dá
> `updateTime` nem `sizeBytes`.

Números que saíram daí e que servem para planejar (estão no card "Planning the next one"):

| Pergunta | Resposta medida |
|---|---|
| Reprocessar a nação inteira (11.320) | ~18 dias na mediana observada, ~27 TB |
| Um ano novo (283 células) | ~meio dia, ~0,7 TB |
| Armazenamento | 2,40 GB por mosaico, em média |
| Insumo | ~54 cenas Landsat por imagem entregue |
| Não planejar pelo pico | 1.225/dia aconteceu uma vez, com fila drenada |

O gráfico marca a **janela de travamento (6–7 set)** com uma faixa `color-warning-200`
desenhada **antes** das colunas — se for desenhada depois, tinge as duas barras que ela
deveria destacar.

## Não repetir: "EECU congelado" não é travamento

O relatório e o `CLAUDE.md` afirmavam que duas células travavam por uma cena específica,
com o EECU congelando a 44% e 73%. **As duas eram falsas.** Relançadas com fila vazia em
2026-09-22, concluíram: 3h40 e 11h30, ~400k EECU cada. As porcentagens antigas eram
frações de um total que ninguém tinha medido.

E no relançamento bem-sucedido, `NI-43-Z-D_2019` ficou **1,2 h parado em 412.065 EECU** —
14 leituras de 5 min sem mover — e depois terminou. O contador anda em degraus.

Consequência para o texto do relatório: a seção Incident precisa dizer que **as 71 eram
contenção de fila, sem exceção**, e que a taxa de travamento real do pipeline é zero. Não
reintroduzir a história de "cena específica" numa revisão futura.

## Reconstruir

```bash
cd india && source .venv/bin/activate

# 1. imagens (Earth Engine) — escreve em <dir>/img/
python docs/make_report_thumbs.py

# 2. arquivos do design system — copiar do artefato do design system para <dir>/ds/
#    (bundle.css, bundle.js, react.js, react-dom.js, lucide.js)

# 3. o arquivo único versionado
python docs/build_report.py \
    --src    docs/delivery_report.html \
    --assets <dir> \
    --out    docs/delivery_report.standalone.html
```

Para republicar o artefato: publicar `delivery_report.html` como página junto de `ds/`
e `img/`, **com a URL existente**, para não criar um artefato novo.

### Armadilhas do build

- **Servir sempre com `charset=utf-8`.** O bundle do design system tem faixas
  não-ASCII dentro de expressões regulares; decodificado como latin-1 o navegador
  levanta `Invalid regular expression: range out of order` e a página não renderiza —
  fica em branco, sem erro visível. O `standalone` já carrega `<meta charset>` próprio;
  a versão publicada depende do servidor.
- **Caminhos de imagem são literais** no objeto `IMG` da página, de propósito:
  `build_report.py` troca cada string por um data URI e só enxerga caminho escrito por
  extenso. Não voltar a montar `'img/' + nome + '.jpg'`.
- As fontes (Open Sans, Montserrat) continuam vindo do Google Fonts por `@import` dentro
  de `bundle.css`. O `standalone` precisa de rede para elas; sem rede, cai no fallback
  sans-serif e o resto da página fica intacto.
- O `standalone` tem ~4,5 MB. Cada regeneração reescreve o blob inteiro no git, então
  regerar por entrega, não por ajuste de texto.
