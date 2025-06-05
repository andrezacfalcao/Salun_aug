import subprocess
import os
import time
import argparse
import datetime
import json

def extract_save_dir(cmd):
    """Extrai o diretório de salvamento do comando"""
    parts = cmd.split('--save_dir')
    if len(parts) > 1:
        save_dir = parts[1].split()[0].strip()
        return save_dir
    return None

def check_experiment_success(save_dir):
    """Verifica se o experimento foi concluído com sucesso"""
    if not save_dir or not os.path.exists(save_dir):
        return False
        
    # Verifica se o arquivo results.txt existe e contém as métricas necessárias
    results_file = os.path.join(save_dir, "results.txt")
    if not os.path.exists(results_file):
        return False
        
    try:
        with open(results_file, 'r') as f:
            content = f.read()
            # Verifica se todas as métricas importantes estão presentes
            required_metrics = ["UA", "RA", "TA", "MIA"]
            return all(metric in content for metric in required_metrics)
    except:
        return False
    
    return False

def save_progress(progress_file, completed_experiments):
    """Salva o progresso dos experimentos"""
    with open(progress_file, 'w') as f:
        json.dump(completed_experiments, f)

def load_progress(progress_file):
    """Carrega o progresso dos experimentos"""
    if os.path.exists(progress_file):
        try:
            with open(progress_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

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
    
    # Arquivo para armazenar o progresso
    progress_file = args.input + '.progress'
    completed_experiments = load_progress(progress_file)
    
    # Ler os comandos do arquivo de entrada
    with open(args.input, 'r') as f:
        commands = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    # Modo de escrita depende se já existe arquivo de resultados
    mode = 'a' if os.path.exists(args.output) else 'w'
    
    with open(args.output, mode) as results_file:
        # Escrever cabeçalho se estiver iniciando do começo
        if mode == 'w':
            start_time = time.time()
            start_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            header = f"=== EXECUÇÃO INICIADA EM {start_datetime} ===\n"
            results_file.write(header)
            results_file.write(f"Total de comandos a executar: {len(commands)}\n\n")
        else:
            results_file.write("\n\n=== CONTINUANDO EXECUÇÃO ===\n\n")
        
        # Executar cada comando e salvar o resultado
        for i, cmd in enumerate(commands):
            save_dir = extract_save_dir(cmd)
            
            # Verifica se o experimento já foi concluído com sucesso
            if save_dir in completed_experiments and completed_experiments[save_dir]:
                results_file.write(f"[{i+1}/{len(commands)}] COMANDO: {cmd}\n")
                results_file.write("-" * 80 + "\n")
                results_file.write("PULANDO - Experimento já concluído com sucesso anteriormente\n")
                results_file.write("=" * 80 + "\n\n")
                results_file.flush()
                continue
                
            results_file.write(f"[{i+1}/{len(commands)}] COMANDO: {cmd}\n")
            results_file.write("-" * 80 + "\n")
            
            # Registrar tempo de início do comando
            cmd_start = time.time()
            cmd_start_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            results_file.write(f"Início: {cmd_start_str}\n\n")
            results_file.flush()
            
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
                success = False
                if return_code == 0:
                    # Verifica se o experimento foi realmente concluído com sucesso
                    if save_dir and check_experiment_success(save_dir):
                        results_file.write(f"SUCESSO - Comando concluído em {cmd_duration:.2f} segundos\n")
                        success = True
                    else:
                        results_file.write(f"ERRO - Experimento não gerou resultados válidos após {cmd_duration:.2f} segundos\n")
                else:
                    results_file.write(f"ERRO (código {return_code}) - Comando falhou após {cmd_duration:.2f} segundos\n")
                
                # Atualizar e salvar o progresso
                if save_dir:
                    completed_experiments[save_dir] = success
                    save_progress(progress_file, completed_experiments)
                
            except Exception as e:
                results_file.write(f"\nERRO AO EXECUTAR: {str(e)}\n")
                if save_dir:
                    completed_experiments[save_dir] = False
                    save_progress(progress_file, completed_experiments)
            
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