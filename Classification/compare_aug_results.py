import os
import re
import argparse
import csv
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from extract_metrics import extract_metrics_from_file

def extract_augmentation_type(command):
    """Extrai o tipo de augmentation do comando ou diretório de salvamento"""
    # Primeiro tenta extrair do --aug_mode
    aug_mode_match = re.search(r'--aug_mode\s+(\S+)', command)
    if aug_mode_match:
        aug_mode = aug_mode_match.group(1)
        if aug_mode == 'noaug':
            return 'No Augmentation'
        elif 'crop-flip-autoaug' in aug_mode:
            return 'AutoAugment'
        elif 'crop-flip-rerase' in aug_mode:
            return 'Random Erasing'
        elif 'crop-flip-augmix' in aug_mode:
            return 'AugMix'
        elif 'crop-flip-triviaug' in aug_mode:
            return 'TrivialAugment'
        elif 'crop-flip-randaug' in aug_mode:
            return 'RandAugment'
        else:
            return aug_mode.capitalize()
    
    # Se não encontrar no aug_mode, tenta extrair do diretório de salvamento
    save_dir_match = re.search(r'--save_dir\s+([^\s]+)', command)
    if save_dir_match:
        save_dir = save_dir_match.group(1)
        if 'noaug' in save_dir:
            return 'No Augmentation'
        elif 'autoaug' in save_dir:
            return 'AutoAugment'
        elif 'rerase' in save_dir:
            return 'Random Erasing'
        elif 'augmix' in save_dir:
            return 'AugMix'
        elif 'triviaug' in save_dir:
            return 'TrivialAugment'
        elif 'randaug' in save_dir:
            return 'RandAugment'
        elif 'df' in save_dir:
            return 'Default (RandomCrop+Flip)'
    
    return 'Unknown'

def create_comparison_table(all_metrics):
    """Cria uma tabela comparativa a partir das métricas extraídas"""
    comparison = []
    
    for metrics in all_metrics:
        aug_type = extract_augmentation_type(metrics.get('command', ''))
        
        entry = {
            'Augmentation': aug_type,
            'UA (%)': metrics.get('ua', ''),
            'RA (%)': metrics.get('ra', ''),
            'TA (%)': metrics.get('ta', ''),
            'MIA (%)': metrics.get('mia', ''),
            'RTE (s)': metrics.get('total_rte', ''),
            'Epoch RTE (s)': metrics.get('sum_epoch_rte', '')
        }
        comparison.append(entry)
    
    # Ordenar por tipo de augmentation
    comparison.sort(key=lambda x: x['Augmentation'])
    
    return comparison

def plot_metrics(comparison, output_dir):
    """Cria gráficos comparativos das métricas"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Converter para DataFrame para facilitar a manipulação
    df = pd.DataFrame(comparison)
    
    # Gráfico de barras para métricas de acurácia
    plt.figure(figsize=(12, 6))
    
    # Agrupar barras por tipo de augmentation
    x = np.arange(len(df['Augmentation']))
    width = 0.2
    
    plt.bar(x - width*1.5, df['UA (%)'], width, label='UA (%)', color='#ff9999')
    plt.bar(x - width/2, df['RA (%)'], width, label='RA (%)', color='#66b3ff')
    plt.bar(x + width/2, df['TA (%)'], width, label='TA (%)', color='#99ff99')
    plt.bar(x + width*1.5, df['MIA (%)'], width, label='MIA (%)', color='#ffcc99')
    
    plt.xlabel('Augmentation Method')
    plt.ylabel('Percentage (%)')
    plt.title('Performance Metrics by Augmentation Method')
    plt.xticks(x, df['Augmentation'], rotation=45, ha='right')
    plt.legend()
    plt.tight_layout()
    plt.grid(axis='y', alpha=0.3)
    
    # Adicionar valores nas barras
    for i, v in enumerate(df['UA (%)']):
        plt.text(i - width*1.5, v + 0.5, f'{v:.1f}', ha='center', fontsize=8)
    for i, v in enumerate(df['RA (%)']):
        plt.text(i - width/2, v + 0.5, f'{v:.1f}', ha='center', fontsize=8)
    for i, v in enumerate(df['TA (%)']):
        plt.text(i + width/2, v + 0.5, f'{v:.1f}', ha='center', fontsize=8)
    for i, v in enumerate(df['MIA (%)']):
        plt.text(i + width*1.5, v + 0.5, f'{v:.1f}', ha='center', fontsize=8)
    
    plt.savefig(os.path.join(output_dir, 'accuracy_metrics.png'), dpi=300)
    plt.close()
    
    # Gráfico para tempo de execução
    plt.figure(figsize=(10, 6))
    plt.bar(df['Augmentation'], df['RTE (s)'], color='#9999ff')
    plt.xlabel('Augmentation Method')
    plt.ylabel('Runtime (seconds)')
    plt.title('Total Runtime by Augmentation Method')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.grid(axis='y', alpha=0.3)
    
    # Adicionar valores nas barras
    for i, v in enumerate(df['RTE (s)']):
        plt.text(i, v + 5, f'{v:.1f}s', ha='center')
    
    plt.savefig(os.path.join(output_dir, 'runtime.png'), dpi=300)
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Compara resultados dos experimentos de augmentation')
    parser.add_argument('--input', type=str, default='resultados_aug.txt', help='Arquivo de resultados ou diretório contendo resultados')
    parser.add_argument('--output', type=str, default='aug_comparison.csv', help='Arquivo CSV para salvar o resumo das métricas')
    parser.add_argument('--plots-dir', type=str, default='plots', help='Diretório para salvar os gráficos')
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
    
    # Criar tabela comparativa
    comparison = create_comparison_table(all_metrics)
    
    # Escrever para CSV
    with open(args.output, 'w', newline='') as csvfile:
        fieldnames = ['Augmentation', 'UA (%)', 'RA (%)', 'TA (%)', 'MIA (%)', 'RTE (s)', 'Epoch RTE (s)']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in comparison:
            writer.writerow(row)
    
    print(f"Comparação salva em: {args.output}")
    
    # Criar gráficos
    plot_metrics(comparison, args.plots_dir)
    print(f"Gráficos salvos em: {args.plots_dir}")
    
    # Mostrar tabela resumida no console
    print("\n=== RESUMO DOS RESULTADOS ===")
    print(f"{'Augmentation':<20} {'UA (%)':<10} {'RA (%)':<10} {'TA (%)':<10} {'MIA (%)':<10} {'RTE (s)':<10}")
    print("-" * 70)
    for row in comparison:
        print(f"{row['Augmentation']:<20} {row['UA (%)']:<10.2f} {row['RA (%)']:<10.2f} {row['TA (%)']:<10.2f} {row['MIA (%)']:<10.2f} {row['RTE (s)']:<10.2f}")

if __name__ == "__main__":
    main() 