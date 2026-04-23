.. Assistente de Lances documentation master file, created by
   sphinx-quickstart on Tue Apr 21 23:28:00 2026.

Bem-vindo à documentação do Assistente de Lances!
=================================================

.. toctree::
   :maxdepth: 2
   :caption: Conteúdo:

Módulo Principal
----------------
.. automodule:: src.main
   :members:

Análise de Eficiência Algorítmica (Big O)
========================================

O sistema foi projetado priorizando a economia de recursos computacionais, especialmente em páginas com estruturas DOM (Document Object Model) densas. Abaixo, detalhamos a complexidade de tempo das principais rotinas:

1. Processamento de Texto e Conversão de Preços
----------------------------------------------
* **Função:** ``validators.parse_price``
* **Complexidade:** :math:`O(n)`, onde :math:`n` é o comprimento da string.
* **Justificativa:** A função utiliza expressões regulares para identificar padrões numéricos. Como o motor de busca de regex percorre a string linearmente para encontrar correspondências, o custo aumenta de forma proporcional ao tamanho do texto capturado.

2. Descoberta Automática de Elementos
------------------------------------
* **Função:** ``AuctionMonitor.discover_price_elements``
* **Complexidade:** :math:`O(E)`, onde :math:`E` é o número total de elementos no DOM.
* **Justificativa:** O algoritmo realiza uma varredura completa na árvore de elementos da página para aplicar o sistema de pontuação (scoring). Cada elemento é avaliado individualmente, resultando em uma execução linear em relação ao tamanho da página.

3. Ciclo de Monitoramento Contínuo
----------------------------------
* **Função:** ``AuctionMonitor.start`` (por iteração)
* **Complexidade:** :math:`O(D)`, onde :math:`D` representa a profundidade ou complexidade do seletor XPath.
* **Justificativa:** Em cada ciclo de verificação, o navegador realiza uma busca direcionada. Ao utilizar XPaths otimizados ou IDs, essa busca é extremamente eficiente, aproximando-se de um custo constante, independentemente do tempo total de execução do programa.

Monitoramento
-------------
.. automodule:: src.monitor
   :members:

Validações
----------
.. automodule:: src.validators
   :members:

Notificação
-----------
.. automodule:: src.notifier
   :members:

Logs
----
.. automodule:: src.logger
   :members:

Índices e Tabelas
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
