# Deep-dive — `chrysa/floating-agent`

**Repo local**: `/home/anthony/Documents/perso/projects/chrysa/floating-agent`

**But (1 phrase)**: Assistant IA "whole-life" flottant multi-OS (Windows + Linux) — un
overlay natif PySide6 (Qt) frameless/always-on-top au-dessus d'un cœur agent à tool-calling,
avec un moteur proactif (scheduler + notifications OS) qui lit/écrit Notion, envoie des
rappels et agit (système, calendrier, messagerie) sans quitter le contexte de l'utilisateur.

**Stack observée**: Python 3.14, PySide6 (LGPL, choisi vs PyQt6/GPL — cf D-0002), FastAPI/uvicorn
optionnel (`--serve`), httpx, psutil, keyring (secrets), pydantic. Cœur = `floating_agent/agent/loop.py`
(boucle tool-call, `MAX_STEPS=5`, gate de confirmation deny-by-default sur tools sensibles),
`overlay/window.py` (fenêtre frameless translucide draggable), `proactive/scheduler.py` (tick →
reminders dus → notifier). Packaging PyInstaller onefile per-OS (D-0003).

Le projet est une **app produit**, pas une lib — mais chacune de ses briques (overlay Qt,
tool-loop, scheduler proactif, notifications cross-OS, secret store) a un équivalent OSS de
référence directement pillable. Toutes les sources ci-dessous sont **permissives** (MIT/Apache/LGPL)
→ copiables. Aucune source copyleft fort / restrictive retenue.

---

## szczyglis-dev/py-gpt

