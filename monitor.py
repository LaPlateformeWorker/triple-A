import psutil
import platform
import socket
import time
import datetime
import os
from flask import Flask, render_template_string, render_template

app = Flask(__name__) 

TEMPLATE_FILE = 'template.html'
OUTPUT_FILE = 'index.html'
MONITOR_DIR = os.path.expanduser('~')

# FONCTIONS UTILITAIRES 
def bytes_to_gb(bytes_value):
    return round(bytes_value / (1024**3), 2)

def color_level(percent):
    if percent <= 50:
        return "green"
    elif percent <= 80:
        return "orange"
    else:
        return "red"

# FONCTIONS DE COLLECTE DES DONNÉES 

def collect_data():

    # 1. Infos Système et Réseau

    boot_time_timestamp = psutil.boot_time()
    bt = datetime.datetime.fromtimestamp(boot_time_timestamp)
    uptime_seconds = time.time() - boot_time_timestamp
    uptime_str = str(datetime.timedelta(seconds=int(uptime_seconds)))
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
    except Exception:
        ip_address = "N/A"
        
    load_avg = [round(x / psutil.cpu_count() * 100, 2) for x in psutil.getloadavg()] if platform.system() == "Linux" else ["N/A"] * 3
    
    context = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "system_hostname": socket.gethostname(),
        "system_os": f"{platform.system()} {platform.release()}",
        "system_boot_time": bt.strftime("%Y-%m-%d %H:%M:%S"),
        "system_uptime": uptime_str,
        "system_user_count": len(psutil.users()),
        "network_ip_address": ip_address,
        "load_average_1m": load_avg[0] if len(load_avg) >= 1 else "N/A",
        "load_average_5m": load_avg[1] if len(load_avg) >= 2 else "N/A",
        "load_average_15m": load_avg[2] if len(load_avg) >= 3 else "N/A",
    }
    
    # 2. Infos CPU
    cpu_percent_usage = psutil.cpu_percent(interval=1)
    cpu_per_core = psutil.cpu_percent(interval=None, percpu=True)
    cpu_freq = psutil.cpu_freq()
    
    core_usage_list = ""
    for i, percent in enumerate(cpu_per_core):
        color = color_level(percent)
        core_usage_list += f'<p>Coeur {i}: <span role="progressbar" aria-valuenow="{percent}" aria-valuemin="0" aria-valuemax="100" aria-label="Utilisation Coeur {i}" class="usage-level-{color}">{percent}%</span></p>'

    context.update({
        "cpu_core_count": psutil.cpu_count(logical=True),
        "cpu_current_freq": round(cpu_freq.current, 2) if cpu_freq else "N/A",
        "cpu_percent_usage": cpu_percent_usage,
        "cpu_usage_color": color_level(cpu_percent_usage),
        "cpu_core_usage_list": core_usage_list,
    })

    # 3. Infos Mémoire
    mem = psutil.virtual_memory()
    mem_percent = mem.percent
    context.update({
        "ram_total_gb": bytes_to_gb(mem.total),
        "ram_used_gb": bytes_to_gb(mem.used),
        "ram_percent_usage": mem_percent,
        "ram_usage_color": color_level(mem_percent),
    })

    # 4. Top 3 
    process_list = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            cpu_percent = round(proc.info['cpu_percent'], 1)
            mem_percent = round(proc.info['memory_percent'], 1)
            if cpu_percent > 0.0 or mem_percent > 0.0:
                process_list.append({"pid": proc.info['pid'], "name": proc.info['name'], "cpu": cpu_percent, "ram": mem_percent})
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    sorted_processes = sorted(process_list, key=lambda x: (x['cpu'], x['ram']), reverse=True)
    top_process_rows = ""
    for p in sorted_processes[:3]:
        cpu_color = color_level(p['cpu'])
        ram_color = color_level(p['ram'])
        top_process_rows += f'<tr><td>{p["pid"]}</td><td>{p["name"]}</td><td class="usage-level-{cpu_color}">{p["cpu"]}%</td><td class="usage-level-{ram_color}">{p["ram"]}%</td></tr>'
    
    context["top_process_rows"] = top_process_rows
    
    # 5. Analyse de Fichiers
        
    extensions_to_track = {
        '.txt': {'count': 0, 'size': 0}, '.py': {'count': 0, 'size': 0}, '.pdf': {'count': 0, 'size': 0},
        '.jpg': {'count': 0, 'size': 0}, '.png': {'count': 0, 'size': 0}, '.html': {'count': 0, 'size': 0},
        '.css': {'count': 0, 'size': 0}, '.js': {'count': 0, 'size': 0}, '.log': {'count': 0, 'size': 0},
        '.zip': {'count': 0, 'size': 0}, 'OTHER': {'count': 0, 'size': 0}
    }
    total_files = 0
    largest_files = []
    
    for root, _, files in os.walk(MONITOR_DIR):
        for filename in files:
            file_path = os.path.join(root, filename)
            if not os.path.exists(file_path) or not os.path.isfile(file_path): continue
            try: file_size = os.path.getsize(file_path)
            except OSError: continue

            total_files += 1
            _, ext = os.path.splitext(filename)
            ext = ext.lower()
            key = ext if ext in extensions_to_track else 'OTHER'
            extensions_to_track[key]['count'] += 1
            extensions_to_track[key]['size'] += file_size
            largest_files.append((file_path, file_size))

    file_stats_rows = ""
    for ext, stats in extensions_to_track.items():
        if stats['count'] > 0:
            count = stats['count']
            percent = round((count / total_files) * 100, 2) if total_files else 0
            size_gb = bytes_to_gb(stats['size'])
            file_stats_rows += f'<tr><td>{ext}</td><td>{count}</td><td>{percent}%</td><td>{size_gb} GB</td></tr>'
    
    largest_files.sort(key=lambda x: x[1], reverse=True)
    largest_files_list = ""
    for i, (path, size) in enumerate(largest_files[:5]):
        size_gb = bytes_to_gb(size)
        largest_files_list += f'<p>{i+1}. <strong>{os.path.basename(path)}</strong> ({size_gb} GB)</p>'

    context.update({
        "file_scan_directory": MONITOR_DIR,
        "recursive_status": "Oui",
        "file_extension_count": len(extensions_to_track) - 1,
        "file_stats_rows": file_stats_rows,
        "largest_files_list": largest_files_list
    })
    
    return context


