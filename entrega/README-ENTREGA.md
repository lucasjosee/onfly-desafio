1  - test_status_rules / Regras de status

Causa raiz: is_billable escluia apenas "CANCELLED" e deixava "NO_SHOW" passar.

Ao rodar o pytest e analisar as entradas de teste:

{"reservation_id": "R-1", "status": "CONFIRMED", "amount": "100.00"};
{"reservation_id": "R-2", "status": "CANCELLED", "amount": "50.00"};
{"reservation_id": "R-3", "status": "NO_SHOW", "amount": "20.00"};

E tambem o resultado final de total_amount:
 
Esperado - 100.00
     
Obtido - 120.00
 

Percebi que o NO_SHOW estava sendo somado a fatura, alem de somar noites, by_month e top_hotels. No codigo vi que existia uma comparação que deixava o NO_SHOW passar.

return status != "CANCELLED" -> return status == "CONFIRMED"

Inverti a logica, fazendo a função só retornar true se o status for confirmed.

Como validar:
pytest -q tests/test_status_rules.py