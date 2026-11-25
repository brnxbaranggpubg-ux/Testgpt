from pathlib import Path
import json
import sys

root = Path(sys.argv[1])
locales = {
    "en_us.json": {
        "baroxvs.settings.label.hand_glass_opacity": "Hand glass opacity",
        "baroxvs.settings.label.fresnel_edge_strength": "Fresnel edge strength",
        "baroxvs.settings.label.item_detail_transmission": "Item detail transmission",
        "baroxvs.settings.label.reflection_pattern_scale": "Reflection pattern scale",
        "baroxvs.settings.label.moving_reflection_gloss": "Moving reflection gloss",
        "baroxvs.settings.label.skin_transmission": "Skin transmission",
        "baroxvs.settings.label.reflection_size": "Reflection size",
        "baroxvs.settings.label.glass_coating_opacity": "Glass coating opacity",
        "baroxvs.settings.label.arm_glass_opacity": "Arm glass opacity",
    },
    "de_de.json": {
        "baroxvs.settings.label.hand_glass_opacity": "Deckkraft des Handglases",
        "baroxvs.settings.label.fresnel_edge_strength": "Stärke der Fresnel-Kante",
        "baroxvs.settings.label.item_detail_transmission": "Übertragung von Objektdetails",
        "baroxvs.settings.label.reflection_pattern_scale": "Skalierung des Reflexionsmusters",
        "baroxvs.settings.label.moving_reflection_gloss": "Beweglicher Reflexionsglanz",
        "baroxvs.settings.label.skin_transmission": "Hautdurchlässigkeit",
        "baroxvs.settings.label.reflection_size": "Reflexionsgröße",
        "baroxvs.settings.label.glass_coating_opacity": "Deckkraft der Glasbeschichtung",
        "baroxvs.settings.label.arm_glass_opacity": "Deckkraft des Armglases",
    },
    "tr_tr.json": {
        "baroxvs.settings.label.hand_glass_opacity": "Eldeki cam saydamlığı",
        "baroxvs.settings.label.fresnel_edge_strength": "Fresnel kenar gücü",
        "baroxvs.settings.label.item_detail_transmission": "Eşya ayrıntısı geçirgenliği",
        "baroxvs.settings.label.reflection_pattern_scale": "Yansıma deseni ölçeği",
        "baroxvs.settings.label.moving_reflection_gloss": "Hareketli yansıma parlaklığı",
        "baroxvs.settings.label.skin_transmission": "Deri geçirgenliği",
        "baroxvs.settings.label.reflection_size": "Yansıma boyutu",
        "baroxvs.settings.label.glass_coating_opacity": "Cam kaplama saydamlığı",
        "baroxvs.settings.label.arm_glass_opacity": "Kol camı saydamlığı",
    },
}
lang_dir = root / "src/main/resources/assets/baroxvs/lang"
for filename, additions in locales.items():
    path = lang_dir / filename
    data = json.loads(path.read_text(encoding="utf-8"))
    data.update(additions)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("v108 localization compatibility labels added for all three languages")
