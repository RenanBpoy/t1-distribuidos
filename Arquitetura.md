# Arquitetura do sistema

## Definição do trabalho

O Trabalho 2 consiste em implementar e avaliar uma solução que garanta algum nível de tolerância a falhas para o Trabalho 1, usando replicação.

a) O que acontece se um dos servidores web ou do banco de dados falhar?

b) Quantas réplicas serão usadas? Como atualizar as réplicas? Qual o protocolo de atualização das réplicas? Como isso impacta na minha solução?

c) Os servidores são stateful ou stateless? Como isso impacta na minha solução?

Parte 1: projeto da arquitetura da solução e cenário de experimentos

Parte 2: avaliação da arquitetura proposta através de experimentos


## Projeto da arquitetura do sistema

Resumo da proposta:

- Fazer outra(s) instância(s) do banco de dados
- Criar um script para que os bancos possam se sincronizar e alterar entre eles para criar a tolerância a falhas


## Resumo dos slides da aula

https://ead06.proj.ufsm.br/pluginfile.php/5530406/mod_resource/content/1/chap-5-replication.pdf


Resumo dos slides da aula de replicação:
- definir o líder das réplicas (single-leader, multi-leader ou leaderless replication)

### Single-leader
há um líder e as alterações são replicadas aos seguidores
- definir o tipo de replicação
  - síncrona
  - assíncrona
- definir a estratégia de replicação
  - WAL
  - logical
  - logical (será usado essa para o nosso projeto)
- definir a estratégia para tratar os erros de replicação (replication lag)
  - reading your own writes: quem fez a escrita, consulta o database que armazenou essa escrita
  - Monotonic reads: garantir que as leituras feitas por um mesmo usuário sempre venha de uma mesma réplica -> é uma boa estratégia para o nosso caso, já que vamos fazer uma consulta de apenas um único computador
  - Consistent prefix reads


### Multi-leader
- definir a topologia de replicação
  - circular (anel)
  - all-to-all (estrela)

### Leaderless replication
Qualquer réplica aceita gravações


## Passo a passo

### Aumentar a robustez da camada de acesso ao banco de dados

Antes mesmo de usar as réplicas, iremos aumentar a robustes para acessar o banco de dados

`database.py` 

De:
```
engine = create_engine(DATABASE_URL)
```

Para:
```
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_pre_ping=True,
)
```

### Definição da arquitetura

Para definir a arquitetura, é preciso entender qual é o cenário de uso do banco de dados, a fim de criar a arquitetura mais eficiente para esse caso em específico.

Os critérios de avaliação são: qual é a natureza da aplicação e qual é o atual banco de dados utilizado, para assim definir a consistência, disponibilidade e desempenho necessários para ela. Com base nisso, define-se qual é o tipo de replicação (single-leader, multi-leader ou leader-less) e como ocorre a sincronização entre as réplicas (síncrona e assíncrona)


#### Natureza da aplicação
- A nossa aplicação é simples, pois usa leituras e escritas de produtos. Como se trata da escrita de produtos, é possível que esse sistema foi projetado para gerenciar o estoque, então é importante que não tenha muitas falhas no estoque.  
- Há apenas uma tabela no banco de dados (produtos)
- Apenas uma máquina vai realizar as operações de escrita/leitura


#### Banco de dados 

O Neon (database) já possui um sistema de réplicas, vindas do postgres, então, basicamente, iremos utilizar isso para o nosso trabalho. Para isso, usamos os conceitos abordados em aula, juntamente com a parte prática da configuração usando a documentação da ferramenta. 

Características da replicação do Neon:
- Replicação: Single-leader com logical replication. Há o nó publisher que recebe as operações de escrita, os subscribers recebem as operações do publisher e também processam as operações de leitura.

Referências
- https://neon.com/docs/guides/logical-replication-neon-to-neon
- https://neon.com/docs/guides/logical-replication-guide
- https://neon.com/docs/guides/logical-replication-concepts
- https://ead06.proj.ufsm.br/pluginfile.php/5530406/mod_resource/content/1/chap-5-replication.pdf
- Como criar as réplicas (detalhamento mais técnico): https://deepwiki.com/neondatabase/website/3.4-logical-replication 
- [Create and manage Read Replicas](https://neon.com/docs/guides/read-replica-guide)

#### Conclusão

- Será utilizado a arquitetura single-leader com 1 líder e 3 réplicas. O líder recebe as escritas e escreve nas réplicas, enquanto as réplicas apenas recebem leituras, sendo essas gerenciadas por um loadbalancer (com o algoritmo de roun-robin)
- As réplicas serão atualizadas de forma [assíncrona](https://neon.com/blog/introducing-same-region-read-replicas-to-serverless-postgres), usando o protocolo [logical replication](https://neon.com/docs/guides/logical-replication-neon).
- O servidor (backend (fastapi)) é stateless. 


