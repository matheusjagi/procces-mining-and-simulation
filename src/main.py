import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pm4py.objects.log.obj import EventLog, Trace, Event
from pm4py.algo.discovery.inductive import algorithm as inductive_miner
from pm4py.objects.conversion.process_tree import converter as pt_converter
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.objects.petri_net.exporter import exporter as pnml_exporter

#Importações da parte de simulação
from pm4py.algo.simulation.montecarlo import algorithm as montecarlo
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.algo.evaluation.replay_fitness import algorithm as replay_fitness

# 1. Ler o CSV
csv_path = "data\production_data.csv"
try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    raise FileNotFoundError(f"Arquivo '{csv_path}' não encontrado. Verifique o caminho do arquivo.")

# Verificar valores nulos em colunas críticas
if df[['Case ID', 'Activity', 'Start Timestamp']].isnull().any().any():
    raise ValueError("Valores nulos encontrados em 'Case ID', 'Activity' ou 'Start Timestamp'.")

# Converter timestamps
df['Start Timestamp'] = pd.to_datetime(df['Start Timestamp'])
df['Complete Timestamp'] = pd.to_datetime(df['Complete Timestamp'])

# Calcular duração em minutos a partir de Span (HH:MM)
def span_to_minutes(span):
    try:
        hours, minutes = map(int, span.split(':'))
        return hours * 60 + minutes
    except:
        return 0

df['Duration_Minutes'] = df['Span'].apply(span_to_minutes)

# Calcular tempos médios por atividade para usar na simulação
activity_durations = df.groupby('Activity')['Duration_Minutes'].mean().to_dict()

# Calcular a taxa média de rejeição do log original
total_rejected = df['Qty Rejected'].sum()
total_ordered = df['Work Order Qty'].sum()
rejection_rate_mean = total_rejected / total_ordered if total_ordered > 0 else 0
avg_qty_completed = df['Qty Completed'].mean() if not df['Qty Completed'].empty else 1

# Cria o Event Log a partir do CSV
log = EventLog()

# Agrupa por "Case ID" para formar cada "Trace"
for case_id, group in df.groupby("Case ID"):
    trace = Trace()
    trace.attributes['concept:name'] = str(case_id)  # Definir Case ID como atributo do trace
    # Ordenar por "Start Timestamp" para garantir a ordem correta dos eventos
    group_sorted = group.sort_values("Start Timestamp")

    for idx, row in group_sorted.iterrows():
        event = Event({
            'concept:name': row['Activity'],  # Nome da atividade
            'time:timestamp': row['Start Timestamp'],  # Timestamp
            'org:resource': row['Resource'],  # Recurso (máquina/qualidade)
            'duration': row['Duration_Minutes'],  # Duração em minutos
            'part_desc': row['Part Desc.'],  # Descrição da peça (opcional)
            'qty_completed': row['Qty Completed'],  # Quantidade completada
            'qty_rejected': row['Qty Rejected']  # Quantidade rejeitada
        })
        trace.append(event)
    log.append(trace)

# Aplicar o Inductive Miner
parameters = {
    'pm4py:param:noise_threshold': 0.15  # Ajustar para lidar com atividades raras -> Quanto maior o valor
}
tree = inductive_miner.apply(log, parameters=parameters)

# Converter a árvore para rede de Petri
net, initial_marking, final_marking = pt_converter.apply(tree)

# Visualizar o modelo
gviz = pn_visualizer.apply(net, initial_marking, final_marking)
pn_visualizer.save(gviz, "outcomes/petri_net_visualization.png")
pn_visualizer.view(gviz)
print("✅ Imagem salva e visalizada como 'petri_net_visualization.png' com sucesso!")

# Salvar a rede de Petri como arquivo .pnml
pnml_exporter.apply(net, initial_marking, "outcomes/petri_net_model.pnml", final_marking=final_marking)
print("✅ Rede de Petri salva como 'petri_net_model.pnml' com sucesso!")

print("✅ Processo minerado, convertido e visualizado com sucesso!")

# Análise de Caminhos Críticos
# Converter o log para um formato adequado para análise de caminhos críticos
# Aqui, simulamos um log maior para análise de tempos e inferimos os caminhos mais longos
critical_sim_log = montecarlo.apply(
    log, 
    net, 
    initial_marking, 
    final_marking,
    parameters={'no_traces': 1000, 'default_activity_duration': activity_durations}
)[0]

# Calcular tempos por trace e identificar os mais longos
trace_durations = []
for trace in critical_sim_log:
    timestamps = [event['time:timestamp'] for event in trace]
    if timestamps:
        duration = (max(timestamps) - min(timestamps)).total_seconds() / 60
        trace_durations.append((duration, [event['concept:name'] for event in trace]))

# Ordenar traces por duração e pegar os 5 mais longos
trace_durations.sort(reverse=True)
top_5_longest_paths = trace_durations[:5]

# Salvar os caminhos mais longos em um arquivo
with open("outcomes/critical_paths.txt", "w") as f:
    f.write("Caminhos Críticos (5 traces com maior duração):\n\n")
    for i, (duration, activities) in enumerate(top_5_longest_paths, 1):
        f.write(f"Trace {i}: Duração = {duration:.2f} minutos\n")
        f.write("Atividades: " + " -> ".join(activities) + "\n\n")
