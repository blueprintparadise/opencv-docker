# BUGS #

Este programa não está funcionando corretamente.
Existe algum problema na utilização do python socket com UDP que precisa ser verificado.
Quando precisamos mandar diversos pacotes, como no caso de uma imagem, a quantidade de perdas que está acontecendo é muito grande.

Teste-client.py é utilizado somente para gerar pacotes de tamanho diversos para testar a comunicação UDP.
Com ele vemos que existem muitas perdas, para tamanhos de dados cerca de 10x menores que o necessário para a captura, mesmo com o cliente e o servidor na mesma máquina. (MUITO ESTRANHO !!!)