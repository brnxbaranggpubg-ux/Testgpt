#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "project")

def read(rel):
    path = root / rel
    if not path.is_file():
        raise SystemExit(f"Missing v026 source file: {rel}")
    return path.read_text(encoding="utf-8")

def write(rel, value):
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding="utf-8")

gui = r'''package com.baroxvs.client.gui;

import com.baroxvs.client.BaroxVsClient;
import com.baroxvs.client.config.BaroxConfig;
import com.baroxvs.client.cosmetic.ModuleCatalog;
import com.baroxvs.client.theme.Theme;
import com.baroxvs.client.theme.Themes;
import net.minecraft.client.gui.DrawContext;
import net.minecraft.client.gui.screen.Screen;
import net.minecraft.text.Text;
import org.lwjgl.glfw.GLFW;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * BAROX VS client-style ClickGUI.
 * It manages only the existing visual/cosmetic module catalogue.
 */
public final class ModuleClickGuiScreen extends Screen {
    private enum Filter { ALL, ENABLED, DISABLED }

    private record ModuleHit(ModuleCatalog.Module module, int x, int y, int w, int h) {}
    private record CategoryHit(String category, int x, int y, int w, int h) {}

    private final BaroxConfig cfg;
    private final Map<String, Float> hover = new HashMap<>();
    private final Map<String, Float> power = new HashMap<>();
    private final List<ModuleHit> moduleHits = new ArrayList<>();
    private final List<CategoryHit> categoryHits = new ArrayList<>();

    private String selectedCategory = "All";
    private String selectedModuleId = "";
    private String search = "";
    private Filter filter = Filter.ALL;
    private boolean searchFocused;
    private float openProgress;
    private float easedOpenProgress;
    private float animationTime;
    private int scroll;
    private int maxScroll;
    private int panelX, panelY, panelW, panelH;
    private int sidebarW, inspectorW;
    private int mainX, mainW, listY, listBottom;
    private int searchX, searchY, searchW, searchH;
    private int studioX, studioY, studioW, studioH;
    private int closeX, closeY;
    private int inspectorX, inspectorToggleY, inspectorSettingsY;
    private int allCount, enabledCount;

    public ModuleClickGuiScreen(BaroxConfig cfg) {
        super(Text.literal("BAROX VS — Visual Client"));
        this.cfg = cfg;
    }

    @Override
    public boolean shouldPause() {
        return false;
    }

    @Override
    public void renderBackground(DrawContext context, int mouseX, int mouseY, float delta) {
        context.fill(0, 0, width, height, 0xF2070B12);
    }

    @Override
    public void render(DrawContext context, int mouseX, int mouseY, float delta) {
        Theme theme = Themes.current(cfg);
        float step = Math.max(0.01f, Math.min(1f, delta));
        openProgress = Math.min(1f, openProgress + step * 0.17f);
        float inverse = 1f - openProgress;
        easedOpenProgress = 1f - inverse * inverse * inverse;
        animationTime += step;

        layout();
        moduleHits.clear();
        categoryHits.clear();

        allCount = ModuleCatalog.all().size();
        enabledCount = 0;
        for (ModuleCatalog.Module module : ModuleCatalog.all()) {
            if (isEnabled(module)) enabledCount++;
        }
        if (selectedModuleId.isEmpty() && !ModuleCatalog.all().isEmpty()) {
            selectedModuleId = ModuleCatalog.all().get(0).id();
        }

        drawBackdrop(context, theme);
        drawShell(context, theme);
        drawHeader(context, theme);
        drawSidebar(context, theme, mouseX, mouseY);
        drawToolbar(context, theme, mouseX, mouseY);
        drawModules(context, theme, mouseX, mouseY, step);
        if (inspectorW > 0) drawInspector(context, theme, mouseX, mouseY, step);
        drawFooter(context, theme);
    }

    private void layout() {
        panelW = Math.max(220, Math.min(1120, width - 12));
        panelH = Math.max(220, Math.min(760, height - 12));
        panelX = (width - panelW) / 2;
        panelY = (height - panelH) / 2;

        sidebarW = panelW < 440 ? 74 : 148;
        inspectorW = panelW >= 940 ? 214 : 0;
        mainX = panelX + sidebarW + 13;
        mainW = panelX + panelW - 14 - mainX - (inspectorW > 0 ? inspectorW + 12 : 0);

        searchX = mainX;
        searchY = panelY + 56;
        searchH = 27;
        searchW = Math.max(86, mainW - 126);
        listY = searchY + 43;
        listBottom = panelY + panelH - 29;

        studioW = panelW >= 500 ? 62 : 0;
        studioH = 22;
        studioX = panelX + panelW - (studioW > 0 ? 108 : 34);
        studioY = panelY + 11;
        closeX = panelX + panelW - 30;
        closeY = panelY + 11;

        inspectorX = mainX + mainW + 12;
        inspectorToggleY = listBottom - 48;
        inspectorSettingsY = listBottom - 22;
    }

    private void drawBackdrop(DrawContext c, Theme theme) {
        c.fillGradient(0, 0, width, height, 0xF3070B13, 0xF00B1522);
        int glow = Ui.alpha(theme.primary(), 0x16);
        for (int i = 0; i < 12; i++) {
            float phase = animationTime * (0.17f + i * 0.011f) + i * 1.47f;
            int x = (int) (width * 0.5 + Math.sin(phase) * width * 0.43);
            int y = (int) (height * 0.5 + Math.cos(phase * 0.83f) * height * 0.40);
            int size = 2 + i % 3;
            c.fill(x, y, x + size, y + size, glow);
        }
        int line = Ui.alpha(theme.primary(), 0x20);
        int scanY = (int) ((animationTime * 17f) % Math.max(1, height));
        c.fill(0, scanY, width, scanY + 1, line);
    }

    private void drawShell(DrawContext c, Theme theme) {
        int lift = Math.round((1f - easedOpenProgress) * 16f);
        Ui.glassPanel(c, panelX, panelY + lift, panelX + panelW, panelY + panelH + lift,
                17, 0xF20B121B, Ui.alpha(theme.primary(), 0xA0));
        Ui.roundRect(c, panelX + 1, panelY + lift + 1, panelX + panelW - 1,
                panelY + lift + 43, 14, 0xDD111D2A);
        c.fill(panelX + 14, panelY + lift + 43, panelX + panelW - 14,
                panelY + lift + 44, Ui.alpha(theme.primary(), 0x64));

        Ui.glassPanel(c, panelX + 8, panelY + 51 + lift, panelX + sidebarW + 3,
                panelY + panelH - 9 + lift, 11, 0xC9081018, 0x42374A5E);
        Ui.glassPanel(c, mainX - 3, panelY + 51 + lift, mainX + mainW + 3,
                panelY + panelH - 9 + lift, 11, 0xA80B131D, 0x30394B5C);
        if (inspectorW > 0) {
            Ui.glassPanel(c, inspectorX, panelY + 51 + lift, inspectorX + inspectorW,
                    panelY + panelH - 9 + lift, 11, 0xC90B131D, 0x46384B5E);
        }
    }

    private void drawHeader(DrawContext c, Theme theme) {
        int y = panelY + 11 + Math.round((1f - easedOpenProgress) * 14f);
        Ui.text(c, textRenderer, "BAROX", panelX + 17, y, theme.primary(), 1.03f, true);
        Ui.text(c, textRenderer, "VS", panelX + 60, y, 0xFFF0F5FA, 1.03f, true);
        Ui.text(c, textRenderer, "VISUAL CLIENT", panelX + 91, y + 3,
                0xFF8499AB, 0.57f, true);

        int statusX = panelX + sidebarW + 20;
        Ui.roundRect(c, statusX, y + 1, statusX + 58, y + 19, 7, 0xA51D3A35);
        c.fill(statusX + 8, y + 8, statusX + 13, y + 13, 0xFF65E6A5);
        Ui.text(c, textRenderer, "READY", statusX + 18, y + 7, 0xFF8CE9BC, 0.55f, true);

        if (studioW > 0) {
            Ui.roundRect(c, studioX, studioY, studioX + studioW, studioY + studioH, 7, 0xA52B4050);
            Ui.textCentered(c, textRenderer, "STUDIO", studioX + studioW / 2,
                    studioY + 7, 0xFFD8E7F0, 0.55f, true);
        }
        Ui.roundRect(c, closeX, closeY, closeX + 20, closeY + studioH, 7, 0xA6422934);
        Ui.textCentered(c, textRenderer, "×", closeX + 10, closeY + 5,
                0xFFFFD8E0, 0.85f, true);

        Ui.textRight(c, textRenderer, "91 MODULES", panelX + panelW - 42,
                panelY + 38, 0xFF6E8496, 0.48f, true);
    }

    private void drawSidebar(DrawContext c, Theme theme, int mouseX, int mouseY) {
        List<String> categories = new ArrayList<>();
        categories.add("All");
        categories.addAll(ModuleCatalog.categories());

        int y = panelY + 64;
        int rowH = panelH < 340 ? 27 : 32;
        c.enableScissor(panelX + 8, panelY + 57, panelX + sidebarW + 3, panelY + panelH - 54);

        for (String category : categories) {
            int x = panelX + 13;
            int w = sidebarW - 18;
            int h = rowH - 3;
            boolean selected = selectedCategory.equals(category);
            boolean over = inside(mouseX, mouseY, x, y, w, h);
            String key = "cat:" + category;
            float value = approach(hover.getOrDefault(key, 0f), over ? 1f : 0f, 0.24f);
            hover.put(key, value);

            if (selected) {
                Ui.glassPanel(c, x, y, x + w, y + h, 7,
                        Ui.alpha(theme.primary(), 0x36), Ui.alpha(theme.primary(), 0xB0));
                c.fill(x + 1, y + 5, x + 3, y + h - 5, theme.primary());
            } else if (value > 0.01f) {
                Ui.roundRect(c, x, y, x + w, y + h, 7,
                        Ui.alpha(theme.primary(), Math.round(value * 0x24)));
            }

            String icon = categoryIcon(category);
            String label = category.equals("All") ? "ALL MODULES"
                    : (panelW < 440 ? compactCategory(category) : category.toUpperCase(Locale.ROOT));
            if (panelW < 440) {
                Ui.textCentered(c, textRenderer, icon, x + 13, y + 8,
                        selected ? theme.primary() : 0xFF91A5B6, 0.69f, true);
                Ui.text(c, textRenderer, Ui.fit(textRenderer, label, w - 28, 0.50f),
                        x + 25, y + 8, selected ? 0xFFF2F7FB : 0xFF93A5B5, 0.50f, selected);
            } else {
                Ui.text(c, textRenderer, icon, x + 8, y + 8,
                        selected ? theme.primary() : 0xFF91A5B6, 0.64f, true);
                Ui.text(c, textRenderer, Ui.fit(textRenderer, label, w - 48, 0.60f),
                        x + 27, y + 8, selected ? 0xFFF2F7FB : 0xFF93A5B5, 0.60f, selected);
            }
            int count = countCategory(category);
            Ui.textRight(c, textRenderer, Integer.toString(count), x + w - 7, y + 8,
                    selected ? theme.primary() : 0xFF687D8E, 0.50f, true);

            categoryHits.add(new CategoryHit(category, x, y, w, h));
            y += rowH;
        }
        c.disableScissor();

        int dividerY = panelY + panelH - 58;
        c.fill(panelX + 18, dividerY, panelX + sidebarW - 12, dividerY + 1, 0x493A4B5B);
        Ui.text(c, textRenderer, "BUILD 026", panelX + 17, dividerY + 9,
                0xFF71899B, 0.50f, true);
        Ui.text(c, textRenderer, enabledCount + " ACTIVE", panelX + 17, dividerY + 20,
                theme.primary(), 0.52f, true);
    }

    private String categoryIcon(String category) {
        return switch (category) {
            case "All" -> "◈";
            case "Cosmetics" -> "✧";
            case "Effects" -> "◎";
            case "Trails" -> "〰";
            case "HUD" -> "▦";
            case "Misc" -> "⌘";
            default -> "•";
        };
    }

    private String compactCategory(String category) {
        return switch (category) {
            case "Cosmetics" -> "STYLE";
            case "Effects" -> "FX";
            case "Trails" -> "TRAIL";
            case "HUD" -> "HUD";
            case "Misc" -> "MISC";
            default -> category.toUpperCase(Locale.ROOT);
        };
    }

    private int countCategory(String category) {
        if (category.equals("All")) return ModuleCatalog.all().size();
        return ModuleCatalog.inCategory(category).size();
    }

    private void drawToolbar(DrawContext c, Theme theme, int mouseX, int mouseY) {
        Ui.glassPanel(c, searchX, searchY, searchX + searchW, searchY + searchH,
                7, searchFocused ? 0xE11A2B39 : 0xA8172532,
                searchFocused ? Ui.alpha(theme.primary(), 0xD0) : 0x4B536779);

        String shown = search.isEmpty() ? (searchFocused ? "" : "⌕  SEARCH MODULES") : search;
        Ui.text(c, textRenderer, Ui.fit(textRenderer, shown, searchW - 16, 0.58f),
                searchX + 8, searchY + 9, search.isEmpty() ? 0xFF788F9F : 0xFFE7F0F5,
                0.58f, false);
        if (searchFocused && (animationTime % 1.0f) < 0.55f) {
            int caret = searchX + 8 + textRenderer.getWidth(search) / 2;
            c.fill(Math.min(searchX + searchW - 8, caret), searchY + 8,
                    Math.min(searchX + searchW - 7, caret) + 1, searchY + 19, theme.primary());
        }

        int fx = searchX + searchW + 6;
        int chipW = Math.max(25, (mainW - searchW - 12) / 3);
        String[] labels = {"ALL", "ON", "OFF"};
        Filter[] values = Filter.values();
        for (int i = 0; i < values.length; i++) {
            int x = fx + i * (chipW + 2);
            boolean selected = filter == values[i];
            boolean over = inside(mouseX, mouseY, x, searchY + 1, chipW, searchH - 2);
            Ui.roundRect(c, x, searchY + 1, x + chipW, searchY + searchH - 1, 6,
                    selected ? Ui.alpha(theme.primary(), 0x56) :
                            (over ? 0x88384E60 : 0x68202D3B));
            Ui.textCentered(c, textRenderer, labels[i], x + chipW / 2, searchY + 10,
                    selected ? 0xFFF3F8FC : 0xFF91A4B3, 0.52f, true);
        }

        List<ModuleCatalog.Module> modules = filteredModules();
        Ui.text(c, textRenderer, selectedCategory.toUpperCase(Locale.ROOT),
                mainX + 2, searchY + 34, 0xFFE2ECF3, 0.57f, true);
        Ui.textRight(c, textRenderer, modules.size() + " RESULTS  /  " + enabledCount + " ACTIVE",
                mainX + mainW, searchY + 34, 0xFF6E8495, 0.48f, true);
    }

    private void drawModules(DrawContext c, Theme theme, int mouseX, int mouseY, float delta) {
        List<ModuleCatalog.Module> modules = filteredModules();
        int columns = mainW >= 680 ? 3 : mainW >= 420 ? 2 : 1;
        int gap = 8;
        int cardW = Math.max(80, (mainW - gap * (columns - 1)) / columns);
        int cardH = panelH < 300 ? 58 : 66;
        int rowGap = 8;
        int rows = (modules.size() + columns - 1) / columns;
        int contentHeight = rows * (cardH + rowGap);
        maxScroll = Math.max(0, contentHeight - Math.max(1, listBottom - listY));
        scroll = Math.max(0, Math.min(maxScroll, scroll));

        c.enableScissor(mainX, listY, mainX + mainW, listBottom);
        for (int i = 0; i < modules.size(); i++) {
            ModuleCatalog.Module module = modules.get(i);
            int col = i % columns;
            int row = i / columns;
            int x = mainX + col * (cardW + gap);
            int y = listY + row * (cardH + rowGap) - scroll;
            if (y + cardH < listY || y > listBottom) continue;
            drawModuleCard(c, theme, module, x, y, cardW, cardH, mouseX, mouseY, delta);
        }
        c.disableScissor();

        if (modules.isEmpty()) {
            Ui.textCentered(c, textRenderer, "NO MODULES FOUND", mainX + mainW / 2,
                    listY + 45, 0xFF8CA0AF, 0.67f, true);
            Ui.textCentered(c, textRenderer, "Change the search or category filter",
                    mainX + mainW / 2, listY + 62, 0xFF657B8B, 0.53f, false);
        }
        if (maxScroll > 0) drawScrollbar(c, theme, contentHeight);
    }

    private void drawModuleCard(DrawContext c, Theme theme, ModuleCatalog.Module module,
                                int x, int y, int w, int h, int mouseX, int mouseY, float delta) {
        boolean enabled = isEnabled(module);
        boolean over = inside(mouseX, mouseY, x, y, w, h);
        boolean selected = module.id().equals(selectedModuleId);
        if (over) selectedModuleId = module.id();

        float hoverValue = approach(hover.getOrDefault(module.id(), 0f),
                over ? 1f : 0f, Math.min(0.52f, delta * 0.44f));
        float powerValue = approach(power.getOrDefault(module.id(), enabled ? 1f : 0f),
                enabled ? 1f : 0f, Math.min(0.46f, delta * 0.32f));
        hover.put(module.id(), hoverValue);
        power.put(module.id(), powerValue);

        int base = enabled ? 0xC21C2A38 : 0xB1121C28;
        int border = selected ? Ui.alpha(theme.primary(), 0xC0)
                : enabled ? Ui.alpha(theme.primary(), 0x58)
                : Ui.alpha(theme.primary(), Math.round(0x1C + hoverValue * 0x45));
        Ui.glassPanel(c, x, y, x + w, y + h, 9,
                over ? Ui.alpha(theme.primary(), Math.round(0x18 + hoverValue * 0x25)) : base,
                border);

        int accentH = Math.max(4, Math.round((h - 12) * powerValue));
        Ui.roundRect(c, x + 5, y + (h - accentH) / 2, x + 7,
                y + (h + accentH) / 2, 2,
                Ui.alpha(theme.primary(), Math.round(0x32 + powerValue * 0xCD)));

        int iconX = x + 13;
        int iconY = y + 13;
        int iconSize = 28;
        Ui.roundRect(c, iconX, iconY, iconX + iconSize, iconY + iconSize, 7,
                enabled ? Ui.alpha(theme.primary(), 0x42) : 0x78304455);
        Ui.textCentered(c, textRenderer, module.name().isEmpty() ? "?" :
                module.name().substring(0, 1).toUpperCase(Locale.ROOT),
                iconX + iconSize / 2, iconY + 10, enabled ? theme.primary() : 0xFF9CB0BF,
                0.82f, true);

        int right = x + w - 9;
        int settingsW = 24;
        int switchW = 34;
        int textX = iconX + iconSize + 9;
        int textW = Math.max(26, w - (textX - x) - switchW - settingsW - 27);
        Ui.text(c, textRenderer, Ui.fit(textRenderer, module.name(), textW, 0.68f),
                textX, y + 14, enabled ? 0xFFF1F6FA : 0xFFD3DFE7, 0.68f, true);
        if (h > 60) {
            Ui.text(c, textRenderer, Ui.fit(textRenderer, module.description(), textW, 0.48f),
                    textX, y + 33, 0xFF8297A7, 0.48f, false);
        }

        int stateW = 34;
        int switchX = right - settingsW - 7 - switchW;
        int switchY = y + (h - 16) / 2;
        Ui.roundRect(c, switchX, switchY, switchX + stateW, switchY + 16, 8,
                enabled ? Ui.alpha(theme.primary(), Math.round(0x55 + powerValue * 0x48))
                        : 0x90303E4C);
        int knobX = switchX + (int) Math.round(3 + powerValue * 15);
        Ui.roundRect(c, knobX, switchY + 3, knobX + 10, switchY + 13, 5,
                enabled ? 0xFFF4FBFF : 0xFF899AA7);

        int gearX = right - settingsW;
        Ui.roundRect(c, gearX, y + (h - 23) / 2, gearX + 23, y + (h + 23) / 2,
                6, over ? 0xA63C5365 : 0x73253643);
        Ui.textCentered(c, textRenderer, "⋯", gearX + 11, y + h / 2 - 4,
                0xFFB9C8D2, 0.78f, true);

        if (module.kind() == ModuleCatalog.Kind.CYCLE) {
            Ui.textRight(c, textRenderer, "STYLE " + (cfg.style(module.id()) + 1),
                    right, y + h - 7, 0xFF718A9B, 0.43f, true);
        }
        moduleHits.add(new ModuleHit(module, x, y, w, h));
    }

    private void drawInspector(DrawContext c, Theme theme, int mouseX, int mouseY, float delta) {
        ModuleCatalog.Module module = findModule(selectedModuleId);
        if (module == null) return;

        int x = inspectorX + 12;
        int w = inspectorW - 24;
        int y = listY + 4;
        int bottom = listBottom - 4;
        boolean enabled = isEnabled(module);

        Ui.text(c, textRenderer, "MODULE DETAILS", x, y + 2, 0xFF8195A6, 0.53f, true);
        Ui.roundRect(c, x, y + 18, x + w, y + 68, 8, 0x7E263647);
        Ui.roundRect(c, x + 9, y + 29, x + 39, y + 59, 7,
                Ui.alpha(theme.primary(), enabled ? 0x62 : 0x28));
        Ui.textCentered(c, textRenderer, module.name().isEmpty() ? "?" :
                module.name().substring(0, 1).toUpperCase(Locale.ROOT),
                x + 24, y + 39, theme.primary(), 0.88f, true);
        Ui.text(c, textRenderer, Ui.fit(textRenderer, module.name(), w - 56, 0.65f),
                x + 47, y + 31, 0xFFF0F5F9, 0.65f, true);
        Ui.text(c, textRenderer, module.category().toUpperCase(Locale.ROOT),
                x + 47, y + 47, 0xFF849AAA, 0.45f, true);

        int descY = y + 82;
        Ui.text(c, textRenderer, "DESCRIPTION", x, descY, 0xFF7D92A2, 0.49f, true);
        drawWrapped(c, module.description(), x, descY + 14, w, 0xFFB7C5CF, 0.54f, 3);

        int statusY = descY + 78;
        Ui.text(c, textRenderer, "STATUS", x, statusY, 0xFF7D92A2, 0.49f, true);
        Ui.roundRect(c, x, statusY + 13, x + w, statusY + 37, 6,
                enabled ? 0x88305B4E : 0x7B303D4A);
        c.fill(x + 8, statusY + 22, x + 13, statusY + 27,
                enabled ? 0xFF66E6A5 : 0xFF738697);
        Ui.text(c, textRenderer, module.kind() == ModuleCatalog.Kind.CYCLE
                ? "STYLE MODULE" : (enabled ? "ENABLED" : "DISABLED"),
                x + 19, statusY + 21, enabled ? 0xFF9AF0C3 : 0xFF9AAAB7, 0.52f, true);

        int infoY = statusY + 53;
        Ui.text(c, textRenderer, "OPTIONS", x, infoY, 0xFF7D92A2, 0.49f, true);
        String optionInfo = module.hasOptions()
                ? module.options().length + " STYLE PRESETS"
                : "NO EXTRA PRESETS";
        Ui.text(c, textRenderer, optionInfo, x, infoY + 15, 0xFFCAD5DD, 0.55f, false);

        int toggleY = Math.max(infoY + 42, inspectorToggleY);
        if (toggleY + 22 < bottom) {
            boolean overToggle = inside(mouseX, mouseY, x, toggleY, w, 22);
            Ui.roundRect(c, x, toggleY, x + w, toggleY + 22, 6,
                    enabled ? Ui.alpha(theme.primary(), 0x48) : 0x8B2D4050);
            Ui.textCentered(c, textRenderer,
                    module.kind() == ModuleCatalog.Kind.CYCLE ? "CYCLE STYLE"
                            : (enabled ? "DISABLE MODULE" : "ENABLE MODULE"),
                    x + w / 2, toggleY + 8, 0xFFE9F2F7, 0.52f, true);
            if (overToggle) c.fill(x + 7, toggleY + 20, x + w - 7, toggleY + 21,
                    theme.primary());
        }

        int settingsY = Math.max(toggleY + 28, inspectorSettingsY);
        if (settingsY + 20 < bottom) {
            Ui.roundRect(c, x, settingsY, x + w, settingsY + 20, 6, 0x88304455);
            Ui.textCentered(c, textRenderer, "OPEN SETTINGS  ›", x + w / 2,
                    settingsY + 7, 0xFFB9C9D4, 0.49f, true);
        }
    }

    private void drawWrapped(DrawContext c, String message, int x, int y,
                             int maxWidth, int color, float scale, int maxLines) {
        if (message == null || message.isBlank()) return;
        String[] words = message.split("\\s+");
        StringBuilder line = new StringBuilder();
        int lineIndex = 0;
        for (String word : words) {
            String candidate = line.length() == 0 ? word : line + " " + word;
            if (textRenderer.getWidth(candidate) * scale > maxWidth && line.length() > 0) {
                Ui.text(c, textRenderer, line.toString(), x, y + lineIndex * 11, color, scale, false);
                line.setLength(0);
                line.append(word);
                lineIndex++;
                if (lineIndex >= maxLines) return;
            } else {
                if (line.length() > 0) line.append(' ');
                line.append(word);
            }
        }
        if (line.length() > 0 && lineIndex < maxLines) {
            Ui.text(c, textRenderer, line.toString(), x, y + lineIndex * 11, color, scale, false);
        }
    }

    private void drawScrollbar(DrawContext c, Theme theme, int contentHeight) {
        int trackX = mainX + mainW - 2;
        int trackH = listBottom - listY - 8;
        int thumbH = Math.max(18, Math.round(trackH * (trackH / (float) contentHeight)));
        int thumbY = listY + 4 + Math.round((trackH - thumbH) * (scroll / (float) maxScroll));
        Ui.roundRect(c, trackX, listY + 4, trackX + 2, listBottom - 4, 2, 0x503B4D5D);
        Ui.roundRect(c, trackX - 1, thumbY, trackX + 3, thumbY + thumbH, 2,
                Ui.alpha(theme.primary(), 0xD0));
    }

    private void drawFooter(DrawContext c, Theme theme) {
        Ui.text(c, textRenderer, "LMB  TOGGLE     RMB / ⋯  SETTINGS     WHEEL  SCROLL",
                mainX + 1, panelY + panelH - 20, 0xFF718697, 0.48f, true);
        int barW = Math.max(0, Math.min(mainW, Math.round(mainW * easedOpenProgress)));
        if (barW > 0) c.fill(mainX, panelY + panelH - 7,
                mainX + barW, panelY + panelH - 6, Ui.alpha(theme.primary(), 0xC0));
    }

    private List<ModuleCatalog.Module> filteredModules() {
        List<ModuleCatalog.Module> out = new ArrayList<>();
        List<ModuleCatalog.Module> source = selectedCategory.equals("All")
                ? ModuleCatalog.all() : ModuleCatalog.inCategory(selectedCategory);
        String needle = search.trim().toLowerCase(Locale.ROOT);
        for (ModuleCatalog.Module module : source) {
            boolean enabled = isEnabled(module);
            if (filter == Filter.ENABLED && !enabled) continue;
            if (filter == Filter.DISABLED && enabled) continue;
            if (!needle.isEmpty() && !(module.name().toLowerCase(Locale.ROOT).contains(needle)
                    || module.description().toLowerCase(Locale.ROOT).contains(needle)
                    || module.id().toLowerCase(Locale.ROOT).contains(needle))) continue;
            out.add(module);
        }
        return out;
    }

    private ModuleCatalog.Module findModule(String id) {
        if (id == null || id.isEmpty()) return null;
        for (ModuleCatalog.Module module : ModuleCatalog.all()) {
            if (module.id().equals(id)) return module;
        }
        return null;
    }

    private boolean isEnabled(ModuleCatalog.Module module) {
        return module.kind() == ModuleCatalog.Kind.CYCLE || cfg.isOn(module.id());
    }

    private void toggle(ModuleCatalog.Module module) {
        if (module.kind() == ModuleCatalog.Kind.CYCLE) cfg.cycleStyle(module.id());
        else BaroxVsClient.toggleModule(module.id());
        cfg.save();
    }

    private void openSettings(ModuleCatalog.Module module) {
        if (client != null) client.setScreen(new ModuleSettingsScreen(this, cfg, module));
    }

    private static float approach(float current, float target, float factor) {
        return current + (target - current) * Math.max(0.02f, Math.min(1f, factor));
    }

    private static boolean inside(double mx, double my, int x, int y, int w, int h) {
        return mx >= x && mx <= x + w && my >= y && my <= y + h;
    }

    @Override
    public boolean mouseClicked(double mouseX, double mouseY, int button) {
        if (inside(mouseX, mouseY, closeX, closeY, 20, studioH)) {
            close();
            return true;
        }
        if (studioW > 0 && button == 0 &&
                inside(mouseX, mouseY, studioX, studioY, studioW, studioH)) {
            client.setScreen(new BaroxMenuScreen(cfg));
            return true;
        }
        if (button == 0 && inside(mouseX, mouseY, searchX, searchY, searchW, searchH)) {
            searchFocused = true;
            return true;
        }

        searchFocused = false;
        int fx = searchX + searchW + 6;
        int chipW = Math.max(25, (mainW - searchW - 12) / 3);
        if (button == 0 && mouseY >= searchY && mouseY <= searchY + searchH) {
            for (int i = 0; i < Filter.values().length; i++) {
                int x = fx + i * (chipW + 2);
                if (inside(mouseX, mouseY, x, searchY + 1, chipW, searchH - 2)) {
                    filter = Filter.values()[i];
                    scroll = 0;
                    return true;
                }
            }
        }

        if (button == 0) {
            for (CategoryHit hit : categoryHits) {
                if (inside(mouseX, mouseY, hit.x(), hit.y(), hit.w(), hit.h())) {
                    selectedCategory = hit.category();
                    scroll = 0;
                    return true;
                }
            }
        }

        ModuleCatalog.Module selected = findModule(selectedModuleId);
        if (inspectorW > 0 && selected != null) {
            int ix = inspectorX + 12;
            int iw = inspectorW - 24;
            if (button == 0 && inside(mouseX, mouseY, ix, inspectorToggleY, iw, 22)) {
                toggle(selected);
                return true;
            }
            if (button == 0 && inside(mouseX, mouseY, ix, inspectorSettingsY, iw, 20)) {
                openSettings(selected);
                return true;
            }
            int toggleY = Math.max(listY + 4 + 82 + 78 + 53 + 42, inspectorToggleY);
            int settingsY = Math.max(toggleY + 28, inspectorSettingsY);
            if (button == 0 && inside(mouseX, mouseY, ix, toggleY, iw, 22)) {
                toggle(selected);
                return true;
            }
            if (button == 0 && inside(mouseX, mouseY, ix, settingsY, iw, 20)) {
                openSettings(selected);
                return true;
            }
        }

        for (ModuleHit hit : moduleHits) {
            if (!inside(mouseX, mouseY, hit.x(), hit.y(), hit.w(), hit.h())) continue;
            selectedModuleId = hit.module().id();
            if (button == 1) {
                openSettings(hit.module());
                return true;
            }
            if (button == 0) {
                int settingsLeft = hit.x() + hit.w() - 33;
                if (mouseX >= settingsLeft) openSettings(hit.module());
                else toggle(hit.module());
                return true;
            }
        }
        return super.mouseClicked(mouseX, mouseY, button);
    }

    @Override
    public boolean mouseScrolled(double mouseX, double mouseY,
                                 double horizontalAmount, double verticalAmount) {
        if (mouseX >= mainX && mouseX <= mainX + mainW
                && mouseY >= listY && mouseY <= listBottom && maxScroll > 0) {
            scroll = Math.max(0, Math.min(maxScroll,
                    scroll - (int) Math.round(verticalAmount * 42)));
            return true;
        }
        return super.mouseScrolled(mouseX, mouseY, horizontalAmount, verticalAmount);
    }

    @Override
    public boolean charTyped(char chr, int modifiers) {
        if (searchFocused && !Character.isISOControl(chr) && search.length() < 40) {
            search += chr;
            scroll = 0;
            return true;
        }
        return super.charTyped(chr, modifiers);
    }

    @Override
    public boolean keyPressed(int keyCode, int scanCode, int modifiers) {
        if (keyCode == GLFW.GLFW_KEY_ESCAPE) {
            if (searchFocused) {
                searchFocused = false;
                return true;
            }
            close();
            return true;
        }
        if (searchFocused && keyCode == GLFW.GLFW_KEY_BACKSPACE && !search.isEmpty()) {
            search = search.substring(0, search.length() - 1);
            scroll = 0;
            return true;
        }
        if (!searchFocused && keyCode == GLFW.GLFW_KEY_SLASH) {
            searchFocused = true;
            return true;
        }
        if (searchFocused && keyCode == GLFW.GLFW_KEY_ENTER) {
            searchFocused = false;
            return true;
        }
        return super.keyPressed(keyCode, scanCode, modifiers);
    }

    @Override
    public void close() {
        cfg.save();
        if (client != null) client.setScreen(null);
    }
}
'''
write("src/main/java/com/baroxvs/client/gui/ModuleClickGuiScreen.java", gui)
print("Applied v026: redesigned client-style GUI with sidebar, status header, animated module cards/switches, search filters, settings inspector and phone-responsive layout.")
