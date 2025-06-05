# Guia para Experimentos de Augmentation

Este guia explica como usar os scripts para executar e analisar experimentos com diferentes técnicas de data augmentation.

## 1. Estrutura dos Experimentos

Os experimentos estão organizados em três grupos principais no arquivo `all_experiments.txt`:

### Grupo 1: Experimentos com main_forget.py (Retrain)
- Default (RandomCrop+Flip) - Experimento #1
- No Augmentation - Experimento #2
- AutoAugment - Experimento #3
- Random Erasing - Experimento #4
- AugMix - Experimento #5
- TrivialAugment - Experimento #6
- RandAugment - Experimento #7

### Grupo 2: Experimentos com generate_mask.py
- Default (RandomCrop+Flip) - Experimento #8
- No Augmentation - Experimento #9
- AutoAugment - Experimento #10
- Random Erasing - Experimento #11
- AugMix - Experimento #12
- TrivialAugment - Experimento #13
- RandAugment - Experimento #14

### Grupo 3: Experimentos com main_random.py (RL)
- Default (RandomCrop+Flip) - Experimento #15
- No Augmentation - Experimento #16
- AutoAugment - Experimento #17
- Random Erasing - Experimento #18
- AugMix - Experimento #19
- TrivialAugment - Experimento #20
- RandAugment - Experimento #21

## 2. Executando os Experimentos

### Executar todos os experimentos em sequência

```bash
python run_aug_experiments.py --input all_experiments.txt --output resultados_todos.txt
```

### Executar um grupo específico de experimentos

#### Grupo 1 (Retrain)
```bash
python run_aug_experiments.py --input all_experiments.txt --output resultados_retrain.txt --start-from 1 --end-at 7
```

#### Grupo 2 (Generate Mask)
```bash
python run_aug_experiments.py --input all_experiments.txt --output resultados_masks.txt --start-from 8 --end-at 14
```

#### Grupo 3 (RL)
```bash
python run_aug_experiments.py --input all_experiments.txt --output resultados_rl.txt --start-from 15 --end-at 21
```

### Continuar de um experimento específico (caso um falhe ou você precise interromper)

```bash
python run_aug_experiments.py --input all_experiments.txt --output resultados_aug.txt --start-from 3
```

### Sobrescrever a GPU para todos os experimentos

```bash
python run_aug_experiments.py --input all_experiments.txt --output resultados_aug.txt --gpu 0
```

## 3. Analisando os Resultados

Depois que os experimentos terminarem, você pode extrair e comparar os resultados:

```bash
python compare_aug_results.py --input resultados_todos.txt --output comparacao_aug.csv --plots-dir plots_aug
```

Você também pode analisar cada grupo separadamente:

```bash
python compare_aug_results.py --input resultados_retrain.txt --output comparacao_retrain.csv --plots-dir plots_retrain
python compare_aug_results.py --input resultados_masks.txt --output comparacao_masks.csv --plots-dir plots_masks
python compare_aug_results.py --input resultados_rl.txt --output comparacao_rl.csv --plots-dir plots_rl
```

Isso irá:
1. Extrair as métricas importantes (UA, RA, TA, MIA, RTE) de cada experimento
2. Criar um arquivo CSV com a comparação
3. Gerar gráficos comparativos na pasta especificada
4. Mostrar um resumo no console

## 4. Métricas Analisadas

- **UA (Unlearning Accuracy)**: Percentual de dados "esquecidos" pelo modelo
- **RA (Remaining Accuracy)**: Acurácia nos dados retidos
- **TA (Testing Accuracy)**: Acurácia no conjunto de teste
- **MIA (Membership Inference Attack)**: Resistência a ataques de inferência de associação
- **RTE (Runtime Execution)**: Tempo total de execução

## 5. Arquivos Gerados

- `resultados_*.txt`: Resultado detalhado dos experimentos
- `comparacao_*.csv`: Tabelas comparativas com as métricas principais
- `plots_*/accuracy_metrics.png`: Gráficos de barras comparando UA, RA, TA e MIA
- `plots_*/runtime.png`: Gráficos de barras comparando tempos de execução

## Dicas

1. Se você precisar interromper a execução, use Ctrl+C e depois continue com a opção `--start-from`
2. Para executar apenas um experimento específico, use `--start-from X --end-at X` com o mesmo valor
3. Verifique os caminhos dos modelos em `all_experiments.txt` antes de executar
4. Se quiser adicionar mais experimentos, basta acrescentá-los ao arquivo `all_experiments.txt`
5. Use arquivos de saída diferentes para cada grupo para facilitar a análise posterior 