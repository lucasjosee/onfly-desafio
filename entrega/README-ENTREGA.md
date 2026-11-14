# Entrega

## Como investigou/abordou o problema

Primeiro, analisei os testes que falhavam: quais eram seus resultados esperados e obtidos, quais os casos de teste e qual regra de negócio abordavam. Em seguida, fui analisando cada arquivo do `services` e comparando com a sua respectiva regra de negócio. Por fim, veio a validação através dos testes e, depois, a validação com os dados reais.

## Como validar

Com o ambiente preparado conforme o README principal:

```bash
pytest -q

PYTHONPATH=src python -m onfly_report \
  --input data/reservas_hoteis.csv \
  --rates data/taxas_cambio.csv \
  --output output/report.json
```

Saída esperada do CLI: `Reservas: 300 | Confirmadas: 235 | Noites: 1347 | Total BRL: 396170.00`.

**Resultado do pytest:**

```text
.......                                                                  [100%]
7 passed in 0.37s
```

---

## Defeitos corrigidos

### 1. `test_status_rules` — Regras de status

**Causa raiz:** `is_billable` excluía apenas `"CANCELLED"` e deixava `"NO_SHOW"` passar.

Ao rodar o pytest e analisar as entradas de teste:

```json
{"reservation_id": "R-1", "status": "CONFIRMED", "amount": "100.00"}
{"reservation_id": "R-2", "status": "CANCELLED", "amount": "50.00"}
{"reservation_id": "R-3", "status": "NO_SHOW", "amount": "20.00"}
```

E também o resultado final de `total_amount`:

| Esperado | Obtido |
| -------- | ------ |
| 100.00   | 120.00 |

Percebi que o `NO_SHOW` estava sendo somado à fatura, além de somar noites, `by_month` e `top_hotels`. No código, vi que existia uma comparação que deixava o `NO_SHOW` passar.

**Antes:**

```python
return status != "CANCELLED"
```

Inverti a lógica, fazendo a função só retornar `True` se o status for `CONFIRMED`.

**Depois:**

```python
return status == "CONFIRMED"
```

**Como validar:**

```bash
pytest -q tests/test_status_rules.py
```

---

### 2. `test_currency_conversion_to_brl` — Câmbio

**Causa raiz:** `convert_to_brl` não multiplicava o valor, e sim dividia.

Já no pytest, percebi que a saída estava muito inferior à esperada:

| Esperado | Obtido |
| -------- | ------ |
| 642.00   | 118.45 |

Também olhei nas regras de negócio do README que a conversão é feita multiplicando `amount` por `rate_to_brl`. E, quando olhei o service, ele estava dividindo ao invés de multiplicar.

Troquei apenas o sinal e o teste passou.

**Como validar:**

```bash
pytest -q tests/test_currency.py
```

---

### 3. `test_nights_across_month_boundary` — Noites

**Causa raiz:** `calculate_room_nights` usava `.day`, pegando o dia do check-in e do checkout e subtraindo. Porém, isso não trata os casos de virada do mês:

```json
"checkin_date": "2025-01-30"
"checkout_date": "2025-02-02"
```

| Esperado | Obtido |
| -------- | ------ |
| 3        | -28    |

A própria biblioteca `datetime` cuida desses casos, permitindo subtrair as datas e, em seguida, mostrar os dias usando `.days`. Essa lógica também está descrita no README, na lógica de negócio.

**Antes:**

```python
return (checkout.day - checkin.day) * rooms
```

**Depois:**

```python
return (checkout - checkin).days * rooms
```

**Como validar:**

```bash
pytest -q tests/test_nights.py
```

---

### 4. `test_top_hotels_are_ranked_descending` — Ordenação

**Causa raiz:** A função `sorted`, dentro do arquivo `report_builder.py`, ordenava os itens por `amount`, mas de forma incorreta. O certo é ordenar de forma decrescente, e ela estava fazendo o contrário.

O problema foi resolvido de forma simples, apenas colocando um `-` antes do item, tornando-o negativo. E o valor negativo vem primeiro.

**Antes:**

```python
ranked_hotels = sorted(hotels.items(), key=lambda item: (item[1]["amount"], item[0]))
```

**Depois:**

```python
ranked_hotels = sorted(hotels.items(), key=lambda item: (-item[1]["amount"], item[0]))
```

**Como validar:**

```bash
pytest -q tests/test_top_hotels.py
```

---

### 5. `test_regression_report_on_sample` — Teste de regressão

Esse teste não exigiu correção própria; ele combina status, noites e câmbio. Após resolver o defeito de câmbio, que era a única coisa que afetava esse teste, ele passou.

**Como validar:**

```bash
pytest -q tests/test_regression_report.py
```

---

### 6. Dinheiro passando por `float`

**Causa raiz:** Na função `convert_to_brl`, o dinheiro, antes de ser passado para `Decimal`, passa por `float`, e o `float` não representa decimais exatamente, o que pode mudar o centavo em alguns casos.

Os testes fornecidos já passavam, mas, quando bati o olho na parte de exatidão, onde é deixado explícito que não pode ser usado `float`, dei mais uma checada no arquivo.

**Antes:**

```python
return Decimal(str(float(amount) * float(rate)))
```

**Depois:**

```python
return amount * rate
```

Como as variáveis `amount` e `rate` já são `Decimal`, a conversão não é necessária.

**Como validar:**

```bash
pytest -q tests/test_money_precision.py
```

---

### 7. O relatório não usa o arquivo inteiro

**Causa raiz:** O código não lia o arquivo CSV inteiro, parando na linha 200 por causa de um `if`.

Ao rodar o CLI, percebi que o código lia apenas 200 das 300 linhas disponíveis no CSV. Quando olhei o arquivo `csv_reservation_repository.py`, vi que existia um `if` que parava a leitura quando as linhas chegavam a 200. Removi o `if` e agora o arquivo inteiro é lido.

**Como validar:**

```bash
pytest -q tests/test_full_file_read.py
```
