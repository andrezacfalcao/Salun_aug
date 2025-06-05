# Execução de Experimentos em Lote

Este diretório contém ferramentas para executar múltiplos experimentos em lote e registrar seus resultados automaticamente.

## Como Usar

### 1. Configurar o arquivo de comandos

Crie um arquivo de texto (por padrão `commands.txt`) contendo os comandos que deseja executar, um por linha:

```
# Linhas que começam com # são ignoradas (comentários)
python main_train.py --dataset cifar10 --seed 1 --save-dir ./results/exp1 --gpu 0
python main_forget.py --dataset cifar10 --seed 2 --model-path ./path/to/model.pth --save-dir ./results/exp2 --gpu 0
```

### 2. Executar o script de lote

```bash
python run_experiments.py --input commands.txt --output resultados.txt
```

Parâmetros opcionais:
- `--input`: Caminho para o arquivo com os comandos (padrão: `commands.txt`)
- `--output`: Caminho para o arquivo onde serão salvos os resultados (padrão: `results.txt`)

### 3. Verificar resultados

O arquivo de saída conterá:
- Hora de início da execução
- Cada comando executado com sua saída completa
- Tempo de execução de cada comando
- Hora de término e tempo total de execução

## Exemplo de Saída

```
=== EXECUÇÃO INICIADA EM 2023-08-10 15:30:25 ===
Total de comandos a executar: 2

[1/2] COMANDO: python main_train.py --dataset cifar10 --seed 1 --save-dir ./results/exp1 --gpu 0
--------------------------------------------------------------------------------
Início: 2023-08-10 15:30:25

... [saída do comando] ...

SUCESSO - Comando concluído em 120.45 segundos

================================================================================

[2/2] COMANDO: python main_forget.py --dataset cifar10 --seed 2 --model-path ./path/to/model.pth --save-dir ./results/exp2 --gpu 0
--------------------------------------------------------------------------------
Início: 2023-08-10 15:32:26

... [saída do comando] ...

SUCESSO - Comando concluído em 85.32 segundos

================================================================================

=== EXECUÇÃO FINALIZADA EM 2023-08-10 15:33:51 ===
Tempo total de execução: 206.77 segundos (3.45 minutos)
Total de comandos executados: 2
```

## Dicas

1. Use caminhos absolutos nos comandos para evitar problemas de diretório.
2. Você pode organizar os resultados em diferentes diretórios usando parâmetros como `--save-dir`.
3. Para executar experimentos longos, considere usar uma sessão de terminal persistente (como `screen` ou `tmux`). 