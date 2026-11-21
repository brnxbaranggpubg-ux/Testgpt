from pathlib import Path
import json
import sys

root = Path(sys.argv[1])
locales = {
    "en_us.json": {
        "baroxvs.settings.label.hand_glass_opacity": "Hand glass opacity",
        "baroxvs.settings.label.fresnel_edge_strength": "Fresnel edge strength",
        "baroxvs.settings.label.item_detail_transmission": "Item detail transmission",
    },
    "de_de.json": {
        "baroxvs.settings.label.hand_glass_opacity": "Deckkraft des Handglases",
        "baroxvs.settings.label.fresnel_edge_strength": "Stärke der Fresnel-Kante",
        "baroxvs.settings.label.item_detail_transmission": "Übertragung von Objektdetails",
    },
    "tr_tr.json": {
        "baroxvs.settings.label.hand_glass_opacity": "Eldeki cam saydamlığı",
        "baroxvs.settings.label.fresnel_edge_strength": "Fresnel kenar gücü",
        "baroxvs.settings.label.item_detail_transmission": "Eşya ayrıntısı geçirgenliği",
    },
}
lang_dir = root / "src/main/resources/assets/baroxvs/lang"
for filename, additions in locales.items():
    path = lang_dir / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(additions)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("v108 localization compatibility labels added for all three languages")
