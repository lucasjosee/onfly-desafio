1 - test_status_rules / Regras de status

Causa raiz: is_billable escluia apenas "CANCELLED" e deixava "NO_SHOW" passar.

Ao rodar o pytest e analisar as entradas de teste:

{"reservation_id": "R-1", "status": "CONFIRMED", "amount": "100.00"};
{"reservation_id": "R-2", "status": "CANCELLED", "amount": "50.00"};
{"reservation_id": "R-3", "status": "NO_SHOW", "amount": "20.00"};

E tambem o resultado final de total_amount:
 
Esperado - 100.00
     
Obtido - 120.00
 

Percebi que o NO_SHOW estava sendo somado a fatura, alem de somar noites, by_month e top_hotels. No codigo vi que existia uma comparação que deixava o NO_SHOW passar.

Antes:
return status != "CANCELLED"

Inverti a logica, fazendo a função só retornar true se o status for confirmed.

Depois:
return status == "CONFIRMED"

Como validar:
pytest -q tests/test_status_rules.py


2 - test_currency_conversion_to_brl / Câmbio

Causa raiz: concert_to_brl não multiplicava o valor e sim dividia.

Já no pytest percebi que a saida estava muito inferior que a esperada:

Esperado - 642.00

Obtido - 118.45

Também olhei nas regras de negocio do REAME que a conversão é feita multiplicando amout por rate_to_brl. E quando olhei o service ele estava divindo ao inves de estar multiplicando.


Troquei apenas o sinal e o teste passou

Como validar:
pytest -1 tests/test_currency.py


3 - test_nights_across_month_boundary / Noites

Causa raiz: calculate_room_nights usava .day, pegando o dia do checkin e checkout, e subtraindo. Porem, isso não trata os casos de virada do mes:

"checkin_date": "2025-01-30"
"checkout_date": "2025-02-02"

Esperado - 3

Obtido - -28

A propria biblioteca datatime cuida desses casos, permitindo subtrair as datas e em seguida possibilitando mostrar os dias usando .days. Essa logica tambem está descrita no README na logica de negocio.

antes:
return (checkout.day - checkin.day) * rooms

depois: 
return (checkout - checkin).days * rooms

Como validar:
pytest -1 tests/test_nights.py


4 - Test_top_hotels_are_ranked_descending / Ordenação

Causa raiz: A função sorted, dentro do arquivo report_builder.py, ordenava os itens total_brl mas de forma incorreta. O certo é ser ordenado de forma decrescente, e ele estava fazendo o contrario.

O problema foi resolvido de forma simples, apenas colocando um "-" antes do item tornando ele negativo. E o valor negativo vem primeiro.


Antes:
ranked_hotels = sorted(hotels.items(), key=lambda item: (item[1]["amount"], item[0]))

Depois:
ranked_hotels = sorted(hotels.items(), key=lambda item: (-item[1]["amount"], item[0]))

Como validar:
pytest -1 tests/test_top_hotels.py


5 - test_regression_report_on_sample / Teste de regressão

Esse teste não exigiu correção propria, ele combina status, noites e cambio. Após resolver o defeito de cambio, que era a unica coisa que afetava esse teste, ele passou.

Como validar:
pytest -1 tests/test_regression_report.py


6 - Dinheiro passando por float

Causa raiz: Na função convert_to_brl, o dinheiro antes de ser passado para Decimal, passa por float, e o float não representa decimais exatamente e isso pode mudar o centavo em alguns casos. 

Os teste fornecidos ja passavam, mas quando bati o olho na parte de exatidão, onde é deixado explicito que não pode ser usado float dei mais uma checada no arquivo.

Antes:
return Decimal(str(float(amount) * float(rate)))

Depois:
return amount * rate

Como as variaveis amount e rate ja são Decimais, não é necessario a converção.

Como validar:
pytest -q tests/test_money_precision.py




