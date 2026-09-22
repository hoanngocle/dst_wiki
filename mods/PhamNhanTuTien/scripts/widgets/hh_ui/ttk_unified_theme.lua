local Theme = {
    font = TTK_FORGE_SERIF or BODYTEXTFONT or UIFONT,
    shell = { width = 1480, height = 860, scale = .82 },
    content = { width = 1380, height = 690, y = -48 },
    colours = {
        backdrop = { .018, .016, .035, .985 },
        panel = { .055, .050, .085, .98 },
        silver = { .76, .79, .88, 1 },
        silver_dim = { .30, .32, .40, 1 },
        purple = { .61, .40, .92, 1 },
        purple_soft = { .78, .66, .98, 1 },
        text = { .91, .92, .98, 1 },
        muted = { .62, .64, .72, 1 },
        locked = { .42, .42, .50, 1 },
    },
}

return Theme
