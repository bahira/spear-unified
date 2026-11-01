"""Export a local dashboard snapshot from measured reports; no service or network."""
from pathlib import Path
import datetime,json
root=Path(__file__).resolve().parents[1]
def read(name):
 p=root/'reports'/name
 return json.loads(p.read_text()) if p.exists() else None
payload={'updated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'repository':'https://github.com/bahira/spear-unified','goal':'Réduire le coût des calculs avec une précision contrôlée et des gains mesurés.','modules':[{'name':n,'status':s} for n,s in [('Découverte Superspear','actif'),('Validation indépendante','actif'),('Benchmarks précision/vitesse','actif'),('CLI Python/JSON','actif'),('Triple Helix et suivi GitHub','actif'),('Backend natif dans le runtime','non connecté'),('Navigateur / LLM / REA','non connectés')]],'discovery':read('discovery-speed.json'),'native_probe':read('native-probe.json'),'note':'Instantané exporté par l’agent ; aucun accès GitHub direct ni activité simulée.'}
(root/'dashboard/status.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n')