# --- ROUTE FLASK ET GÉNÉRATION DE FICHIER ---

def static_dashboard(context):
    """Génère le fichier index.html statique pour la soumission."""
    try:
        with open(TEMPLATE_FILE, 'r') as f:
            template_content = f.read()
            
        with app.app_context(): 
            # Utilise render_template_string de Flask pour effectuer le rendu Jinja2
            output = render_template_string(template_content, **context)
        
        with open(OUTPUT_FILE, 'w') as f:
            f.write(output)
            
        print(f" Tableau de bord statique généré dans {OUTPUT_FILE}")
        print(f"   Dernière mise à jour : {context['timestamp']}")
        
    except Exception as e:
        print(f"Erreur lors de la génération du dashboard statique : {e}")
        
        with open(OUTPUT_FILE, 'w') as f:
            f.write(output)
            
        print(f" Tableau de bord statique généré dans {OUTPUT_FILE}")
        print(f"   Dernière mise à jour : {context['timestamp']}")
        
    except Exception as e:
        print(f"Erreur lors de la génération du dashboard statique : {e}")

def static_generation():
    """Fonction à appeler pour le mode 'génération statique'."""
    data = collect_data()
    static_dashboard(data)

@app.route('/')
def live_dashboard():
    """Route pour afficher les données collectées dynamiquement."""
    data = collect_data()
    
    try:
        with open(TEMPLATE_FILE, 'r') as f:
            template_content = f.read()
        return render_template_string(template_content, **data)
    except FileNotFoundError:
        return f"Erreur: Le fichier {TEMPLATE_FILE} est introuvable."


if __name__ == '__main__':
    
    print("Mode d'exécution : Génération de fichier statique (Requis pour la soumission)")
    static_generation()
