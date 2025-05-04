# Definições de cores para mensagens
R = '\033[31m'
P = '\033[38;5;135m'
RST = '\033[0m'
ERR = f'{P}[{RST}{R}ERROR{RST}{P}]{RST}'

# Verifica se a versão do Python é compatível (>= 3.10.6)
import sys, subprocess
python_version = subprocess.run(['python', '--version'], capture_output=True, text=True).stdout.split()[1]
if tuple(map(int, python_version.split('.'))) < (3, 10, 6):
    print(f'{ERR}: Python version 3.10.6 or higher required, and you are using Python {python_version}')
    sys.exit()

# Imports e variáveis globais
from IPython.display import display, HTML, clear_output, Image
from IPython import get_ipython
from ipywidgets import widgets
from pathlib import Path
import shutil
import shlex
import json
import os

# Adiciona diretório ao path de importação
sys.path.append(os.path.expanduser("~/.conda"))

# Importa funções personalizadas do módulo nenen88
from nenen88 import pull, say, download, clone, tempe

# Utilidades
SyS = get_ipython().system
CD = os.chdir
HOME = Path.home()
SRC = HOME / '.gutris1'
CSS = SRC / 'setup.css'
IMG = SRC / 'loading.png'
MRK = SRC / 'marking.py'
MARKED = SRC / 'marking.json'
TMP = Path('/tmp')

SRC.mkdir(parents=True, exist_ok=True)
iRON = os.environ

# Retorna links dos scripts dependendo da UI
def SM_Script(WEBUI):
    return [
        f'https://github.com/gutris1/segsmaker/raw/main/script/SM/venv.py {WEBUI}',
        f'https://github.com/gutris1/segsmaker/raw/main/script/SM/Launcher.py {WEBUI}',
        f'https://github.com/gutris1/segsmaker/raw/main/script/SM/segsmaker.py {WEBUI}'
    ]

def CN_Script(WEBUI):
    return f'https://github.com/gutris1/segsmaker/raw/main/script/controlnet.py {WEBUI}/asd'

# Carrega o CSS
def Load_CSS():
    display(HTML(f'<style>{CSS.read_text()}</style>'))

# Limpa o /tmp exceto um diretório específico
def tmp_cleaning(v):
    for i in TMP.iterdir():
        if i.is_dir() and i != v:
            shutil.rmtree(i)
        elif i.is_file() and i != v:
            i.unlink()

# Instala ffmpeg e CUDA libs se necessário
def check_ffmpeg():
    i = get_ipython().getoutput('conda list ffmpeg')
    if not any('ffmpeg' in l for l in i):
        cmds = [
            ('mamba install -y ffmpeg curl', '\ninstalling ffmpeg...'),
            ('mamba install -y cuda-runtime=12.4.1', 'installing cuda-runtime=12.4.1...'),
            ('mamba install -y cudnn=9.2.1.18', 'installing cudnn=9.2.1.18...'),
            ('conda clean -y --all', None)
        ]
        for cmd, msg in cmds:
            if msg: print(msg)
            subprocess.run(shlex.split(cmd), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Marca configurações no JSON
def marking(p, n, i):
    t = p / n
    if not t.exists():
        t.write_text(json.dumps({
            'ui': i,
            'launch_args': '',
            'zrok_token': '',
            'ngrok_token': '',
            'tunnel': ''
        }, indent=4))
    d = json.loads(t.read_text())
    d.update({'ui': i, 'launch_args': ''})
    t.write_text(json.dumps(d, indent=4))

# Instala túneis ngrok e zrok
def install_tunnel():
    bins = {
        'zrok': {
            'bin': HOME / '.zrok/bin/zrok',
            'url': 'https://github.com/openziti/zrok/releases/download/v1.0.2/zrok_1.0.2_linux_amd64.tar.gz'
        },
        'ngrok': {
            'bin': HOME / '.ngrok/bin/ngrok',
            'url': 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz'
        }
    }

    for n, b in bins.items():
        binPath = b['bin']
        if binPath.exists():
            continue
        url = b['url']
        name = Path(url).name
        binDir = binPath.parent
        binDir.mkdir(parents=True, exist_ok=True)
        SyS(f'curl -sLo {binDir}/{name} {url}')
        SyS(f'tar -xzf {binDir}/{name} -C {binDir} --wildcards *{n}')
        SyS(f'rm -f {binDir}/{name}')
        if str(binDir) not in iRON.get('PATH', ''):
            iRON['PATH'] += ':' + str(binDir)
        binPath.chmod(0o755)

# Cria links simbólicos dependendo da UI selecionada
def sym_link(U, M):
    configs = {
        'A1111': {...},  # pode preencher como está no original
        'ReForge': {...},
        'Forge': {...},
        'ComfyUI': {...},
        'SwarmUI': {...}
    }
    cfg = configs.get(U)
    if cfg is None:
        print(f'{ERR}: Unknown UI "{U}"')
        return
    for s in cfg['sym']:
        SyS(s)
    for src, dst in cfg['links']:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            dst.symlink_to(src, target_is_directory=src.is_dir())
