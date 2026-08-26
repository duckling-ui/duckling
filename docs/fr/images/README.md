# Captures d'écran (Français)

Les captures pour la documentation française se trouvent dans **`docs/assets/screenshots/`** et doivent être référencées avec des chemins absolus :

```markdown
![Zone de dépôt vide](/assets/screenshots/ui/dropzone-empty-fr.png)
```

Guide complet : [SCREENSHOT_GUIDE.md](/assets/screenshots/SCREENSHOT_GUIDE.md)

Régénérer toutes les langues :

```bash
./scripts/capture-screenshots.sh
python3 scripts/normalize_doc_screenshot_paths.py
```