- **owner/repo**: szczyglis-dev/py-gpt
- **stars**: ⭐1880
- **activité**: pushed 2026-08-15 (très actif)
- **langage**: Python
- **licence**: **MIT** (l'API GitHub renvoie NOASSERTION mais le fichier LICENSE est bien MIT © 2026 Marcin Szczygliński) → **COPIABLE**
- **fichier/module du pattern**: `src/pygpt_net/ui/tray.py`, `src/pygpt_net/ui/main.py`, plugin/tool system
- **mécanisme réel**: assistant IA desktop PySide6 multi-modèle (GPT/Claude/Ollama/…) avec system
  tray, présets, plugins, MCP, tools. C'est l'analogue mature le plus proche de floating-agent :
  overlay/tray Qt + boucle agent + tools + multi-provider. À étudier surtout pour (a) l'organisation
  UI/plugins Qt, (b) l'intégration tray + fenêtre, (c) l'abstraction multi-provider (aligne avec le
  standard chrysa "multi-model / local-first").
- **snippet portable** (pattern tray + toggle overlay, réécrit générique) :
  ```python
  from PySide6.QtGui import QAction, QIcon
  from PySide6.QtWidgets import QSystemTrayIcon, QMenu

  def build_tray(app, window) -> QSystemTrayIcon:
      tray = QSystemTrayIcon(QIcon("assets/icon.png"), parent=app)
      menu = QMenu()
      toggle = QAction("Show / Hide", menu)
      toggle.triggered.connect(lambda: window.hide() if window.isVisible() else window.show())
      menu.addAction(toggle)
      quit_action = QAction("Quit", menu)
      quit_action.triggered.connect(app.quit)
      menu.addAction(quit_action)
      tray.setContextMenu(menu)
      tray.show()
      return tray
  ```
- **intégration dans floating-agent**: brancher un `QSystemTrayIcon` dans `overlay/app.py` /
  `overlay/tray.py` (le module existe déjà) pour show/hide l'`OverlayWindow`, aligné sur le pattern
  py-gpt ; s'inspirer de leur `plugin/` pour formaliser le contrat des tools (`agent/tools.py`).
- **gotchas**: py-gpt est un monolithe lourd (des centaines de modules, vision/voice/RAG) — ne pas
  vendoriser, seulement lire les patterns. Leur couche provider est plus riche mais moins typée que
  le standard chrysa ; garder l'`LLMClient` maison typé strict.

---

## kivy/plyer

- **owner/repo**: kivy/plyer
- **stars**: ⭐1797
- **activité**: pushed 2026-06-02 (actif)
- **langage**: Python
- **licence**: **MIT** → **COPIABLE**
- **fichier/module du pattern**: `plyer/facades/notification.py` + backends `plyer/platforms/{win,linux,macosx}/notification.py`
- **mécanisme réel**: façade unique `notification.notify(title, message, ...)` qui dispatche vers le
  backend natif de l'OS (Windows toast / dbus `notify-send` Linux / NSUserNotification macOS). Couvre
  aussi battery, wifi, etc. C'est exactement l'abstraction dont a besoin `proactive/notifier.py`
  pour être réellement cross-OS.
- **snippet portable**:
  ```python
  from plyer import notification

  def notify(title: str, message: str) -> None:
      notification.notify(title=title, message=message, app_name="floating-agent", timeout=8)
  ```
- **intégration dans floating-agent**: implémenter `Notifier.notify()` (`proactive/notifier.py`) via
  plyer plutôt qu'un backend maison par OS ; le `ReminderScheduler.tick()` appelle déjà
  `self._notifier.notify(...)` → une seule classe `PlyerNotifier` à écrire.
- **gotchas**: sur Linux nécessite un daemon de notifications (dbus) ; en headless/CI ça lève →
  garder un `NullNotifier` pour les tests (déjà la bonne granularité avec l'injection du notifier).
  Windows toast plyer est parfois capricieux (préférer `win10toast`/WinRT si besoin d'actions).

---

## ms7m/notify-py

- **owner/repo**: ms7m/notify-py
- **stars**: ⭐290
- **activité**: pushed 2024-07-09 (peu actif mais stable/petit)
- **langage**: Python
- **licence**: **MIT** → **COPIABLE**
- **fichier/module du pattern**: `notifypy/notify.py` + `notifypy/os_notifiers/{windows,linux,macos}.py`
- **mécanisme réel**: objet `Notify()` avec `.title/.message/.icon/.audio` puis `.send()` ; backends
  OS auto-sélectionnés, une seule dépendance (loguru). Alternative plus légère à plyer, focalisée
  uniquement notifications → utile si on ne veut pas la surface complète de plyer.
- **snippet portable**:
  ```python
  from notifypy import Notify

  def notify(title: str, message: str) -> None:
      n = Notify()
      n.application_name = "floating-agent"
      n.title = title
      n.message = message
      n.send(block=False)
  ```
- **intégration dans floating-agent**: interchangeable avec plyer pour `Notifier` ; choisir l'un OU
  l'autre. notify-py = plus minimal, plyer = plus de features système.
- **gotchas**: repo peu maintenu (dernier push 2024) ; support actions/boutons limité ; l'icône doit
  être un chemin fichier valide sinon fallback silencieux.

---

## agronholm/apscheduler

- **owner/repo**: agronholm/apscheduler
- **stars**: ⭐7606
- **activité**: pushed 2026-08-01 (très actif)
- **langage**: Python
- **licence**: **MIT** → **COPIABLE**
- **fichier/module du pattern**: `apscheduler/schedulers/` + triggers `apscheduler/triggers/{cron,interval,date}.py`
- **mécanisme réel**: scheduler in-process avec triggers cron/interval/date, jobstores persistants,
  exécution async ou thread. `proactive/scheduler.py` réimplémente aujourd'hui un tick manuel
  (`due(now)` → notify → `mark_fired`) — APScheduler industrialise ça (persistance des jobs, misfire
  grace time, timezones) sans réinventer le cron.
- **snippet portable**:
  ```python
  from apscheduler.schedulers.background import BackgroundScheduler

  scheduler = BackgroundScheduler()
  scheduler.add_job(lambda: notifier.notify("Reminder", r.message),
                    trigger="date", run_date=r.due_at, id=r.id)
  scheduler.start()  # non-bloquant ; s'intègre à la boucle Qt
  ```
- **intégration dans floating-agent**: remplacer le `tick(now)` maison par un `BackgroundScheduler`
  qui planifie chaque reminder à sa `due_at` ; garder `ReminderStore` comme source de vérité +
  jobstore SQLAlchemy pour survivre aux redémarrages. La `proactive/pulse.py` (wake) peut devenir un
  `interval` job.
- **gotchas**: v4 a une API async assez différente de v3 (vérifier la version épinglée) ; attention à
  faire tourner le scheduler dans le thread Qt correct (le callback notify touche l'UI → passer par
  un signal Qt, pas d'appel direct depuis le thread scheduler). Pour l'unit-test, garder le
  `tick(now)` déterministe existant plutôt que de tester le vrai scheduler.

---

## anthropics/claude-cookbooks

- **owner/repo**: anthropics/claude-cookbooks (ex anthropic-cookbook)
- **stars**: ⭐51545
- **activité**: pushed 2026-08-14 (très actif)
- **langage**: Jupyter Notebook
- **licence**: **MIT** → **COPIABLE**
- **fichier/module du pattern**: `tool_use/` (customer_service_agent, tool_choice, parallel tools)
- **mécanisme réel**: recettes canoniques de la boucle tool-use Anthropic — envoyer `tools=[...]`,
  lire `stop_reason == "tool_use"`, exécuter, renvoyer un bloc `tool_result`, itérer. C'est
  exactement le contrat que `agent/loop.py` implémente déjà (messages assistant→tool→assistant) ;
  utile comme référence de conformité (ids de tool_call, format des résultats, gestion parallèle).
- **snippet portable** (forme de la boucle, provider-agnostique) :
  ```python
  while step < MAX_STEPS:
      resp = client.complete(messages, registry.specs())
      if not resp.tool_calls:
          return resp.text
      messages.append({"role": "assistant", "content": resp.text,
                       "tool_calls": [{"id": c.id, "name": c.name, "arguments": c.arguments}
                                      for c in resp.tool_calls]})
      messages += [{"role": "tool", "tool_call_id": c.id, "content": registry.get(c.name).run(c.arguments)}
                   for c in resp.tool_calls]
  ```
- **intégration dans floating-agent**: le cœur existe déjà et suit ce pattern — s'en servir pour (a)
  valider le mapping vers le format Anthropic quand `LLMClient` cible Claude, (b) ajouter le
  parallel-tool + `tool_choice` forcé si besoin, (c) reprendre leurs prompts de confirmation.
- **gotchas**: ce sont des notebooks pédagogiques, pas une lib packagée → recopier le *pattern*, pas
  d'import. Le format tool exact diffère entre Anthropic (`tool_use`/`tool_result` blocks) et OpenAI
  (`tool_calls`/`role:tool`) — l'abstraction `LLMClient` doit masquer ça (elle le fait déjà).

---

## openai/openai-python

- **owner/repo**: openai/openai-python
- **stars**: ⭐31378
- **activité**: pushed 2026-08-15 (très actif)
- **langage**: Python
- **licence**: **Apache-2.0** → **COPIABLE** (permissive ; conserver l'attribution NOTICE si on copie du code substantiel)
- **fichier/module du pattern**: `src/openai/types/chat/` (schémas function-calling) + exemples `examples/`
- **mécanisme réel**: référence du format `tools`/`tool_calls`/`role:"tool"` côté OpenAI-compatible
  (le même que celui utilisé dans `loop.py`). Utile comme source des types/JSON-schema des tool
  specs et pour un backend `LLMClient` OpenAI-compatible (couvre aussi Ollama/llama.cpp en mode
  OpenAI → sert le standard chrysa local-first).
- **snippet portable**:
  ```python
  tools = [{"type": "function", "function": {
      "name": t.name, "description": t.description, "parameters": t.json_schema}}
      for t in registry.tools]
  resp = client.chat.completions.create(model=model, messages=messages, tools=tools)
  ```
- **intégration dans floating-agent**: fournir un `OpenAICompatibleClient` implémentant l'interface
  `LLMClient` → permet de router vers ai-aggregator OU un LLM local (llama3.1) via la même API,
  conformément au standard offline-first.
- **gotchas**: Apache-2.0 ≠ MIT — si on copie des fichiers entiers, garder l'en-tête/NOTICE ; sinon
  ré-écrire le mapping (trivial). Ne pas coupler l'agent au SDK OpenAI en dur : garder `LLMClient`
  comme port, le SDK comme un adapter parmi d'autres.

---

## Note licences

Toutes les sources retenues sont **permissives et copiables** : MIT (py-gpt, plyer, notify-py,
APScheduler, claude-cookbooks, keyring), Apache-2.0 (openai-python). PySide6 lui-même est **LGPL**
(déjà arbitré vs PyQt6/GPL en D-0002 — OK tant qu'on linke dynamiquement, ce que fait PyInstaller).
**Aucune** dépendance copyleft fort (GPL/AGPL) ou restrictive (Elastic/BSL/FSL/fair-code) à
réimplémenter. Seule vigilance : Apache-2.0 (openai-python) impose l'attribution NOTICE en cas de
copie substantielle de code.
