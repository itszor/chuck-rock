/* Chuck Rock (Core Design, 1991; Archimedes conversion by Krisalis - Andy
 * Ware with Shaun Hollingworth): what libroger needs to know about the game.
 *
 * !Run sets Chuck$Dir, RMLoads TequeMemory (MemMod: *TequeMem, which only
 * frees memory; nothing here calls it) and MusicModule 1.02 (MUSMOD2: a
 * tracker player that also plays the sound effects), selects MODE 9 and
 * runs ChuckProg, the loader: it shows the Krisalis logo (KRIS) and the
 * intro sequence (CHSEQ1-4), then copies a stub to &28800 that loads GAME
 * at &8000 and jumps to it. GAME loads each level's files from
 * <Chuck$Dir>.CHUCK (the hard disc installation, ../tools/install.py) and
 * carries the Amiga original's planar graphics, which it converts.
 *
 * The translated images: GAME (gen/), ChuckProg (genprog/), MusicModule
 * (genmus/, for its RMA address &1800000) and each level's code (genlevel1-5/,
 * all for &25928). */
#include <dirent.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>
#include <roger.h>

extern const struct roger_image recomp_image, recompP_image, recompM_image;   /* gen{,prog,mus}/entries.c */
extern const struct roger_image recompL1_image, recompL2_image, recompL3_image, recompL4_image,
    recompL5_image;                                                           /* genlevel1-5/entries.c */

#define APP "../game/!Chuck"
static const char *const vars[] = {"Chuck$Dir", "!Chuck", NULL};
static const char *const prefixes[] = {"<Obey$Dir>.", NULL};
/* A level's code (CHUCK.CODE1-5) is crunched: GAME loads it into its buffer
 * at &4BF78 and unpacks it to &25928, just past its own end (../tools/unpack.py),
 * then calls it through its objects' handler fields. Loading it selects that
 * level's translation, an overlay. */
#define LEVEL_BUFFER 0x4BF78
static const struct roger_program programs[] = {
    {"GAME", &recomp_image, 0, 0},
    {"CODE1", &recompL1_image, 1, LEVEL_BUFFER},
    {"CODE2", &recompL2_image, 1, LEVEL_BUFFER},
    {"CODE3", &recompL3_image, 1, LEVEL_BUFFER},
    {"CODE4", &recompL4_image, 1, LEVEL_BUFFER},
    {"CODE5", &recompL5_image, 1, LEVEL_BUFFER},
    {NULL, NULL, 0, 0}};
static struct roger_module modules[] = {{"MUSMOD2", &recompM_image, 0}, {NULL, NULL, 0}};

/* ChuckProg's last act: the stub it copies to &28800 (from &B1B4) loads
 * GAME over itself at &8000 and jumps there. It is a handful of
 * instructions, interpreted. */
static const uint32_t interpreted[] = {0x28800, 0x28840, 0, 0};

/* --level=N: a new game starts at level N. GAME's new-game settings are a
 * table of (address, size, value) (&D370; &D318 applies it): the level,
 * the byte at &8007, starts as 1 (&D3B0). */
#define LEVEL_SETTING 0xD3B8
static int start_level;

static int arg(const char *a)
{
    if (!strncmp(a, "--level=", 8) && atoi(a + 8) >= 1 && atoi(a + 8) <= 5) start_level = atoi(a + 8);
    else return 0;
    return 1;
}

static void frame(void)
{
    if (start_level && roger_current_image() == &recomp_image && *(uint32_t *)(MEM + LEVEL_SETTING) == 1)
        *(uint32_t *)(MEM + LEVEL_SETTING) = start_level;
}

/* a file in !Chuck, whatever ,load-exec suffix the extraction gave it (the
 * discs' and the zip's differ) */
static const char *in_app(const char *leaf)
{
    DIR *d = opendir(APP);
    struct dirent *e;
    char *path = NULL;
    while (d && !path && (e = readdir(d)))
        if (strcspn(e->d_name, ",") == strlen(leaf) && !strncasecmp(e->d_name, leaf, strlen(leaf))) {
            path = malloc(strlen(APP) + strlen(e->d_name) + 2);
            sprintf(path, "%s/%s", APP, e->d_name);
        }
    if (d) closedir(d);
    if (!path) { fprintf(stderr, "no %s/%s: build.sh extracts it\n", APP, leaf); exit(1); }
    return path;
}

static struct roger_config config = {
    .title = "Chuck Rock (recompiled)",
    /* the keys (the Read_Me): Z/X left/right, P up (jump), L down, Space
     * fire; F1 pauses */
    .pad_map = "left=Z,right=X,up=P,down=L,a=Space,b=P,start=F1",
    .image = &recompP_image,
    .programs = programs,
    .modules = modules,
    .appdir = "../game",
    .dir_prefixes = prefixes,
    .variables = vars,
    .command_line = "<Chuck$Dir>.ChuckProg 8000",
    .initial_mode = 9,
    .wimpslot = 464 * 1024,
    .interpreted = interpreted,
    .frame = frame,
    .arg = arg,
    .usage = "  --level=N         a new game starts at level N (1-5)\n",
};

int main(int argc, char **argv)
{
    config.image_path = in_app("ChuckProg");
    modules[0].path = in_app(modules[0].path);
    roger_main(argc, argv, &config);
}
