import subprocess
import os
import time
import argparse
import datetime

def main():
    parser = argparse.ArgumentParser(description='Executa experimentos de augmentation em sequência')
    parser.add_argument('--input', type=str, default='aug_commands.txt', help='Arquivo com os comandos para executar')
    parser.add_argument('--output', type=str, default='resultados_aug.txt', help='Arquivo para salvar os resultados')
    parser.add_argument('--start-from', type=int, default=1, help='Índice do experimento para começar (1-based)')
    parser.add_argument('--end-at', type=int, default=None, help='Índice do experimento para terminar (1-based, inclusivo)')
    parser.add_argument('--gpu', type=str, default=None, help='Sobrescrever GPU para todos os comandos (ex: --gpu 0)')
    args = parser.parse_args()
    
    # Verificar se o arquivo de entrada existe
    if not os.path.exists(args.input):
        print(f"Erro: Arquivo de entrada '{args.input}' não encontrado!")
        return
    
    # Criar diretório para o arquivo de saída se não existir
    output_dir = os.path.dirname(args.output)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Ler os comandos do arquivo de entrada
    with open(args.input, 'r') as f:
        all_lines = f.readlines()
        # Filtrar comentários e linhas vazias
        commands = [line.strip() for line in all_lines if line.strip() and not line.strip().startswith('#')]
    
    # Verificar se o índice de início é válido
    if args.start_from < 1 or args.start_from > len(commands):
        print(f"Erro: O índice de início deve estar entre 1 e {len(commands)}")
        return
    
    # Verificar se o índice de fim é válido
    end_at = args.end_at if args.end_at is not None else len(commands)
    if end_at < args.start_from or end_at > len(commands):
        print(f"Erro: O índice de fim deve estar entre {args.start_from} e {len(commands)}")
        return
    
    # Substituir GPU se especificado
    if args.gpu is not None:
        print(f"Substituindo GPU para todos os comandos: --gpu {args.gpu}")
        for i in range(len(commands)):
            # Remover --gpu existente
            if '--gpu' in commands[i]:
                parts = commands[i].split('--gpu')
                before_gpu = parts[0]
                after_gpu = parts[1]
                # Remover o valor após --gpu
                after_gpu = ' '.join(after_gpu.split()[1:])
                commands[i] = before_gpu + '--gpu ' + args.gpu + ' ' + after_gpu
            else:
                commands[i] = commands[i] + f" --gpu {args.gpu}"
    
    # Pegar apenas os comandos do intervalo especificado
    commands_to_run = commands[args.start_from - 1:end_at]
    
    # Abrir ou criar o arquivo de resultados
    mode = 'a' if os.path.exists(args.output) and args.start_from > 1 else 'w'
    with open(args.output, mode) as results_file:
        # Escrever cabeçalho se estiver iniciando do começo
        if mode == 'w':
            start_time = time.time()
            start_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header = f"=== EXECUÇÃO INICIADA EM {start_datetime} ===\n"
            results_file.write(header)
            results_file.write(f"Total de comandos a executar: {len(commands_to_run)}\n")
            results_file.write(f"Executando experimentos de #{args.start_from} até #{end_at} de {len(commands)}\n\n")
        else:
            # Adicionar uma marca de continuação
            results_file.write("\n\n")
            start_time = time.time()
            start_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header = f"=== CONTINUANDO EXECUÇÃO EM {start_datetime} ===\n"
            results_file.write(header)
            results_file.write(f"Continuando com experimentos de #{args.start_from} até #{end_at} de {len(commands)}\n")
            results_file.write(f"Restam {len(commands_to_run)} comandos para executar\n\n")
        
        # Executar cada comando e salvar o resultado
        for i, cmd in enumerate(commands_to_run):
            overall_index = i + args.start_from
            results_file.write(f"[{overall_index}/{len(commands)}] COMANDO: {cmd}\n")
            results_file.write("-" * 80 + "\n")
            
            # Registrar tempo de início do comando
            cmd_start = time.time()
            cmd_start_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results_file.write(f"Início: {cmd_start_str}\n\n")
            results_file.flush()  # Forçar escrita no arquivo
            
            try:
                # Executar o comando e capturar a saída
                process = subprocess.Popen(
                    cmd, 
                    shell=True, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.STDOUT,
                    universal_newlines=True
                )
                
                # Capturar a saída em tempo real e escrevê-la no arquivo
                output = []
                for line in process.stdout:
                    print(line, end='')  # Mostrar no console
                    output.append(line)
                    results_file.write(line)
                    results_file.flush()  # Atualizar o arquivo em tempo real
                
                # Aguardar o término do processo
                return_code = process.wait()
                
                # Registrar tempo de fim do comando
                cmd_end = time.time()
                cmd_duration = cmd_end - cmd_start
                
                # Adicionar informações sobre o resultado
                results_file.write("\n")
                if return_code == 0:
                    results_file.write(f"SUCESSO - Comando concluído em {cmd_duration:.2f} segundos\n")
                else:
                    results_file.write(f"ERRO (código {return_code}) - Comando falhou após {cmd_duration:.2f} segundos\n")
                
            except Exception as e:
                results_file.write(f"\nERRO AO EXECUTAR: {str(e)}\n")
            
            results_file.write("\n" + "=" * 80 + "\n\n")
            results_file.flush()
        
        # Finalizar o arquivo com o tempo total de execução
        end_time = time.time()
        total_duration = end_time - start_time
        end_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        footer = f"""
=== EXECUÇÃO FINALIZADA EM {end_datetime} ===
Tempo total desta sessão: {total_duration:.2f} segundos ({total_duration/60:.2f} minutos)
Total de comandos executados nesta sessão: {len(commands_to_run)}
"""
        results_file.write(footer)

if __name__ == "__main__":
    main() 