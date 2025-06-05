import subprocess
import os
import time
import argparse
import datetime

def main():
    parser = argparse.ArgumentParser(description='Executa vários comandos de um arquivo texto e salva os resultados')
    parser.add_argument('--input', type=str, default='commands.txt', help='Arquivo com os comandos para executar')
    parser.add_argument('--output', type=str, default='results.txt', help='Arquivo para salvar os resultados')
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
        commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Abrir o arquivo de resultados
    with open(args.output, 'w') as results_file:
        # Escrever cabeçalho
        start_time = time.time()
        start_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        header = f"=== EXECUÇÃO INICIADA EM {start_datetime} ===\n"
        results_file.write(header)
        results_file.write(f"Total de comandos a executar: {len(commands)}\n\n")
        
        # Executar cada comando e salvar o resultado
        for i, cmd in enumerate(commands):
            results_file.write(f"[{i+1}/{len(commands)}] COMANDO: {cmd}\n")
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
Tempo total de execução: {total_duration:.2f} segundos ({total_duration/60:.2f} minutos)
Total de comandos executados: {len(commands)}
"""
        results_file.write(footer)

if __name__ == "__main__":
    main() 