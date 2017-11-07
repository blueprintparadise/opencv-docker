# BUGS #

Existe algum problema na utilização do python socket com UDP no lado do cliente.
Quando precisamos mandar diversos pacotes em rápida sequencia, como no caso de uma imagem, a quantidade de perdas que está acontecendo é muito grande.
Em cliente-cv.py foi necessário colocar um sleep entre os sendto's pois parece que o problema ocorre porque a fila de envio enche, mas não dá erro.

```python
connection.sendto(msg, (server_ip, server_port))
time.sleep(0.0001)  # PYTHON BUG: this sleep is need, so the local processor can put the packet in the queue
```
