from flask import Flask, request, jsonify  
import subprocess  
import re  
import json  
import os  
import glob  

app = Flask(__name__)  

@app.route('/run-pytest', methods=['POST'])  
def run_pytest():  
    data = request.get_json()  
    
    # Récupération des paramètres  
    test_path = data.get('test_path', '')  
    verbose = data.get('verbose', False)  
    
    if not test_path:  
        return jsonify({"error": "Chemin de test non spécifié"}), 400  
    
    # Construction de la commande  
    cmd = ['poetry', 'run', 'pytest', test_path]  
    
    # Ajout des options  
    if verbose:  
        cmd.append('-v')  
    
    # Option pour la sortie au format JSON  
    cmd.append('--no-header')  
    cmd.append('-v')  
    
    try:  
        # Exécution de la commande  
        result = subprocess.run(cmd, capture_output=True, text=True)  
        
        # Traitement de la sortie pour un format plus lisible  
        output = result.stdout  
        error_output = result.stderr  
        
        # Formatage des résultats  
        formatted_results = format_pytest_output(output, error_output)  
        
        return jsonify({  
            "success": result.returncode == 0,  
            "results": formatted_results,  
            "returncode": result.returncode  
        })  
    except Exception as e:  
        return jsonify({"error": str(e)}), 500  

def format_pytest_output(output, error_output):  
    """Formate la sortie de PyTest pour être plus lisible"""  
    lines = output.split('\n')  
    formatted_results = []  
    
    # Motif pour détecter les tests  
    test_pattern = r'(PASSED|FAILED|SKIPPED|XFAILED|XPASSED)'  
    
    current_test = None  
    current_error = []  
    collecting_error = False  
    
    for line in lines:  
        if re.search(test_pattern, line):  
            # Nouveau test trouvé  
            if current_test:  
                # Ajouter le test précédent  
                if current_error:  
                    current_test["error"] = "\n".join(current_error)  
                formatted_results.append(current_test)  
                current_error = []  
            
            # Extraire le nom du test et le statut  
            parts = line.strip().split()  
            if len(parts) >= 2:  
                test_name = parts[0]  
                status = next((s for s in parts if s in ["PASSED", "FAILED", "SKIPPED", "XFAILED", "XPASSED"]), "UNKNOWN")  
                
                current_test = {  
                    "name": test_name,  
                    "status": status,  
                    "error": None  
                }  
                
                collecting_error = status == "FAILED"  
            
        elif collecting_error and line.strip() and not line.startswith("="):  
            # Collecter les lignes d'erreur  
            current_error.append(line)  
    
    # Ajouter le dernier test  
    if current_test:  
        if current_error:  
            current_test["error"] = "\n".join(current_error)  
        formatted_results.append(current_test)  
    
    # Ajouter les erreurs générales  
    if error_output:  
        formatted_results.append({  
            "name": "SYSTEM",  
            "status": "ERROR",  
            "error": error_output  
        })  
    
    return formatted_results  

@app.route('/git-commit', methods=['POST'])  
def git_commit():  
    data = request.get_json()  
    
    # Récupération du message de commit  
    commit_message = data.get('message', '')  
    
    if not commit_message:  
        return jsonify({"error": "Message de commit non spécifié"}), 400  
    
    try:  
        # Vérification que nous sommes dans un dépôt Git  
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'],   
                       check=True, capture_output=True, text=True)  
        
        # Obtenir la liste des fichiers modifiés non ignorés et < 10Mo  
        files_to_add = get_files_to_commit()  
        
        if not files_to_add:  
            return jsonify({  
                "success": False,  
                "message": "Aucun fichier à committer",  
                "command": f"git commit -m \"{commit_message}\""  
            })  
        
        # Ajouter les fichiers  
        add_result = subprocess.run(['git', 'add'] + files_to_add,   
                                    capture_output=True, text=True)  
        
        if add_result.returncode != 0:  
            return jsonify({  
                "success": False,  
                "error": f"Erreur lors de l'ajout des fichiers: {add_result.stderr}",  
                "command": f"git add . && git commit -m \"{commit_message}\""  
            })  
        
        # Effectuer le commit  
        commit_result = subprocess.run(['git', 'commit', '-m', commit_message],   
                                       capture_output=True, text=True)  
        
        if commit_result.returncode != 0:  
            return jsonify({  
                "success": False,  
                "error": f"Erreur lors du commit: {commit_result.stderr}",  
                "command": f"git commit -m \"{commit_message}\""  
            })  
        
        return jsonify({  
            "success": True,  
            "message": commit_result.stdout,  
            "files_added": files_to_add  
        })  
        
    except subprocess.CalledProcessError:  
        return jsonify({  
            "success": False,  
            "error": "Ce dossier n'est pas un dépôt Git valide.",  
            "command": "git init && git add . && git commit -m \"Initial commit\""  
        })  
    except Exception as e:  
        return jsonify({  
            "success": False,  
            "error": str(e),  
            "command": f"git add . && git commit -m \"{commit_message}\""  
        })  

def get_files_to_commit():  
    """  
    Obtient la liste des fichiers à committer:  
    - Non présents dans .gitignore  
    - Taille < 10Mo  
    - Modifiés ou non suivis  
    """  
    # Obtenir les fichiers modifiés ou non suivis  
    status_result = subprocess.run(['git', 'status', '--porcelain'],   
                                  capture_output=True, text=True)  
    
    if status_result.returncode != 0:  
        raise Exception(f"Erreur lors de l'obtention du statut Git: {status_result.stderr}")  
    
    # Extraire les chemins de fichiers  
    files = []  
    for line in status_result.stdout.split('\n'):  
        if not line.strip():  
            continue  
        
        # Format du statut git: XY PATH  
        # Où X est le statut dans l'index, Y est le statut dans le working tree  
        status = line[:2]  
        file_path = line[3:].strip()  
        
        # Vérifier si le fichier existe (il pourrait avoir été supprimé)  
        if os.path.exists(file_path):  
            # Vérifier la taille du fichier (< 10Mo = 10 * 1024 * 1024 octets)  
            if os.path.getsize(file_path) < 10 * 1024 * 1024:  
                files.append(file_path)  
    
    return files  

@app.route('/status', methods=['GET'])  
def status():  
    return jsonify({"status": "running"})  

if __name__ == '__main__':  
    app.run(host='127.0.0.1', port=5000, debug=True)  