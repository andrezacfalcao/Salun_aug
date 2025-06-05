import os
import re
import argparse
import csv


def extract_metrics_from_file(file_path):
    """Extrai métricas importantes de um arquivo de resultado."""
    metrics = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
            # Extrair nome do comando
            command_match = re.search(r'\[.*?\] COMANDO: (.*?)$', content, re.MULTILINE)
            if command_match:
                metrics['command'] = command_match.group(1).strip()
            
            # Extrair Total RTE
            rte_match = re.search(r'Total RTE \(Runtime Execution\): ([\d.]+)', content)
            if rte_match:
                metrics['total_rte'] = float(rte_match.group(1))
            
            # Extrair Sum of epoch RTE
            sum_rte_match = re.search(r'Sum of epoch RTE: ([\d.]+)', content)
            if sum_rte_match:
                metrics['sum_epoch_rte'] = float(sum_rte_match.group(1))
            
            # Extrair Unlearning Accuracy (UA)
            ua_match = re.search(r'UA \(Unlearning Accuracy\): ([\d.]+)', content)
            if ua_match:
                metrics['ua'] = float(ua_match.group(1))
            
            # Extrair Remaining Accuracy (RA)
            ra_match = re.search(r'RA \(Remaining Accuracy\): ([\d.]+)', content)
            if ra_match:
                metrics['ra'] = float(ra_match.group(1))
            
            # Extrair Testing Accuracy (TA)
            ta_match = re.search(r'TA \(Testing Accuracy\): ([\d.]+)', content)
            if ta_match:
                metrics['ta'] = float(ta_match.group(1))
            
            # Extrair MIA
            mia_match = re.search(r'MIA \(Membership Inference Attack\): ([\d.]+)', content)
            if mia_match:
                metrics['mia'] = float(mia_match.group(1))
            
            # Tempo total de execução do comando
            cmd_time_match = re.search(r'Comando concluído em ([\d.]+) segundos', content)
            if cmd_time_match:
                metrics['command_time'] = float(cmd_time_match.group(1))
                
            # Status de conclusão
            if "SUCESSO" in content:
                metrics['status'] = "SUCESSO"
            elif "ERRO" in content:
                metrics['status'] = "ERRO"
            else:
                metrics['status'] = "DESCONHECIDO"
            
    except Exception as e:
        print(f"Erro ao processar {file_path}: {str(e)}")
        metrics['status'] = f"ERRO_LEITURA: {str(e)}"
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description='Extrai métricas importantes de arquivos de resultados')
    parser.add_argument('--input', type=str, help='Arquivo de resultados ou diretório contendo resultados')
    parser.add_argument('--output', type=str, default='metrics_summary.csv', help='Arquivo CSV para salvar o resumo das métricas')
    args = parser.parse_args()
    
    # Verificar se a entrada é um arquivo ou diretório
    if os.path.isfile(args.input):
        files_to_process = [args.input]
    elif os.path.isdir(args.input):
        files_to_process = [os.path.join(args.input, f) for f in os.listdir(args.input) 
                           if os.path.isfile(os.path.join(args.input, f)) and f.endswith('.txt')]
    else:
        print(f"Erro: A entrada '{args.input}' não é um arquivo nem um diretório válido!")
        return
    
    # Processar todos os arquivos
    all_metrics = []
    for file_path in files_to_process:
        print(f"Processando: {file_path}")
        metrics = extract_metrics_from_file(file_path)
        metrics['file'] = os.path.basename(file_path)
        all_metrics.append(metrics)
    
    # Determinar todas as colunas possíveis
    all_columns = set()
    for metrics in all_metrics:
        all_columns.update(metrics.keys())
    
    # Ordenar colunas para garantir consistência
    columns = ['file', 'command', 'status', 'total_rte', 'sum_epoch_rte', 'command_time', 
              'ua', 'ra', 'ta', 'mia']
    # Adicionar quaisquer colunas extras que podem ter sido encontradas
    columns.extend(sorted([c for c in all_columns if c not in columns]))
    
    # Escrever para CSV
    with open(args.output, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        for metrics in all_metrics:
            # Garantir que todas as colunas estejam presentes
            row = {column: metrics.get(column, '') for column in columns}
            writer.writerow(row)
    
    print(f"Resumo de métricas salvo em: {args.output}")
    print(f"Total de {len(all_metrics)} arquivos processados.")


if __name__ == "__main__":
    main() 