print("✅ Caminhos críticos salvos em 'critical_paths.txt' com sucesso!")

# Construção da Simulação Estocástica (Monte Carlo) através da Rede de Petri
# Definir parâmetros da simulação
num_simulations = 20  # Número de simulações Monte Carlo
num_traces_per_sim = 500  # Número de traces por simulação
sim_parameters = {
    'no_traces': num_traces_per_sim,
    'default_activity_duration': activity_durations
}

# Listas para armazenar métricas de todas as simulações
total_times = []
avg_activities_per_case = []
rejection_rates = []

# Função para calcular métricas de um log simulado
def calculate_metrics(sim_log):
    total_time_per_case = []
    num_activities_per_case = []
    total_rejected_sim = 0
    total_completed_sim = 0

    for trace in sim_log:
        # Tempo total do caso
        timestamps = [event['time:timestamp'] for event in trace]
        if timestamps:
            total_time = (max(timestamps) - min(timestamps)).total_seconds() / 60
            total_time_per_case.append(total_time)
            num_activities_per_case.append(len(trace))
        
        # Simular Qty Rejected estocasticamente
        for event in trace:
            qty_completed = max(1, int(np.random.normal(avg_qty_completed, avg_qty_completed * 0.2)))
            event['qty_completed'] = qty_completed
            
            rejection_rate_varied = max(0, np.random.normal(rejection_rate_mean, rejection_rate_mean * 0.5))
            qty_rejected = np.random.poisson(rejection_rate_varied * qty_completed)
            event['qty_rejected'] = qty_rejected
            
            total_rejected_sim += qty_rejected
            total_completed_sim += qty_completed
    
    # Calcular métricas
    avg_total_time = np.mean(total_time_per_case) if total_time_per_case else 0
    avg_activities = np.mean(num_activities_per_case) if num_activities_per_case else 0
    avg_rejection_rate = (total_rejected_sim / total_completed_sim * 100) if total_completed_sim > 0 else 0
    
    return avg_total_time, avg_activities, avg_rejection_rate

# Executar simulações Monte Carlo
for i in range(num_simulations):
    sim_log, sim_info = montecarlo.apply(
        log,  # O log original
        net,        # Rede de Petri
        initial_marking,   # Marcação inicial
        final_marking,     # Marcação final
        parameters=sim_parameters  # Parâmetros adicionais
    )

    if not sim_log:
        print(f"Simulação {i+1} gerou um log vazio. Pulando...")
        continue
    
    # Calcular métricas
    avg_total_time, avg_activities, rejection_rate = calculate_metrics(sim_log)
    
    # Armazenar métricas
    total_times.append(avg_total_time)
    avg_activities_per_case.append(avg_activities)
    rejection_rates.append(rejection_rate)
    
    # Opcional: Salvar log simulado individual
    xes_exporter.apply(sim_log, f"outcomes/simulations/simulated_log_run_{i+1}.xes")
    sim_df = log_converter.apply(sim_log, variant=log_converter.Variants.TO_DATA_FRAME)
    sim_df.to_csv(f"outcomes/simulations/simulated_log_run_{i+1}.csv", index=False)

# 7. Aggregar e analisar resultados
results_df = pd.DataFrame({
    'Simulation': range(1, num_simulations + 1),
    'Avg_Total_Time_Minutes': total_times,
    'Avg_Activities_Per_Case': avg_activities_per_case,
    'Rejection_Rate_%': rejection_rates
})

# Estatísticas resumidas
summary = results_df.describe()
print("\n✅ Resumo das Simulações Monte Carlo:")
print(summary)

# Salvar resultados
results_df.to_csv("outcomes/monte_carlo_results.csv", index=False)
print("✅ Resultados salvos em 'monte_carlo_results.csv'.")

# 8. Visualização
plt.figure(figsize=(18, 6))

# Histograma do tempo total médio
plt.subplot(1, 3, 1)
plt.hist(total_times, bins=20, color='blue', alpha=0.7)
plt.title('Distribuição do Tempo Total Médio por Caso (Minutos)')
plt.xlabel('Tempo Médio (Minutos)')
plt.ylabel('Frequência')

# Histograma do número médio de atividades
plt.subplot(1, 3, 2)
plt.hist(avg_activities_per_case, bins=20, color='green', alpha=0.7)
plt.title('Distribuição do Número Médio de Atividades por Caso')
plt.xlabel('Número Médio de Atividades')
plt.ylabel('Frequência')

# Gráfico de dispersão (Scatter Plot)
plt.subplot(1, 3, 3)
plt.scatter(avg_activities_per_case, total_times, color='purple', alpha=0.5)
plt.title('Tempo Total Médio vs. Número Médio de Atividades')
plt.xlabel('Número Médio de Atividades')
plt.ylabel('Tempo Total Médio (Minutos)')

plt.tight_layout()
plt.savefig("outcomes/monte_carlo_visualizations.png")
plt.show()
print("✅ Visualizações salvas em 'monte_carlo_visualizations.png'.")

# Avaliar Fitness do Modelo
fitness = replay_fitness.apply(log, net, initial_marking, final_marking, variant=replay_fitness.Variants.TOKEN_BASED)
print(f"✅ Fitness do modelo: {fitness['average_trace_fitness']:.2f}")