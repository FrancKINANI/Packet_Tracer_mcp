# Packet Tracer MCP Server

Serveur MCP pour Cisco Packet Tracer, conçu pour permettre à un LLM (Copilot, Claude, etc.) de planifier, valider et déployer des topologies réseau complètes en temps réel.

Demandez "crée une topologie avec 3 routeurs, DHCP et OSPF" et le serveur :
- planifie les appareils et liens
- attribue automatiquement les adresses IP
- génère le script PTBuilder et les configs CLI
- déploie automatiquement sur Packet Tracer via bridge HTTP

**Python 3.11+ · Pydantic 2.0+ · FastMCP · Streamable HTTP**

---

## Fonctionnalités principales

- Pipeline complet : planification, validation, génération, déploiement
- Déploiement en direct : commandes envoyées directement à Packet Tracer
- 22 outils MCP couvrant catalogue, planification, validation, génération, export et contrôle de topologie
- Auto-fix : correction automatique des erreurs courantes de câblage, modèle et interface
- Planification automatique des adresses IP (/24 pour LAN, /30 pour liens inter-routeurs)
- Génération de scripts PTBuilder et configurations CLI IOS
- Templates de topologie intégrés (multi-LAN, star, hub-spoke, branch office, router-on-a-stick, etc.)

---

## Installation rapide

```bash
git clone https://github.com/FrancKINANI/MCP_Packet_Tracer.git
cd MCP_Packet_Tracer
pip install -e .
```

---

## Démarrage

```bash
python -m src.packet_tracer_mcp
```

Cela démarre automatiquement :
- le serveur MCP sur `http://127.0.0.1:39000/mcp`
- le bridge HTTP interne sur `http://127.0.0.1:54321`

> Pour le mode stdio (debug/legacy) : `python -m src.packet_tracer_mcp --stdio`

---

## Configuration du client MCP

### VS Code

`.vscode/mcp.json`

```json
{
  "servers": {
    "packet-tracer": {
      "url": "http://127.0.0.1:39000/mcp"
    }
  }
}
```

### Claude Desktop

`claude_desktop_config.json`

```json
{
  "mcpServers": {
    "packet-tracer": {
      "url": "http://127.0.0.1:39000/mcp"
    }
  }
}
```

---

## Utilisation

Le serveur expose des outils MCP pour piloter toute la chaîne :
- exploration du catalogue
- planification de topologies
- validation de plans
- génération de scripts et configs
- export de projets
- déploiement live dans Packet Tracer

### Exemples de tools

- `pt_list_devices`
- `pt_list_templates`
- `pt_get_device_details`
- `pt_estimate_plan`
- `pt_plan_topology`
- `pt_validate_plan`
- `pt_fix_plan`
- `pt_explain_plan`
- `pt_generate_script`
- `pt_generate_configs`
- `pt_full_build`
- `pt_deploy`
- `pt_live_deploy`
- `pt_bridge_status`
- `pt_query_topology`
- `pt_delete_device`
- `pt_rename_device`
- `pt_move_device`
- `pt_delete_link`
- `pt_send_raw`
- `pt_export`
- `pt_list_projects`
- `pt_load_project`

---

## Déploiement en direct (Live Deploy)

Le meilleur atout de ce projet : envoyer les commandes directement dans Packet Tracer sans copier-coller.

### Bootstrap à exécuter dans Packet Tracer

Ouvrez `Builder Code Editor` et collez ceci :

```javascript
/* PT-MCP Bridge */ window.webview.evaluateJavaScriptAsync("setInterval(function(){var x=new XMLHttpRequest();x.open('GET','http://127.0.0.1:54321/next',true);x.onload=function(){if(x.status===200&&x.responseText){$se('runCode',x.responseText)}};x.onerror=function(){};x.send()},500)");
```

Ce bootstrap lance une boucle de polling dans le webview de PTBuilder. Le serveur MCP place les commandes dans le bridge HTTP, et Packet Tracer les exécute.

---

## Architecture du projet

```
src/packet_tracer_mcp/
├── adapters/mcp/          # Enregistrement des tools MCP et resources
├── application/           # Use cases et DTOs
├── domain/                # Modèles, services métier, règles de validation
├── infrastructure/        # Catalogue, générateurs, exécution live, persistence
├── shared/                # Constantes, enums, utilitaires, templates
├── server.py              # Point d’entrée du serveur
└── settings.py            # Configuration globale
```

### Flux général

1. LLM envoie une requête
2. Orchestrator génère un `TopologyPlan`
3. Validator vérifie le plan
4. Auto-fixer corrige les erreurs si nécessaire
5. Générateur produit le script PTBuilder et les configs IOS
6. Déploiement en direct via bridge HTTP ou export sur disque

---

## Exigences

- Python 3.11+
- Cisco Packet Tracer 8.2+
- Python packages installés via `pip install -e .`

---

## Tests

```bash
python -m pytest tests/ -v
```

---

## Licence

Ce projet est sous licence MIT.
