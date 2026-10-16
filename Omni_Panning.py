# =============================================================================
# OMNI PANNING -- Gold Panning for Beyond Sosaria (TazUO + RazorEnhanced)
# =============================================================================
#
# Press Start and it pans for gold, town after town, from the runes every Account Runebook comes
# with (Trammel > Cities). It walks out along the shore to fresh water, unloads at a bank or your own
# chest, keeps a Gold Pan in hand, and fills and turns in Harry Johnson's Gold Panning Orders in Minoc.
# Several characters can run it at once from the same Scripts folder; they share what they learn and
# keep out of each other's water.
#
# WHAT YOU NEED
#   * This file in your RazorEnhanced Scripts folder. That is the whole thing -- no other files.
#     Rename it if you like; it creates its own data folder named to match.
#   * The Account Runebook ([ar) your account started with. Its Trammel > Cities folder is the route.
#   * A Gold Pan in your backpack -- or Tinkering to make one: the script buys Tinker's Tools and
#     iron ingots from a tinker in town when it needs them (the vendor takes the gold from your
#     pack or your bank).
#   * Mana to recall with.
#   * For Gold Panning Orders: a rune named PO beside Harry Johnson, the Gold Panner, in Minoc, at the
#     top of your book or one folder down. Without one, the first start walks to Harry from the Minoc
#     rune in Trammel > Cities and marks it -- if your book no longer has that Minoc rune, mark your
#     own PO rune beside Harry.
#   * Optional: a rune named Home beside a chest of yours, to unload there instead of the bank.
#   * Optional: a Sosarian Ethereal in your backpack with its bank unlocked -- the bank opens where
#     you stand, no trip to a banker.
#
# USING IT
#   Press Play. A short screen shows what it found; press Start. Later runs skip that screen.
#   The small panning window shows what it is doing; its Options button opens the options.
#
# MARK YOUR OWN RUNES
#   The town runes are the same for every player, so everyone running this script competes for the
#   same easy water. Mark your own runes beside quiet, safe water -- away from towns and monster
#   spawns -- in a folder named Panning at the top of your Account Runebook (the same folder the
#   script marks its own runes in; make it yourself if it is not there yet). They join the route at
#   the next start, or at Options > Rescan, and keep you clear of the crowd.
#
# OPTIONS
#   * Fill Gold Panning Orders at Harry -- on by default; needs the PO rune (see above).
#   * Mark new runes where gold turns up -- on by default; only ever in a folder named Panning.
#   * Stay out of Town Invasions -- on by default.
#   * Set working chest -- target a chest at home; with a rune named Home, everything panned goes
#     there instead of the bank. Use the bank -- back to the bank.
#   * Rescan -- read your Account Runebook again after you add or move a rune.
#   * How full the pack gets before it unloads: pack_pct in Setup.txt (80 = 80% of your weight, the default).
#
# HOW IT WORKS
#   * Each rune: it looks for water near the rune, then walks out along the shore -- up to 150 tiles
#     -- for water nobody has panned. Emptied water rests 20 minutes. A rune that pays nothing three
#     visits running is passed over (delete RuneStats.txt in the data folder to give them another
#     chance).
#   * New runes: where it finds gold 20+ tiles from every rune you have, it marks one in the
#     Panning folder, which it makes the first time.
#   * It learns the water: a kind of water the shard refuses three times is not tried again, and the
#     water that pays is tried first. A pan the server never answers is given up after 1.5 seconds.
#   * Unloading: at a banker (it remembers which towns have one), your Sosarian Ethereal, or your
#     working chest -- nuggets, bricks, rough stone, gems, and anything else that came into the pack
#     since it started, except pans, kits, ingots, orders and gold. Bank checks go to the bank
#     together after the turn-ins. Panning goods and orders already in your pack when you press
#     Start are handled like its own -- unloaded, filled, turned in -- but an Epic item is left alone.
#   * Gold Panning Orders: nuggets stay in the pack. When it fills, they go into the carried orders
#     of their size where it stands; a pack still full goes to Harry, who trades nuggets up, takes
#     every order it can FINISH (never a partial) and gives the next. The orders paying the most
#     rough stone a nugget go first. Harry hands out a new order every 30 minutes.
#   * Long walks: with an ethereal mount statue in the pack it rides any walk over 40 tiles.
#   * Safety: lost hits, poison, or a red or orange mobile near, and it leaves for the next rune;
#     that spot goes on a list no panner walks within 30 tiles of again. Town Invasions start every
#     even hour UTC in Cove, Delucia, Jhelom, Minoc,
#     Moonglow, Skara Brae, Umbra or Yew: from shortly before each start it keeps out of all eight
#     and takes no trip that would land in one, until the shard names the town, then keeps out of
#     that one until it is saved.
#   * Several panners: each keeps 40 tiles from the water another has panned in the last 3 hours,
#     from its runes and from where it works -- the towns are shared, the shores are not. A new
#     panner whose Home rune stands by another's working chest shares that chest.
#
# =============================================================================

import os
import re
import time

SCRIPT_TITLE = "Omni Panning"

HUE_GOOD = 68
HUE_BAD = 33


def log(msg, hue=HUE_GOOD):
    Misc.SendMessage("[Pan] " + msg, hue)
    try:
        if ensure_char_dir():
            with open(char_path("Log_%s.txt" % time.strftime("%Y_%m_%d")), "a") as f:
                f.write("%s %s\n" % (time.strftime("%H:%M:%S"), msg))
    except Exception:
        pass


LOG_KEEP_DAYS = 14             # the daily logs older than this are deleted at each start


def prune_logs():
    cutoff = time.time() - LOG_KEEP_DAYS * 86400
    for folder in (data_dir(), char_dir()):
        try:
            for name in os.listdir(folder):
                if name.startswith("Log_") and name.endswith(".txt"):
                    path = os.path.join(folder, name)
                    if os.path.getmtime(path) < cutoff:
                        os.remove(path)
        except Exception:
            pass


# =============================================================================
# DATA FOLDER AND SETTINGS -- the folder is named after this file, beside it.
# =============================================================================

def data_dir():
    here = os.path.abspath(__file__)
    return os.path.join(os.path.dirname(here), os.path.splitext(os.path.basename(here))[0])


def data_path(name):
    return os.path.join(data_dir(), name)


def ensure_data_dir():
    try:
        if not os.path.isdir(data_dir()):
            os.makedirs(data_dir())
        return True
    except Exception:
        return False


# EACH PANNER ITS OWN (owner, 2026-10-15 10:4x: "Let's plan for coordinated use between multiple accounts using the same
# file structure"). Several characters can run this script from one Scripts folder. What is the character's own -- its
# options, where its book keeps its PO and Home runes, its Harry timer, its log -- is kept in a folder of its own inside
# the data folder; what is true for every panner -- the towns' vendors, the dangerous runes, the invaded towns, the
# runes' finds, the working chests, the marked spots, who works where -- stays beside it, shared.
def char_tag():
    try:
        return "%s_0x%X" % (re.sub(r"[^A-Za-z0-9]+", "", Player.Name or "") or "Panner", Player.Serial)
    except Exception:
        return "Panner"


def char_dir():
    return os.path.join(data_dir(), char_tag())


def char_path(name):
    return os.path.join(char_dir(), name)


def ensure_char_dir():
    try:
        if not os.path.isdir(char_dir()):
            os.makedirs(char_dir())
        return True
    except Exception:
        return False


def my_id():
    try:
        return "0x%X" % Player.Serial
    except Exception:
        return "?"


SETTINGS_FILE = "Setup.txt"
SETTINGS = {}
DEFAULTS = {
    "orders": "1", "avoid_invasions": "1", "mark_runes": "1",
    "pack_pct": "80", "po_path": "",     # (owner, 2026-10-16: panning fills a find at a time, no bursts)
    "started": "0",                 # Start pressed once: every later run skips the start screen
    "chest": "", "home_path": "",   # THE WORKING CHEST: its serial, and where the Home rune was found
    "bank_goods": "1",              # ... the bank's nuggets at its last look, "small:12,large:3" ("1": not looked yet)
    "eth_bank": "",                 # THE ETHEREAL'S BANK, known in advance: "1" unlocked, "0" not, "" never read
}


def load_settings():
    SETTINGS.clear()
    SETTINGS.update(DEFAULTS)
    if not os.path.exists(char_path(SETTINGS_FILE)) and os.path.exists(data_path(SETTINGS_FILE)) and ensure_char_dir():
        for name in (SETTINGS_FILE, "OrderAsk.txt"):      # the one panner before EACH PANNER ITS OWN: its files move in
            try:
                if os.path.exists(data_path(name)):
                    os.rename(data_path(name), char_path(name))
            except Exception:
                pass
    try:
        with open(char_path(SETTINGS_FILE), "r") as f:
            for line in f:
                if "=" in line:
                    k, _s, v = line.strip().partition("=")
                    if k.strip():
                        SETTINGS[k.strip()] = v.strip()
    except Exception:
        pass


def save_settings():
    if not ensure_char_dir():
        log("Could not create '%s' -- options will not be remembered." % char_dir(), HUE_BAD)
        return False
    try:
        with open(char_path(SETTINGS_FILE), "w") as f:
            for k in sorted(k for k in SETTINGS if k in DEFAULTS):   # an older version's keys are dropped
                f.write("%s=%s\n" % (k, SETTINGS[k]))
        return True
    except Exception as err:
        log("Could not save options (%s)." % err, HUE_BAD)
        return False


def opt(key):
    return SETTINGS.get(key, DEFAULTS.get(key, "")) == "1"


def opt_int(key, lo, hi):
    try:
        return max(lo, min(hi, int(SETTINGS.get(key) or DEFAULTS[key])))
    except Exception:
        return int(DEFAULTS[key])


# =============================================================================
# JOURNAL -- read by RazorEnhanced's own clock: the newest stamp taken before an action, then the
# lines after it (RazorEnhanced keeps 100 lines, so a count stops working once the buffer is full).
# =============================================================================

def newest_journal_timestamp():
    try:
        stamps = [getattr(e, "Timestamp", None) for e in (Journal.GetJournalEntry(None) or [])]
        stamps = [s for s in stamps if s is not None]
        return max(stamps) if stamps else 0.0
    except Exception:
        return 0.0


def journal_lines_after(stamp):
    out = []
    try:
        for e in (Journal.GetJournalEntry(stamp) or []):
            if (getattr(e, "Timestamp", 0.0) or 0.0) > stamp:
                out.append(e)
    except Exception:
        pass
    return out


def journal_texts_after(stamp):
    return [(getattr(e, "Text", "") or "").strip() for e in journal_lines_after(stamp)]


def wait_for_gump_present(gump_id, timeout_ms):
    t0 = time.time()
    while True:
        try:
            if Gumps.HasGump(gump_id):
                return int((time.time() - t0) * 1000)
        except Exception:
            pass
        if (time.time() - t0) * 1000 >= timeout_ms:
            return None
        Misc.Pause(50)


# =============================================================================
# SMALL HELPERS
# =============================================================================

def name_of(thing):
    try:
        n = (thing.Name or "").strip()
    except Exception:
        n = ""
    if not n:
        try:
            Items.WaitForProps(thing.Serial, 1000)
            props = Items.GetPropStringList(thing.Serial) or []
            n = (props[0] if props else "").strip()
        except Exception:
            pass
    return n


def pack_items():
    try:
        return list(Player.Backpack.Contains or [])
    except Exception:
        return []


def here():
    p = Player.Position
    return int(p.X), int(p.Y), int(p.Z)


def cheb(ax, ay, bx, by):
    return max(abs(ax - bx), abs(ay - by))


def clear_cursor():
    try:
        Target.ClearQueue()
    except Exception:
        pass
    if Target.HasTarget():
        Target.Cancel()
        Misc.Pause(200)


def pack_full(pct=None):
    """Over the weight threshold (`pct`, else the setting), or the item count over the same share of the pack's limit."""
    pct = (opt_int("pack_pct", 20, 95) if pct is None else pct) / 100.0
    try:
        if Player.MaxWeight and Player.Weight > Player.MaxWeight * pct:
            return True
    except Exception:
        pass
    try:
        for prop in Items.GetPropStringList(Player.Backpack.Serial) or []:
            if "contents" in prop.lower():
                nums = [int(x) for x in re.findall(r"\d+", prop)]
                if len(nums) >= 2 and nums[1] and nums[0] > nums[1] * pct:
                    return True
    except Exception:
        pass
    return False


WORLD_NAMES = {0: "Felucca", 1: "Trammel", 2: "Ilshenar", 3: "Malas", 4: "Tokuno", 5: "TerMur"}


def world_label(name):
    m = re.search(r"\(([^()]+)\)\s*$", name or "")
    return m.group(1).replace(" ", "").lower() if m else ""


def base_name(name):
    return re.sub(r"\s*\([^()]*\)\s*$", "", name or "").strip()


# =============================================================================
# ACCOUNT RUNEBOOK -- the shard's [ar book. Entry buttons 10-499; a row's gate is +30000 and its
# delete +60000 (never sent from here). New Rune (1) and New Runebook (3) ask for a name by prompt.
# =============================================================================

AR_GUMPID = 0xc395adb4
AR_COMMAND = "[ar"
AR_NEXT_PAGE_BUTTON = 504
AR_PREV_PAGE_BUTTON = 503
AR_ROOT_BUTTON = 5
AR_NEW_RUNE_BUTTON = 1
AR_NEW_FOLDER_BUTTON = 3
AR_CONTROL_BUTTONS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 500, 503, 504]
AR_ENTRY_BUTTON_MIN = 10
AR_ENTRY_BUTTON_MAX = 499
AR_GATE_OFFSET = 30000
AR_MAX_PAGES = 30
AR_GUMP_WAIT_MS = 5000
MARK_REFUSED_TEXT = "thy spell doth not appear to work"
MIN_MANA_TO_TRAVEL = 20
MSG_NO_MANA = ("insufficient mana", "you don't have enough mana", "you lack the mana")
CITY_FOLDER = ["Trammel", "Cities"]   # every account's book starts with it
OWN_FOLDER = "Panning"                 # the script's own runes -- made on the first mark, never anywhere else
PO_RUNE_NAMES = ("po",)                # Harry's rune, at the top of the book or one folder down


def ar_lines():
    try:
        return Gumps.GetLineList(AR_GUMPID, False) or []
    except TypeError:
        return Gumps.GetLineList(AR_GUMPID) or []
    except Exception:
        return []


def openAR():
    if Gumps.HasGump(AR_GUMPID):
        return True
    Player.ChatSay(0, AR_COMMAND)
    wait_for_gump_present(AR_GUMPID, AR_GUMP_WAIT_MS)
    Misc.Pause(250)
    return bool(Gumps.GetGumpRawLayout(AR_GUMPID))


def ar_buttons():
    if not openAR():
        return []
    layout = Gumps.GetGumpRawLayout(AR_GUMPID)
    out = []
    for piece in re.split(r"\}\s*\{", str(layout or "")):
        if "button" in piece.lower():
            nums = re.findall(r"\d+", piece)
            if nums:
                out.append(int(nums[-1]))
    return out


def ar_page_info():
    for line in reversed(list(ar_lines())):
        m = re.search(r"Page\s+(\d+)\s*/\s*(\d+)", line or "", re.I)
        if m:
            return int(m.group(1)), int(m.group(2))
    return 1, 1


def ar_parse_page():
    """({button: folder name}, {button: {"name", "coord"}}) of the open page, or ({}, {}) on a mismatched read."""
    if not openAR():
        return {}, {}
    lines = ar_lines()
    buttons = ar_buttons()
    entry_buttons = sorted(b for b in buttons if AR_ENTRY_BUTTON_MIN <= b <= AR_ENTRY_BUTTON_MAX
                           and b not in AR_CONTROL_BUTTONS)
    entries = []
    for line in lines:
        text = (line or "").strip()
        if not text or text.startswith("<"):
            continue
        if re.match(r"^\(\s*[-+]?\d", text):
            if entries:
                entries[-1]["coord"] = [int(x) for x in re.findall(r"[-+]?\d+", text)]
            continue
        m = re.match(r"^(\d+)\.\s*(.+)$", text)
        if m:
            entries.append({"label": m.group(2).strip(), "coord": None})
    if len(entries) != len(entry_buttons):
        return {}, {}
    folders, dests = {}, {}
    for entry, button in zip(entries, entry_buttons):
        if entry["coord"] is not None or (button + AR_GATE_OFFSET) in buttons:
            dests[button] = {"name": entry["label"], "coord": entry["coord"]}
        else:
            folders[button] = entry["label"]
    return folders, dests


def ar_step(button):
    if button not in ar_buttons():
        return False
    Gumps.SendAction(AR_GUMPID, button)
    wait_for_gump_present(AR_GUMPID, AR_GUMP_WAIT_MS)
    Misc.Pause(300)
    return True


def ar_goto_page(target):
    current, total = ar_page_info()
    target = max(1, min(target, total))
    for _ in range(AR_MAX_PAGES * 2):
        if current == target:
            return True
        if not ar_step(AR_NEXT_PAGE_BUTTON if current < target else AR_PREV_PAGE_BUTTON):
            return False
        current, total = ar_page_info()
    return current == target


def ar_iter_pages():
    if not openAR():
        return
    ar_goto_page(1)
    for _ in range(AR_MAX_PAGES):
        current, total = ar_page_info()
        folders, dests = ar_parse_page()
        yield current, folders, dests
        if current >= total or not ar_step(AR_NEXT_PAGE_BUTTON):
            return
        if ar_page_info()[0] <= current:
            return


def ar_go_root():
    if not openAR():
        return False
    if AR_ROOT_BUTTON in ar_buttons():
        Gumps.SendAction(AR_GUMPID, AR_ROOT_BUTTON)
        wait_for_gump_present(AR_GUMPID, AR_GUMP_WAIT_MS)
        Misc.Pause(300)
    return True


def ar_enter_folder(name, quiet=False):
    wanted = (name or "").strip().lower()
    for page, folders, _d in ar_iter_pages():
        for button, label in sorted(folders.items()):
            if (label or "").strip().lower() == wanted:
                return ar_step(button)
    if not quiet:
        log("Account Runebook folder '%s' not found." % name, HUE_BAD)
    return False


def ar_go_folders(path, quiet=False):
    if not ar_go_root():
        return False
    for folder in path:
        if not ar_enter_folder(folder, quiet):
            return False
    return True


def ar_folder_runes(path, quiet=False):
    """[{"name", "coord", "page", "button", "path"}] of every rune in the folder at `path`."""
    if not ar_go_folders(path, quiet):
        return []
    out = []
    for page, _f, dests in ar_iter_pages():
        for button, d in sorted(dests.items()):
            out.append({"name": d["name"], "coord": d["coord"], "page": page, "button": button, "path": list(path)})
    return out


def ar_new_entry(button, name):
    """New Rune (1) or New Runebook (3) on the open page, named `name`. True once the name prompt is answered."""
    if button not in (AR_NEW_RUNE_BUTTON, AR_NEW_FOLDER_BUTTON) or button not in ar_buttons():
        return False
    Misc.ResetPrompt()
    stamp = newest_journal_timestamp()
    Gumps.SendAction(AR_GUMPID, button)
    until = time.time() + AR_GUMP_WAIT_MS / 1000.0
    while time.time() < until:
        if Misc.WaitForPrompt(250):
            Misc.ResponsePrompt(name)
            wait_for_gump_present(AR_GUMPID, AR_GUMP_WAIT_MS)
            Misc.Pause(500)
            return True
        if any(MARK_REFUSED_TEXT in t.lower() for t in journal_texts_after(stamp)):
            log("The shard refused a rune here -- nothing marked.", HUE_BAD)
            return False
    log("No name prompt came -- nothing made.", HUE_BAD)
    return False


def ensure_own_folder():
    """Into the Panning folder, making it at the top of the book the first time. True there."""
    if ar_go_folders([OWN_FOLDER], quiet=True):
        return True
    if not ar_go_root() or not ar_new_entry(AR_NEW_FOLDER_BUTTON, OWN_FOLDER):
        log("Could not make the '%s' folder in your Account Runebook." % OWN_FOLDER, HUE_BAD)
        return False
    log("Made a '%s' folder in your Account Runebook for the runes this script marks." % OWN_FOLDER)
    return ar_go_folders([OWN_FOLDER])


def ensure_mana():
    if Player.Mana >= MIN_MANA_TO_TRAVEL:
        return True
    log("Mana %d -- meditating before the recall." % Player.Mana)
    deadline = time.time() + 90
    while time.time() < deadline and Player.Mana < min(Player.ManaMax, MIN_MANA_TO_TRAVEL + 20):
        if Player.IsGhost:
            return False
        try:
            Player.UseSkill("Meditation")
        except Exception:
            pass
        Misc.Pause(2500)
    return Player.Mana >= MIN_MANA_TO_TRAVEL


def recall_button(button, what, coord=None):
    """Press a rune's row on the open page and see us land. True once we stand somewhere else (and near the
    rune's own spot when the book showed it)."""
    if not ensure_mana():
        log("Not enough mana to recall to %s." % what, HUE_BAD)
        return False
    for attempt in (1, 2):
        start, start_map = here(), Player.Map
        stamp = newest_journal_timestamp()
        Gumps.SendAction(AR_GUMPID, button)
        t0 = time.time()
        while time.time() - t0 < 5.0:
            Misc.Pause(200)
            pos = here()
            if Player.Map != start_map or cheb(pos[0], pos[1], start[0], start[1]) > 8:
                Misc.Pause(500)
                pos = here()
                if coord and len(coord) >= 2 and Player.Map == start_map and cheb(pos[0], pos[1], coord[0], coord[1]) > 30:
                    log("Recalled toward %s but stood at %d,%d -- not its spot." % (what, pos[0], pos[1]), HUE_BAD)
                    return False
                return True
            if coord and len(coord) >= 2 and cheb(pos[0], pos[1], coord[0], coord[1]) <= 3:
                return True              # already there
            texts = " ".join(journal_texts_after(stamp)).lower()
            if any(m in texts for m in MSG_NO_MANA):
                break
        if attempt == 1:
            ensure_mana()
            if not openAR():
                return False
    log("The recall to %s did not land." % what, HUE_BAD)
    return False


def recall_rune(rune):
    """Recall to a rune read from the book. None when the folder changed under us (the route is read again)."""
    pos = here()
    c = rune.get("coord") or []
    if len(c) >= 2 and cheb(pos[0], pos[1], c[0], c[1]) <= 3 and world_label(rune["name"]) in (
            "", WORLD_NAMES.get(Player.Map, "").lower()):
        return True                      # standing on it
    if not ar_go_folders(rune["path"]):
        return False
    if not ar_goto_page(rune["page"]):
        return False
    _f, dests = ar_parse_page()
    d = dests.get(rune["button"])
    if d is None or d["name"] != rune["name"]:
        return None
    return recall_button(rune["button"], rune["name"], rune["coord"])


def mark_rune(name):
    """New Rune in the Panning folder, named `name`, at our own tile. Only ever in the Panning folder."""
    if not ensure_own_folder():
        return False
    if ar_new_entry(AR_NEW_RUNE_BUTTON, name):
        log("Marked a new rune '%s' at %d,%d in your %s folder." % ((name,) + here()[:2] + (OWN_FOLDER,)))
        return True
    return False


# =============================================================================
# VENDORS -- a town's banker and tinker are found where they stand, and remembered by town.
# =============================================================================

VENDOR_SEEK_TILES = 18         # a vendor this near the town's rune counts
VENDOR_LOOK_S = 4              # ... looked for this long after landing (the town's people arrive a moment after us)
VENDOR_REACH_TILES = 3         # walked to within this for a purchase
BANK_SPEECH_TILES = 12         # a banker answers "bank" from this far -- no walk needed (one behind his counter could
                               # not be walked to, 10-15 01:26, and the bank stop failed)
VENDOR_TRIES = 5               # towns tried for one, a trip
VENDOR_FILE = "Vendors.txt"
VENDORS = {}                   # (kind, rune name) -> True / False
SERVICE_WORDS = {"bank": ["banker"], "tinker": ["tinker"]}
SERVICE_FIRST = {"bank": ("britain", "vesper", "trinsic", "magincia"), "tinker": ("minoc", "britain", "vesper")}


SERVICE_RUNE_WORDS = {"bank": "Bank", "tinker": "Tinker"}   # THE VENDOR'S OWN RUNE (owner, 2026-10-15 09:2x): the first
                               # time a town's banker or tinker is found, "Bank <town>" / "Tinker <town>" is marked
                               # beside him in the Panning folder, and later trips recall there -- never panned


def service_rune_name(kind, town_rune):
    return "%s %s" % (SERVICE_RUNE_WORDS[kind], base_name(town_rune["name"]))


def is_service_rune(rune):
    low = base_name(rune["name"]).lower()
    return any(low.startswith(w.lower() + " ") for w in SERVICE_RUNE_WORDS.values())


def service_rune(kind, town_rune):
    want = service_rune_name(kind, town_rune).lower()
    return next((r for r in OWN_RUNES if base_name(r["name"]).lower() == want), None)


def mark_service_rune(kind, town_rune):
    """The rune beside the vendor just found, once a town -- "Bank Britain", "Tinker Minoc"."""
    if service_rune(kind, town_rune) is not None or hostiles_near():
        return
    name = service_rune_name(kind, town_rune)
    if mark_rune(name):
        x, y, _z = here()
        OWN_RUNES.append({"name": "%s (%s)" % (name, WORLD_NAMES.get(Player.Map, "")), "coord": [x, y], "page": 0,
                          "button": 0, "path": [OWN_FOLDER]})
        ROUTE_STALE[0] = True


VENDOR_SPOTS = {}              # (kind, rune name) -> (x, y, z) where he stood when last found -- walked to when the
                               # town's rune is too far from him to see him (06:33: Britain's banker out of sight)


def load_vendors():
    VENDORS.clear()
    VENDOR_SPOTS.clear()
    try:
        with open(data_path(VENDOR_FILE)) as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 3:
                    VENDORS[(p[0], p[1])] = p[2] == "yes"
                if len(p) >= 4 and p[3]:
                    try:
                        VENDOR_SPOTS[(p[0], p[1])] = tuple(int(v) for v in p[3].split(","))[:3]
                    except ValueError:
                        pass
    except Exception:
        pass


def save_vendors():
    if not ensure_data_dir():
        return
    try:
        with open(data_path(VENDOR_FILE), "w") as f:
            for (kind, name), ok in sorted(VENDORS.items()):
                spot = VENDOR_SPOTS.get((kind, name))
                f.write("%s\t%s\t%s\t%s\n" % (kind, name, "yes" if ok else "no",
                                                ",".join(str(v) for v in spot) if spot else ""))
    except Exception:
        pass


NOT_A_SHOP = ("guildmaster", "guildmistress")   # a guild's master shares the trade's name and sells nothing


def find_vendors(words, rng=12, shop=False):
    """Mobiles within `rng` whose name or title holds one of `words`, nearest first. `shop`: only a shopkeeper --
    never a guildmaster or guildmistress, and Buy on his menu."""
    f = Mobiles.Filter()
    f.Enabled = True
    f.RangeMax = rng
    out = []
    for mob in Mobiles.ApplyFilter(f) or []:
        text = (mob.Name or "").lower()
        if shop or not any(w in text for w in words):
            try:
                Mobiles.WaitForProps(mob.Serial, 2000)
                text = (text + " " + " ".join(Mobiles.GetPropStringList(mob.Serial) or [])).lower()
            except Exception:
                pass
        if not any(w in text for w in words):
            continue
        if shop and (any(w in text for w in NOT_A_SHOP) or not sells(mob)):
            continue
        out.append(mob)
    out.sort(key=lambda m: Player.DistanceTo(m))
    return out


def sells(mob):
    """True when the mobile's menu offers Buy."""
    try:
        try:
            entries = Misc.WaitForContext(mob.Serial, 3000, False)
        except TypeError:
            entries = Misc.WaitForContext(mob.Serial, 3000)
        return any(((getattr(e, "Entry", None) or str(e)) or "").strip().lower() == "buy" for e in entries or [])
    except Exception:
        return False


def context_pick(serial, wanted):
    try:
        entries = Misc.WaitForContext(serial, 5000, False)
    except TypeError:
        entries = Misc.WaitForContext(serial, 5000)
    for e in entries or []:
        label = getattr(e, "Entry", None) or str(e)
        if (label or "").strip().lower() == wanted:
            Misc.ContextReply(serial, label)
            Misc.Pause(800)
            return True
    return False


def approach(mob, reach=VENDOR_REACH_TILES):
    """Within `reach` of `mob`: walked to the open tile beside him nearest us (never onto his own tile -- a vendor
    behind a counter stands where no walk ends). True there."""
    if Player.DistanceTo(mob) <= reach:
        return True
    mx, my, mz = mob.Position.X, mob.Position.Y, mob.Position.Z
    px, py, _pz = here()
    beside = sorted(((cheb(mx + dx, my + dy, px, py), mx + dx, my + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
                     if (dx, dy) != (0, 0)))
    for _d, x, y in beside[:4]:
        z = standable(x, y, Player.Map)
        walk_to(x, y, mz if z is None else z)
        if Player.DistanceTo(mob) <= reach:
            return True
    return Player.DistanceTo(mob) <= reach


def find_service(kind):
    """Travel to a town with a `kind` vendor ("bank" or "tinker") and stand beside him -- the mobile, or None.
    Towns known to have one first, then towns not tried yet (the likeliest first)."""
    words = SERVICE_WORDS[kind]
    first = SERVICE_FIRST.get(kind, ())
    towns = [r for r in CITY_RUNES if not trip_risky(r)]   # NO TRIP INTO THE HOUR

    def rank(r):
        known = VENDORS.get((kind, r["name"]))
        low = base_name(r["name"]).lower()
        return (0 if known else 1 if known is None else 2,
                first.index(low) if low in first else len(first))
    tried = 0
    for r in sorted(towns, key=rank):
        if VENDORS.get((kind, r["name"])) is False or tried >= VENDOR_TRIES:
            continue
        tried += 1
        who = "banker" if kind == "bank" else "tinker"
        if recall_rune(service_rune(kind, r) or r) is not True:   # THE VENDOR'S OWN RUNE, when there is one
            log("Looking for a %s: could not recall to %s." % (who, base_name(r["name"])), HUE_BAD)
            continue
        # THE TOWN ARRIVES FIRST (10-15 02:47: Vesper, Buc's Den, Cove and Heartwood "none in sight" two seconds apart
        # -- each looked the moment it landed, before the client had the town's people, and wrote the town off): the
        # look goes on until one shows or VENDOR_LOOK_S has passed
        look_until = time.time() + VENDOR_LOOK_S
        while True:
            mobs = find_vendors(words, VENDOR_SEEK_TILES, shop=(kind == "tinker"))
            if mobs or time.time() >= look_until:
                break
            Misc.Pause(400)
        spot = VENDOR_SPOTS.get((kind, r["name"]))
        if not mobs and spot is not None:
            walk_to(spot[0], spot[1], spot[2])   # WHERE HE WAS: out of sight of the rune, walked to
            mobs = find_vendors(words, VENDOR_SEEK_TILES, shop=(kind == "tinker"))
        if mobs:
            p = mobs[0].Position
            VENDOR_SPOTS[(kind, r["name"])] = (int(p.X), int(p.Y), int(p.Z))
        if mobs or VENDORS.get((kind, r["name"])) is not True:
            VENDORS[(kind, r["name"])] = bool(mobs)   # one miss never writes off a town that had one (he wanders)
            save_vendors()
        if not mobs:
            try:                        # who IS in sight, nearest first -- a miss names its own cause
                f = Mobiles.Filter()
                f.Enabled = True
                f.RangeMax = VENDOR_SEEK_TILES
                seen = sorted(Mobiles.ApplyFilter(f) or [], key=lambda m: Player.DistanceTo(m))
                seen = ", ".join("%s (%d)" % (name_of(m) or "?", Player.DistanceTo(m)) for m in seen[:8])
            except Exception:
                seen = "?"
            here_now = here()
            log("Looking for a %s: none in sight at %s (we stand at %d,%d; in sight: %s)." % (
                who, base_name(r["name"]), here_now[0], here_now[1], seen or "nobody"))
            continue
        if not approach(mobs[0], BANK_SPEECH_TILES if kind == "bank" else VENDOR_REACH_TILES):
            log("Looking for a %s: one at %s, %d tiles off, could not be reached." % (
                who, base_name(r["name"]), Player.DistanceTo(mobs[0])), HUE_BAD)
            continue
        if mobs:
            if kind == "bank" or not VENDORS.get(("logged", kind + r["name"])):
                log("A %s at %s." % ("banker" if kind == "bank" else "tinker", base_name(r["name"])))
            mark_service_rune(kind, r)
            return mobs[0]
    log("No %s found in the towns tried this trip." % ("banker" if kind == "bank" else "tinker"), HUE_BAD)
    return None


def open_bank_here(banker):
    Player.ChatSay(0, "bank")
    Misc.Pause(1200)
    return Player.Bank


# THE ETHEREAL'S BANK (owner, 2026-10-16 00:4x: "let's give standalone script access to the Sosarian Ethereal bank option
# if the other player has unlocked it. and it's in their inventory."). A Sosarian Ethereal mount statue whose owner has
# unlocked "Can Open Bank" opens the bank from its own context menu ("Open Bankbox") wherever we stand -- the way the
# Omni scripts' remote banking does it: off the mount first (a ridden statue is the mount, not in the pack), the statue
# found in the backpack by its name, its unlock read off its own properties, the menu entry picked by its words, never
# its place. No statue, no unlock, or no bank box: the walk to a banker, as before.
ETHEREAL_NAME = "sosarian ethereal"
ETHEREAL_BANK_PROP = "can open bank: yes"
ETHEREAL_BANK_ENTRY = "open bankbox"
ETHEREAL_WAIT_MS = 3000


def ethereal_statue():
    """The Sosarian Ethereal statue in the backpack, or None."""
    for it in list(getattr(Player.Backpack, "Contains", None) or []):
        if ETHEREAL_NAME in name_of(it).lower():
            return it
    return None


def read_ethereal():
    """KNOWN IN ADVANCE (owner, 2026-10-16 00:5x: "make sure we've stored that data in advance" -- "you can't read it from
    the mount if we're riding it"): the Sosarian Ethereal's "Can Open Bank" read off the statue while it is in the pack
    -- at the start, before a ride, after getting off -- and kept in the options (eth_bank), so the bank step knows
    before it starts and never gets off a mount only to look. No statue in the pack: what was kept stands."""
    statue = ethereal_statue()
    if statue is None:
        return
    try:
        props = " | ".join(" ".join(p.lower().split()) for p in (Items.GetPropStringList(statue.Serial) or []))
    except Exception:
        props = ""
    if "can open bank" not in props:
        return
    known = "1" if ETHEREAL_BANK_PROP in props else "0"
    if SETTINGS.get("eth_bank") != known:
        SETTINGS["eth_bank"] = known
        save_settings()


def ethereal_bank():
    """THE ETHEREAL'S BANK: the bank box opened from the Sosarian Ethereal's menu where we stand, or None -- only when
    its unlock is known (read_ethereal())."""
    read_ethereal()
    if SETTINGS.get("eth_bank") != "1":
        return None
    if Player.Mount:
        dismount()                      # a ridden statue is the mount: off it, it is back in the pack
    statue, waited = ethereal_statue(), 0
    while statue is None and waited < ETHEREAL_WAIT_MS:
        Misc.Pause(200)
        waited += 200
        statue = ethereal_statue()
    if statue is None:
        return None
    try:
        entries = Misc.WaitForContext(statue.Serial, ETHEREAL_WAIT_MS) or []
    except Exception:
        entries = []
    pick = None
    for e in entries:
        if ETHEREAL_BANK_ENTRY in (getattr(e, "Entry", "") or "").lower():
            pick = getattr(e, "Response", None)
            break
    if pick is None:
        log("Your Sosarian Ethereal's menu had no Open Bankbox -- a banker it is.", HUE_BAD)
        return None
    Misc.ContextReply(statue.Serial, pick)
    waited = 0
    while waited < ETHEREAL_WAIT_MS:
        Misc.Pause(200)
        waited += 200
        if Player.Bank is not None:
            break
    if Player.Bank is None:
        log("Your Sosarian Ethereal's Open Bankbox opened no bank -- a banker it is.", HUE_BAD)
        return None
    return Player.Bank


# =============================================================================
# THE GOLD PAN -- water is the shard's own harvest water: land 0x00A8-0x00AB, 0x0136-0x0137; statics
# 0x1797-0x179C, 0x346E-0x3485, 0x3490-0x34AB, 0x34B5-0x35D5 -- or any tile the tile data calls Wet.
# =============================================================================

PAN_WATER_LAND = ((0x00A8, 0x00AB), (0x0136, 0x0137))
PAN_WATER_STATIC = ((0x1797, 0x179C), (0x346E, 0x3485), (0x3490, 0x34AB), (0x34B5, 0x35D5))
PAN_RANGE = 2                  # the pan reaches this far
PAN_WALK_RADIUS = 14           # the shore walk looks this far for a place to stand
PAN_SEEK_RADIUS = 40           # ... and once a visit this far (a town's rune may stand back from its water)
PAN_WALK_TRIES = 3
PAN_SEEK_TRIES = 6
PAN_TRY_SPREAD = 6
PAN_BANK_TILES = 8             # an emptied spot rests this square of water...
PAN_REST_S = 20 * 60           # ... this long
SIFT_WAIT_S = 12               # a sift takes seconds and the shard answers at its END (10-15: a sift sent each second
                               # heard "You are already panning." 40 times) -- one at a time, its answer waited for;
                               # silence this long means the tile was not taken as water
PAN_AFTER_ANSWER_S = 0.75      # the pan is held a moment past its answer
VISIT_DRY_SIFTS = 20           # a visit ends after this many answered sifts in a row without a find
PAN_DEAD_VISITS = 3            # a rune with this many visits and no find is passed over
PAN_RUNE_GAP = 20              # a new rune is marked this far from every other
PAN_MAX_RUNES = 60
DANGER_TILES = 12
HOSTILE_NOTORIETIES = (5, 6)   # orange and red
PANS_KEPT = 2
PAN_INGOTS = 4
INGOTS_BOUGHT = 16
IRON_INGOT_ID = 0x1BF2
TINKER_KIT_IDS = (0x1EBC, 0x1EB8)   # tinker's tools as a tinker sells them, and the tool kit -- either makes a pan
TINKER_GUMP = 0x38920abd
TINKER_TOOLS_CATEGORY = 15
TINKER_KIT_MAKE = 23
TINKER_PAN_MAKE = 121

PAN_REPLIES = (                # the first that matches a reply decides; lower case
    ("mounted", ("while riding",)),
    ("busy", ("already panning",)),
    ("not_dry", ("stand on dry land",)),
    ("full", ("backpack is full", "too heavy", "carry no more")),
    ("broke", ("broke your", "worn out", "pan has no")),
    ("refused", ("must wait to perform",)),
    ("empty", ("nuggets left here", "doesn't seem to be any", "nothing left", "has been depleted")),
    ("miss", ("find nothing", "you sift but", "only mud", "you don't find")),
    ("bad", ("closer to the water", "cannot be seen", "can't use", "cannot use", "too far", "on foot", "not water",
             "can't pan", "cannot pan", "that is not", "you can't do that")),
    ("find", ("gold nugget", "gold brick", "rough stone", "you have found", "you find", "you put")),
)


def in_ranges(graphic, ranges):
    return any(lo <= int(graphic) <= hi for lo, hi in ranges)


def wet_tile(x, y, m):
    """(x, y, z, graphic) when (x, y) is water -- graphic 0 for land water -- else None."""
    try:
        land = Statics.GetLandID(x, y, m)
        if in_ranges(land, PAN_WATER_LAND) or Statics.GetLandFlag(land, "Wet"):
            return (x, y, int(Statics.GetLandZ(x, y, m)), 0)
        # ONLY THE LISTED WATER STATICS (owner, 2026-10-16 01:3x: "stop counting the wet flag for statics"): the shore's
        # edge pieces carry the Wet flag but the shard never takes them -- 10-16 01:11-01:24 at Cove, 0x17A1, 0x17A2,
        # 0x17A7, 0x17A8 and 0x17AA at z-5, every target silent (RazorEnhanced's own tile reads, both standalone clients)
        for t in Statics.GetStaticsTileInfo(x, y, m) or []:
            if in_ranges(t.StaticID, PAN_WATER_STATIC):
                return (x, y, int(t.StaticZ), int(t.StaticID))
    except Exception:
        pass
    return None


def standable(x, y, m):
    """Dry land a player can stand on, by the map files: (z) or None."""
    try:
        land = Statics.GetLandID(x, y, m)
        if Statics.GetLandFlag(land, "Impassable") or in_ranges(land, PAN_WATER_LAND) or Statics.GetLandFlag(land, "Wet"):
            return None
        z = int(Statics.GetLandZ(x, y, m))
        for t in Statics.GetStaticsTileInfo(x, y, m) or []:
            if Statics.GetTileFlag(t.StaticID, "Impassable") and abs(int(t.StaticZ) - z) < 16:
                return None
        return z
    except Exception:
        return None


def is_pan(item):
    return re.search(r"\bgold pans?\b", name_of(item).lower()) is not None


def find_pan():
    for it in pack_items():
        if is_pan(it):
            return it
    return None


def pans_in_pack():
    return sum(1 for it in pack_items() if is_pan(it))


def iron_ingots():
    total = 0
    for it in Items.FindAllByID(IRON_INGOT_ID, 0, Player.Backpack.Serial, False, False) or []:
        total += int(it.Amount or 0)
    return total


def tinker_kits():
    out = []
    for kit_id in TINKER_KIT_IDS:
        out.extend(Items.FindAllByID(kit_id, -1, Player.Backpack.Serial, False, False) or [])
    return out


def kit_uses():
    total = 0
    for it in tinker_kits():
        try:
            total += int(Items.GetPropValue(it, "Uses Remaining"))
        except Exception:
            pass
    return total


def tinker_press(button):
    Gumps.SendAction(TINKER_GUMP, button)
    Misc.Pause(150)
    wait_for_gump_present(TINKER_GUMP, 10000)
    Misc.Pause(50)


def make_pan():
    """One Gold Pan from the tinker's kit (and a new kit first when the last is nearly worn out)."""
    if not tinker_kits() or ingots_on_hand() < PAN_INGOTS:
        return False
    before = pans_in_pack()
    Items.UseItem(tinker_kits()[0])
    if wait_for_gump_present(TINKER_GUMP, 10000) is None:
        log("The tinker's kit opened no menu.", HUE_BAD)
        return False
    tinker_press(TINKER_TOOLS_CATEGORY)
    if kit_uses() < 10 and ingots_on_hand() >= PAN_INGOTS + 2:
        tinker_press(TINKER_KIT_MAKE)
    tinker_press(TINKER_PAN_MAKE)
    Gumps.SendAction(TINKER_GUMP, 0)
    KEY_IRON[0] = None                  # the key may have paid for it: read again when next asked
    for _ in range(20):
        if pans_in_pack() > before:
            return True
        Misc.Pause(150)
    return False


def keep_pans():
    """PANS_KEPT pans in the pack, made from what we carry. True when at least one is carried."""
    made = 0
    while pans_in_pack() < PANS_KEPT and made < PANS_KEPT and ingots_on_hand() >= PAN_INGOTS and tinker_kits():
        if not make_pan():
            log("The tinker's kit made no Gold Pan (Tinkering too low?).", HUE_BAD)
            break
        made += 1
    if made:
        log("%d Gold Pan(s) made -- %d carried, %d iron ingot(s) left." % (made, pans_in_pack(), ingots_on_hand()))
    return pans_in_pack() > 0


# =============================================================================
# INGOT STORAGE -- the shard's Ingot Storage key, when the pack holds one: the gems we find go into it (its "Refill
# from stock" takes everything it has a row for), and a pan's iron ingots are its own -- the tinker's kit uses them
# straight from the key, so none are bought while it holds some. Its window is the shard's storage window: a row's name, its amount, its withdraw button.
# =============================================================================

INGOT_KEY_ID = 0x1BE8
INGOT_KEY_HUE = 0x0014
STORAGE_GUMP = 0x06ABCE12
KEY_PACE_S = 1.2               # the shard lets a storage key act about once a second
KEY_IRON_ROW = "iron"
STORAGE_CONTROL_LINE = re.compile(
    r"^(Previous Page|Next Page|\(\d+/\d+\)|Withdrawal Amount:|Add|Maximum Storage:|Fill from backpack)")
STORAGE_LAYOUT_BUTTON = re.compile(r"\{\s*button\s+\d+\s+(\d+)\s+(\d+)\s+(\d+)\s+\d+\s+\d+\s+(\d+)\s*\}")
STORAGE_ROW_BUTTON_ART = (1209, 1210)
KEY_LAST = [0.0]


def ingot_key():
    for it in pack_items():
        if it.ItemID == INGOT_KEY_ID and it.Hue == INGOT_KEY_HUE:
            return it
    return None


def key_pace():
    wait = KEY_LAST[0] + KEY_PACE_S - time.time()
    if wait > 0:
        Misc.Pause(int(wait * 1000))
    KEY_LAST[0] = time.time()


def close_storage():
    try:
        if Gumps.HasGump(STORAGE_GUMP):
            Gumps.CloseGump(STORAGE_GUMP)
    except Exception:
        pass


def key_rows(key):
    """The key's window opened and read: [(row name, amount, withdraw button)], or None."""
    close_storage()
    key_pace()
    Items.UseItem(key)
    if wait_for_gump_present(STORAGE_GUMP, 5000) is None:
        return None
    Misc.Pause(300)
    try:
        try:
            lines = [re.sub(r"<[^>]+>", "", str(l)).strip() for l in (Gumps.GetLineList(STORAGE_GUMP, False) or [])]
        except TypeError:
            lines = [re.sub(r"<[^>]+>", "", str(l)).strip() for l in (Gumps.GetLineList(STORAGE_GUMP) or [])]
        layout = str(Gumps.GetGumpRawLayout(STORAGE_GUMP) or "")
    except Exception:
        return None
    pairs = []
    i = 1                              # line 0 is the window's title
    while i + 1 < len(lines):
        name, value = lines[i], lines[i + 1].replace(",", "")
        if not name or STORAGE_CONTROL_LINE.match(name) or not value.isdigit():
            break
        pairs.append((name, int(value)))
        i += 2
    buttons = [int(m[3]) for m in STORAGE_LAYOUT_BUTTON.findall(layout)
               if (int(m[1]), int(m[2])) == STORAGE_ROW_BUTTON_ART]
    if not pairs or len(buttons) < len(pairs):
        return None
    return [(n, a, b) for (n, a), b in zip(pairs, buttons)]


def key_absorb():
    """Everything the key has a row for -- the gems we found among it -- out of the pack and into the key."""
    key = ingot_key()
    if key is None:
        return False
    close_storage()
    key_pace()
    before = set(it.Serial for it in pack_items())
    if not context_pick(key.Serial, "refill from stock"):
        log("Your Ingot Storage offered no Refill from stock.", HUE_BAD)
        return False
    wait_for_gump_present(STORAGE_GUMP, 3000)
    close_storage()
    taken = len(before - set(it.Serial for it in pack_items()))
    if taken:
        log("%d stack(s) into your Ingot Storage." % taken)
    return True


KEY_IRON = [None, 0.0]           # the key's iron ingots at its last read, and when
KEY_IRON_FRESH_S = 120


def key_iron(fresh=False):
    """The iron ingots in the Ingot Storage key (0 without one) -- the tinker's kit uses them straight from the key."""
    key = ingot_key()
    if key is None:
        return 0
    if fresh or KEY_IRON[0] is None or time.time() - KEY_IRON[1] > KEY_IRON_FRESH_S:
        rows = key_rows(key)
        close_storage()
        row = next((r for r in rows or [] if r[0].strip().lower() == KEY_IRON_ROW), None)
        KEY_IRON[0], KEY_IRON[1] = (row[1] if row else 0), time.time()
    return KEY_IRON[0]


def ingots_on_hand():
    """Iron ingots the tinker's kit can use: the pack's and the Ingot Storage key's."""
    return iron_ingots() + key_iron()


def supplies_low():
    """True when a trip to a tinker would help. THE FIRST PAN IS MADE FOR YOU: with no pan and nothing to make one from,
    always; and a spare (PANS_KEPT) is always kept."""
    cannot_make = ingots_on_hand() < PAN_INGOTS or not tinker_kits()
    if pans_in_pack() == 0 and cannot_make:
        return True
    return pans_in_pack() < PANS_KEPT and cannot_make


def open_window_ids():
    try:
        return set(Gumps.AllGumpIDs() or [])
    except Exception:
        return set()


def close_new_windows(before):
    """The shop window a buy opened, closed once the buying is done: every window that is open now and was not before
    it -- never a window the player had open."""
    closed = 0
    for gid in open_window_ids() - before:
        try:
            Gumps.SendAction(gid, 0)
            closed += 1
        except Exception:
            pass
    return closed


def vendor_buy(vendor, item_id, name, amount, max_price):
    try:
        return Vendor.Buy(vendor.Serial, item_id, amount, max_price)
    except Exception:
        return Vendor.Buy(vendor.Serial, name, amount, max_price)


def supply_run():
    """A tinker in town: iron ingots and a tinker's kit (pennies -- vendors bill the bank). True when a pan is carried
    after."""
    if tinker_kits() and ingots_on_hand() >= PAN_INGOTS:
        return keep_pans()              # INGOT STORAGE: the key's ingots are enough -- none bought
    doing("Buying a kit and ingots at a tinker")
    vendor = find_service("tinker")
    if vendor is None:
        return keep_pans()
    windows_before = open_window_ids()
    if not tinker_kits():
        for kit_id in TINKER_KIT_IDS + (None,):      # each id the shop may list it under, then its name
            if kit_id is None:
                Vendor.Buy(vendor.Serial, "tinker's tools", 1, 50)
            else:
                vendor_buy(vendor, kit_id, "tinker's tools", 1, 50)
            Misc.Pause(1200)
            if tinker_kits():
                break
        if not tinker_kits():
            log("The tinker would not sell a tinker's kit.", HUE_BAD)
    need = max(0, (PANS_KEPT * PAN_INGOTS + PAN_INGOTS) - ingots_on_hand())
    if need > 0:
        vendor_buy(vendor, IRON_INGOT_ID, "iron ingot", min(INGOTS_BOUGHT, max(need, PAN_INGOTS)), 20)
        Misc.Pause(1200)
    closed = close_new_windows(windows_before)
    log("At the tinker: %d iron ingot(s), %d kit(s) carried%s." % (
        ingots_on_hand(), len(tinker_kits()), "; the shop window closed" if closed else ""))
    return keep_pans()


# =============================================================================
# DANGER AND TOWN INVASIONS
# =============================================================================

INVASION_TOWNS = {             # (maps, x1, y1, x2, y2) -- where each town's invasion spawns
    "cove": ((0, 1), 2160, 1090, 2330, 1290),
    "delucia": ((0, 1), 5110, 3890, 5355, 4130),
    "jhelom": ((0, 1), 1250, 3620, 1520, 3900),
    "minoc": ((0, 1), 2370, 345, 2585, 590),
    "moonglow": ((0, 1), 4330, 1000, 4530, 1220),
    "skara brae": ((0, 1), 485, 2025, 705, 2310),
    "umbra": ((3,), 1900, 1230, 2145, 1450),
    "yew": ((0, 1), 380, 860, 735, 1175),
}
INVASION_BEFORE_S = 60         # the guard starts this long before an invasion hour...
# NO TRIP INTO THE HOUR (owner, 2026-10-16 01:1x: "neither standalone panner got to somewhere safe before the [invasion]
# started. that's an easy way to die" -- "pretty sure one was in Cove"): the guard's minute is for panning, which walks
# off at once; a trip -- the turn-in at Harry, a banker -- takes minutes in town. 10-16 00:59:40 a turn-in began in Cove
# inside that minute and was still there at the hour. A trip into an invasion town starts no later than this before an
# invasion hour, and never into the town an invasion holds.
TRIP_LEAD_S = 5 * 60
INVASION_AWAY_MAX_S = 10 * 60  # ... and holds every town until the shard names one, at most this long after
INVASION_HOLDS_S = 61 * 60     # a named town is avoided this long, or until it is saved
# THE INVASION HOURS ARE FIXED (owner, 2026-10-16 01:2x: "yes, build the fix"). Town Invasions start on the even UTC hours
# -- 19:00, 23:00 and 01:00 at UTC-7 on 10-15/16 -- whatever the player's time zone. This was learned from each card's
# reading time, rounded to the hour: 10-15 23:52:52 (06:52 UTC) the Cove invasion's late warlord card rounded to 07:00 and
# set the hours odd, so at 00:59 the guard watched 07:00 UTC, skipped the real 08:00 (01:00 local), and one panner turned
# in at Harry in Minoc and recalled into Cove inside the guard's minute. Nothing re-learns it now.
INVASION_UTC_PARITY = 0
INVASION_ATTACK_RE = re.compile(r"town invasion:\s*(.+?)\s+is under attack", re.I)
INVASION_SAVED_RE = re.compile(r"^(.+?)\s+is saved", re.I)
INVADED = {}                   # town -> when its broadcast came
INVADED_FILE = "Invaded.txt"   # THE INVADED TOWN IS KEPT (10-15 09:36: a restart at 09:32 forgot Jhelom, named by the
INVADED_SAVED = [None]         # 09:00 card, and the panner walked into it) -- read at start, written on every change


def load_invaded():
    INVADED.clear()
    try:
        with open(data_path(INVADED_FILE)) as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) == 2 and time.time() - float(p[1]) < INVASION_HOLDS_S:
                    INVADED[p[0]] = float(p[1])
    except Exception:
        pass
    INVADED_SAVED[0] = dict(INVADED)


def save_invaded():
    if INVADED_SAVED[0] == INVADED or not ensure_data_dir():
        return
    try:
        with open(data_path(INVADED_FILE), "w") as f:
            for town, at in sorted(INVADED.items()):
                f.write("%s\t%.0f\n" % (town, at))
        INVADED_SAVED[0] = dict(INVADED)
    except Exception:
        pass
JOURNAL_MARK = [0.0]


# THE EVENT CARDS (shard update 10/15): events are announced on pop-up cards, not in the journal -- a card's first line
# is the event's name, the rest its words: "Defend the town!" / "A Warlord has arrived!" with "Location: <town>" when an
# invasion starts, "The invasion has been repelled!" when it ends (and a "Winner: ..." card). Each open card is read
# once a change; the journal's own lines are still read for shards that send them.
CARD_LOCATION_RE = re.compile(r"Location:\s*([A-Za-z' ]+?)(?=\s+[A-Z][A-Za-z]*:|\s*$)")
CARDS_SEEN = {}                # card window id -> the words last read off it


def card_words(gid):
    try:
        try:
            lines = Gumps.GetLineList(gid, False) or []
        except TypeError:
            lines = Gumps.GetLineList(gid) or []
    except Exception:
        return None
    lines = [re.sub(r"<[^>]+>", " ", str(l)) for l in lines]
    lines = [re.sub(r"\s+", " ", l).strip() for l in lines]
    lines = [l for l in lines if l]
    if not lines:
        return None
    return lines[0], " ".join(lines[1:])


def invasion_named(town):
    INVADED[town.lower()] = time.time()
    log("A Town Invasion holds %s -- keeping out of it." % town, HUE_BAD)


def read_cards():
    try:
        ids = list(Gumps.AllGumpIDs() or [])
    except Exception:
        return
    for gid in ids:
        got = card_words(gid)
        if got is None or got[0].lower() != "town invasion":
            continue
        if CARDS_SEEN.get(gid) == got[1]:
            continue
        CARDS_SEEN[gid] = got[1]
        words = got[1].lower()
        m = CARD_LOCATION_RE.search(got[1])
        town = m.group(1).strip() if m else None
        # "Defend the town!" names the invasion; the warlord card, late in it, names only a town not on the list yet (a
        # restart mid-invasion) -- THE INVASION HOURS ARE FIXED, so neither touches them
        if town and ("defend the town" in words or ("warlord" in words and town.lower() not in INVADED)):
            invasion_named(town)
        elif "repelled" in words or (town and "winner" in words):
            for t in ([town.lower()] if town else list(INVADED)):
                if INVADED.pop(t, None) is not None:
                    log("%s is saved." % t.title())


def read_broadcasts():
    read_cards()
    stamp = JOURNAL_MARK[0]
    lines = journal_lines_after(stamp)
    if lines:
        JOURNAL_MARK[0] = max(getattr(e, "Timestamp", 0.0) or 0.0 for e in lines)
    for e in lines:
        text = (getattr(e, "Text", "") or "").strip()
        m = INVASION_ATTACK_RE.search(text)
        if m:
            invasion_named(m.group(1).strip())
            continue
        m = INVASION_SAVED_RE.search(text)
        if m and m.group(1).strip().lower() in INVADED:
            INVADED.pop(m.group(1).strip().lower(), None)
            log("%s is saved." % m.group(1).strip())
    for town, at in list(INVADED.items()):
        if time.time() - at > INVASION_HOLDS_S:
            INVADED.pop(town, None)
    save_invaded()


def invasion_window(before=INVASION_BEFORE_S):
    """True from `before` seconds before an invasion hour until a town is named (or INVASION_AWAY_MAX_S after)."""
    now = time.time()
    parity = INVASION_UTC_PARITY       # THE INVASION HOURS ARE FIXED
    utc = time.gmtime(now)
    top = now - (utc.tm_min * 60 + utc.tm_sec)
    for start, hour in ((top, utc.tm_hour), (top + 3600, utc.tm_hour + 1)):
        if hour % 2 != parity:
            continue
        if start - before <= now < start + INVASION_AWAY_MAX_S:
            if any(at >= start - 5 * 60 for at in INVADED.values()):
                return False
            return True
    return False


def town_at(x, y, m):
    for town, (maps, x1, y1, x2, y2) in INVASION_TOWNS.items():
        if m in maps and x1 <= x <= x2 and y1 <= y <= y2:
            return town
    return None


def risky_spot(x, y, m, name=""):
    """True when (x, y) -- or a rune called `name` -- is in a town an invasion may hold now."""
    if not opt("avoid_invasions"):
        return False
    town = town_at(x, y, m) if x is not None else None
    if town is None:
        low = (name or "").lower()
        town = next((t for t in INVASION_TOWNS if t in low), None)
    if town is None:
        return False
    return invasion_window() or town in INVADED


def rune_map(rune):
    label = world_label(rune["name"])
    return next((k for k, v in WORLD_NAMES.items() if v.lower() == label), Player.Map)


def trip_risky(rune):
    """NO TRIP INTO THE HOUR: True when a trip to `rune` would end in a town an invasion holds, or may hold within
    TRIP_LEAD_S."""
    if rune is None or not opt("avoid_invasions"):
        return False
    c = rune.get("coord") or []
    town = town_at(c[0], c[1], rune_map(rune)) if len(c) >= 2 else None
    if town is None:
        low = (rune.get("name") or "").lower()
        town = next((t for t in INVASION_TOWNS if t in low), None)
    return town is not None and (invasion_window(TRIP_LEAD_S) or town in INVADED)


def rune_risky(rune):
    c = rune.get("coord") or []
    if len(c) >= 2:
        return risky_spot(c[0], c[1], rune_map(rune), rune["name"])
    return risky_spot(None, None, rune_map(rune), rune["name"])


def hostiles_near():
    f = Mobiles.Filter()
    f.Enabled = True
    f.RangeMax = DANGER_TILES
    for n in HOSTILE_NOTORIETIES:
        f.Notorieties.Add(n)
    return list(Mobiles.ApplyFilter(f) or [])


# NO FIGHTING, NO DYING: this script has no defense and no death recovery, so it never stays where anything has turned
# on it -- not an option. Any hit, poison, or a red or orange mobile near while panning: away at once, and that rune is
# never panned again (BLACKLIST_FILE).
AGGRO = [None]                 # what set us off this visit -- once set, the visit is over
LAST_HITS = [None]


def aggro_reset():
    AGGRO[0] = None
    try:
        LAST_HITS[0] = Player.Hits
    except Exception:
        LAST_HITS[0] = None


def in_danger():
    """Something has turned on us: hits lost since the last look, poison, or a red or orange mobile near. Kept for the
    rest of the visit."""
    if AGGRO[0]:
        return True
    why = None
    try:
        hits = Player.Hits
        if LAST_HITS[0] is not None and hits < LAST_HITS[0]:
            why = "hit (%d/%d)" % (hits, Player.HitsMax)
        LAST_HITS[0] = hits
        if why is None and Player.Poisoned:
            why = "poisoned"
    except Exception:
        pass
    if why is None:
        found = hostiles_near()
        if found:
            why = "hostile nearby (%s)" % ", ".join(name_of(mob) or "?" for mob in found[:3])
    if why:
        AGGRO[0] = why
        log("%s%s -- leaving." % (why[:1].upper(), why[1:]), HUE_BAD)
        return True
    return False


BLACKLIST_FILE = "Blacklist.txt"
BLACKLIST = {}                 # rune key -> why


DANGER_SPOTS_FILE = "DangerSpots.txt"   # where danger found us: "map<TAB>x<TAB>y<TAB>when and why", every panner's
DANGER_SPOTS = []              # (map, x, y): those spots and every blacklisted rune's
DANGER_AVOID_TILES = 30        # THE WALK OUT never goes, or walks a line, this near one (owner, 10-15: "Don't move
                               # through previously unsafe areas to find new ones.")


def load_danger_spots():
    del DANGER_SPOTS[:]
    try:
        with open(data_path(DANGER_SPOTS_FILE)) as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 3 and p[0].isdigit():
                    DANGER_SPOTS.append((int(p[0]), int(p[1]), int(p[2])))
    except Exception:
        pass
    for key in BLACKLIST:
        name, _at, xy = key.rpartition("@")
        c = xy.split(",")
        if len(c) == 2 and all(v.lstrip("-").isdigit() for v in c):
            m = rune_map({"name": name})
            DANGER_SPOTS.append((m, int(c[0]), int(c[1])))


def note_danger_spot(why):
    x, y, _z = here()
    m = Player.Map
    DANGER_SPOTS.append((m, x, y))
    if not ensure_data_dir():
        return
    try:
        with open(data_path(DANGER_SPOTS_FILE), "a") as f:
            f.write("%d\t%d\t%d\t%s %s\n" % (m, x, y, time.strftime("%Y-%m-%d %H:%M"), why))
    except Exception:
        pass


def near_danger(m, x, y, tiles=DANGER_AVOID_TILES):
    return any(dm == m and cheb(x, y, dx, dy) < tiles for dm, dx, dy in DANGER_SPOTS)


def line_near_danger(m, x0, y0, x1, y1):
    """The straight line between two places passes within DANGER_AVOID_TILES of a danger spot."""
    n = max(1, cheb(x0, y0, x1, y1))
    for i in range(0, n + 1, 2):
        if near_danger(m, x0 + (x1 - x0) * i // n, y0 + (y1 - y0) * i // n):
            return True
    return near_danger(m, x1, y1)


def load_blacklist():
    BLACKLIST.clear()
    try:
        with open(data_path(BLACKLIST_FILE)) as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if p and p[0]:
                    BLACKLIST[p[0]] = p[1] if len(p) > 1 else ""
    except Exception:
        pass


def in_invasion_hour():
    """True from INVASION_BEFORE_S before an invasion hour until INVASION_HOLDS_S after it -- whether or not its town is
    known."""
    now = time.time()
    parity = INVASION_UTC_PARITY       # THE INVASION HOURS ARE FIXED
    utc = time.gmtime(now)
    top = now - (utc.tm_min * 60 + utc.tm_sec)
    for start, hour in ((top, utc.tm_hour), (top + 3600, utc.tm_hour + 1)):
        if hour % 2 == parity and start - INVASION_BEFORE_S <= now < start + INVASION_HOLDS_S:
            return True
    return False


def blacklist_rune(rune, why):
    key = rune_key(rune)
    if key in BLACKLIST:
        return
    c = rune.get("coord") or []
    town = town_at(c[0], c[1], rune_map(rune)) if len(c) >= 2 else None
    if town and in_invasion_hour():
        log("%s: danger in a town in its invasion hour -- the invasion's, not the spot's; not taken off the route." % (
            base_name(rune["name"])), HUE_BAD)
        if town not in INVADED:         # THE DANGER NAMES THE TOWN (09:36 and 09:49: Jhelom twice, its card missed) --
            invasion_named(town.title())   # kept out of for the rest of the invasion, as a card would
            save_invaded()
        return
    BLACKLIST[key] = why
    log("%s is off the route for good (%s)." % (base_name(rune["name"]), why), HUE_BAD)
    if not ensure_data_dir():
        return
    try:
        with open(data_path(BLACKLIST_FILE), "a") as f:
            f.write("%s\t%s %s\n" % (key, time.strftime("%Y-%m-%d %H:%M"), why))
    except Exception:
        pass


# =============================================================================
# RUNE RECORD -- visits and finds per rune, kept across runs.
# =============================================================================

RUNE_STATS_FILE = "RuneStats.txt"
RUNE_STATS = {}


def load_rune_stats():
    RUNE_STATS.clear()
    try:
        with open(data_path(RUNE_STATS_FILE)) as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) >= 3:
                    RUNE_STATS[p[0]] = [int(p[1]), int(p[2])]
    except Exception:
        pass


def save_rune_stats():
    if not ensure_data_dir():
        return
    try:
        with open(data_path(RUNE_STATS_FILE), "w") as f:
            for k, (v, n) in sorted(RUNE_STATS.items()):
                f.write("%s\t%d\t%d\n" % (k, v, n))
    except Exception:
        pass


def rune_key(rune):
    c = rune.get("coord") or []
    return "%s@%s" % (rune["name"], ",".join(str(v) for v in c[:2]))


def rune_dead(rune):
    v, n = RUNE_STATS.get(rune_key(rune), [0, 0])
    return v >= PAN_DEAD_VISITS and n == 0


def is_po_rune(rune):
    low = base_name(rune["name"]).lower()
    return low in PO_RUNE_NAMES or low.startswith("harry")


# =============================================================================
# PANNING AT ONE RUNE
# =============================================================================

REST = {}                      # (map, x // 8, y // 8) -> when that water is fresh again
BLIND = set()                  # (map, x, y) the shard never took as water -- kept (THE PAN LEARNS ITS WATER)

# THE PAN LEARNS ITS WATER (owner, 2026-10-16 01:2x: "do that and the pan learns its water port as well" -- the Omni
# Panner's own, 10-13: "instead of just trying to pan every spot, we need to also be learning the pan requirements to
# better apply them to new spots and stop trying 'all the things'"). 10-16 01:11-01:14 at Cove: nine sifts, eight with
# no answer, 12 s each -- each blind tile was learned alone, for one run, and the next tile of the same kind tried. What
# decides a sift is the water's kind (land or a static), its height against ours and how far it is: each sift's answer
# goes to the panner's own record under that key -- worked (a find, an empty spot, a sift under way, a miss) or refused
# (a bad target); a key refused LEARN_NEVER times and never worked is not tried again anywhere, and the keys that work
# go first. A tile that never answered, or "cannot be seen", is blind for good; the emptied spots' rests are kept too, so
# a restart tries neither again.
LEARN_FILE = "PanLearn.txt"
LEARN_NEVER = 3
LEARN_DZ = 5                   # heights are kept in steps of this many
LEARN = {}                     # key -> [worked, refused]


def learn_load():
    """The record, read at the start: the keys, the blind tiles, the rests still running."""
    now = time.time()
    try:
        with open(char_path(LEARN_FILE)) as f:
            for line in f:
                p = line.rstrip("\n").split("\t")
                if len(p) == 3 and p[0] == "key":
                    w, r = p[2].split(",")
                    LEARN[p[1]] = [int(w), int(r)]
                elif len(p) == 4 and p[0] == "blind":
                    BLIND.add((int(p[1]), int(p[2]), int(p[3])))
                elif len(p) == 5 and p[0] == "rest" and float(p[4]) > now:
                    REST[(int(p[1]), int(p[2]), int(p[3]))] = float(p[4])
    except Exception:
        pass


def learn_save():
    if not ensure_char_dir():
        return
    now = time.time()
    try:
        with open(char_path(LEARN_FILE), "w") as f:
            for k, (w, r) in sorted(LEARN.items()):
                f.write("key\t%s\t%d,%d\n" % (k, w, r))
            for m, x, y in sorted(BLIND):
                f.write("blind\t%d\t%d\t%d\n" % (m, x, y))
            for (m, bx, by), until in sorted(REST.items()):
                if until > now:
                    f.write("rest\t%d\t%d\t%d\t%.0f\n" % (m, bx, by, until))
    except Exception:
        pass


def water_key(w, origin):
    """(land or static, height against ours, distance) of the water `w` (x, y, z, graphic) from `origin` (x, y, z) --
    never the graphic (a cliff over the sea: every new graphic was refused before the height that refused them all)."""
    dz = int(w[2]) - int(origin[2])
    dist = cheb(int(w[0]), int(w[1]), int(origin[0]), int(origin[1]))
    return "%s|dz%d|d%d" % ("static" if w[3] else "land", int(round(dz / float(LEARN_DZ))) * LEARN_DZ, dist)


def learn_note(w, origin, worked):
    t = LEARN.setdefault(water_key(w, origin), [0, 0])
    t[0 if worked else 1] += 1


class Visit(object):
    def __init__(self, rune):
        self.rune = rune
        self.tried = set()
        self.walked = set()
        self.sought = False
        self.sifts = 0
        self.finds = 0
        self.ready_at = 0.0
        self.dry = 0
        self.filled = 0                 # nuggets into orders while sifting
        self.t0 = time.time()
        self.origin = here()[:2]        # THE WALK OUT measures from here
        self.out = 0                    # ... and how far out it went
        self.hops = 0


# =============================================================================
# THE SHARD'S OWN SIGHT -- a sift is refused "Target cannot be seen" when the shard's line of sight from us to the water
# fails. This is the shard's (ServUO's) Map.LineOfSight, line for line, over RazorEnhanced's own map lookups, so no sift
# is spent on water we cannot see (proven against the shard's answers before it came here: every one agreed).
#   From: our eye, 14 over our feet. To: a land tile at its highest corner + 1, a static at its middle + 1.
#   Blocks: land between (unless an ignored id), a missing land tile with nothing on it, a Window or NoShoot static.
#   Not here: houses and items lying in the world (a sift past them can still be refused -- then the tile is set aside).
# =============================================================================

LOS_MAX = 24 + 1
EYE_HEIGHT = 14
INVALID_LAND = (0x244,)
LOS_CACHE = {}                 # (map, x, y) -> (land id, lowest corner, highest corner, [(z, height, blocks)])


def land_ignored(land_id):
    return land_id == 2 or land_id == 0x1DB or 0x1AE <= land_id <= 0x1B5


def los_tile(m, x, y):
    key = (m, x, y)
    got = LOS_CACHE.get(key)
    if got is None:
        if len(LOS_CACHE) > 60000:
            LOS_CACHE.clear()
        land = Statics.GetLandID(x, y, m)
        zs = [int(Statics.GetLandZ(x, y, m)), int(Statics.GetLandZ(x, y + 1, m)),
              int(Statics.GetLandZ(x + 1, y, m)), int(Statics.GetLandZ(x + 1, y + 1, m))]
        statics = []
        for t in Statics.GetStaticsTileInfo(x, y, m) or []:
            height = int(Statics.GetTileHeight(t.StaticID))
            calc = height // 2 if Statics.GetTileFlag(t.StaticID, "Bridge") else height
            blocks = bool(Statics.GetTileFlag(t.StaticID, "Window") or Statics.GetTileFlag(t.StaticID, "NoShoot"))
            statics.append((int(t.StaticZ), calc, height, blocks))
        got = LOS_CACHE[key] = (land, min(zs), max(zs), statics)
    return got


def sight_target(m, w):
    x, y, z, graphic = w
    if not graphic:
        return (x, y, los_tile(m, x, y)[2] + 1)
    height = int(Statics.GetTileHeight(graphic))
    calc = height // 2 if Statics.GetTileFlag(graphic, "Bridge") else height
    return (x, y, int(z) - calc + height // 2 + 1)


def _between(num, b1, b2, allowance):
    if b1 > b2:
        b1, b2 = b2, b1
    return b1 - allowance < num < b2 + allowance


def line_of_sight(m, org, dest):
    if not (abs(org[0] - dest[0]) <= LOS_MAX and abs(org[1] - dest[1]) <= LOS_MAX):
        return False
    end = dest
    if org[0] > dest[0] or (org[0] == dest[0] and org[1] > dest[1]) or \
            (org[0] == dest[0] and org[1] == dest[1] and org[2] > dest[2]):
        org, dest = dest, org
    if org == dest:
        return True
    xd, yd, zd = dest[0] - org[0], dest[1] - org[1], dest[2] - org[2]
    zslp = (xd * xd + yd * yd) ** 0.5
    sq3d = (zslp * zslp + zd * zd) ** 0.5 if zd != 0 else zslp
    rise, run = yd / sq3d, xd / sq3d
    zslp = zd / sq3d
    x, y, z = float(org[0]), float(org[1]), float(org[2])
    path = []
    while _between(x, dest[0], org[0], 0.5) and _between(y, dest[1], org[1], 0.5) and _between(z, dest[2], org[2], 0.5):
        p = (int(round(x)), int(round(y)), int(round(z)))
        if not path or path[-1] != p:
            path.append(p)
        x += run
        y += rise
        z += zslp
    if not path:
        return True
    if path[-1] != tuple(dest):
        path.append(tuple(dest))
    end_top = end[2] + 1
    for px, py, pz in path:
        point_top = pz + 1
        land, low, top, statics = los_tile(m, px, py)
        if low <= point_top and top >= pz and \
                (px != end[0] or py != end[1] or low > end_top or top < end[2]) and not land_ignored(land):
            return False
        if land in INVALID_LAND and not statics:
            return False
        for sz, calc, _height, blocks in statics:
            if blocks and sz <= point_top and sz + calc >= pz:
                if px != end[0] or py != end[1] or sz > end_top or sz + calc < end[2]:
                    return False
    return True


def sees(m, me, w):
    """True when the shard would let us sift the water `w` (x, y, z, graphic) standing at `me` (x, y, z). True when it
    cannot be judged -- no water is lost to an error."""
    try:
        return line_of_sight(m, (int(me[0]), int(me[1]), int(me[2]) + EYE_HEIGHT), sight_target(m, w))
    except Exception:
        return True


def water_near(cx, cy, m, wet=None, tried=(), cz=None, sight=True):
    """The water we can sift standing at (cx, cy) -- at height `cz`, where we stand when None -- the kinds that work
    first (THE PAN LEARNS ITS WATER), then the nearest. Never a kind only ever refused. `sight` off: every wet tile in
    reach (the shore walk's first cut, which checks sight only on the stands it picks)."""
    now = time.time()
    out = []
    for dx in range(-PAN_RANGE, PAN_RANGE + 1):
        for dy in range(-PAN_RANGE, PAN_RANGE + 1):
            x, y = cx + dx, cy + dy
            if (m, x, y) in BLIND or (m, x, y) in tried or REST.get((m, x // PAN_BANK_TILES, y // PAN_BANK_TILES), 0) > now:
                continue
            w = wet.get((x, y)) if wet is not None else wet_tile(x, y, m)
            if w is not None:
                out.append(w)
    if cz is None:
        cz = here()[2]
    origin = (cx, cy, cz)

    def tally(w):
        return LEARN.get(water_key(w, origin)) or [0, 0]
    out = [w for w in out if not (tally(w)[0] == 0 and tally(w)[1] >= LEARN_NEVER)]   # THE PAN LEARNS ITS WATER
    if sight and out:
        out = [w for w in out if sees(m, origin, w)]
    out.sort(key=lambda w: ((-(tally(w)[0] / float(sum(tally(w))))) if sum(tally(w)) else -0.5,
                            cheb(w[0], w[1], cx, cy)))
    return out


# MOUNTED FOR A LONG WALK (owner, 2026-10-16 00:5x: "we're not mounting in standalone currently, but we could if we have a
# long distance run planned and find a mount statue in the inventory"). A walk of MOUNT_WALK_TILES or more rides an
# ethereal mount statue carried in the backpack -- the Omni Panner's own rule ("mounted only past 40 steps"). Panning
# gets off it again (ON FOOT TO PAN, dismount()); no statue, no ride.
MOUNT_WALK_TILES = 40
MOUNT_STATUE_WORD = "ethereal"


def mount_for_long_walk(x, y):
    """On an ethereal mount statue from the pack before a walk of MOUNT_WALK_TILES or more. Never raises."""
    try:
        pos = here()
        if Player.Mount or cheb(pos[0], pos[1], x, y) < MOUNT_WALK_TILES:
            return
        statue = next((it for it in list(getattr(Player.Backpack, "Contains", None) or [])
                       if MOUNT_STATUE_WORD in name_of(it).lower()), None)
        if statue is None:
            return
        read_ethereal()                 # KNOWN IN ADVANCE: read while the statue is still in the pack
        Items.UseItem(statue.Serial)
        waited = 0
        while not Player.Mount and waited < 2000:
            Misc.Pause(200)
            waited += 200
    except Exception:
        pass


def walk_to(x, y, z, stop=None):
    """The client's own pathfinder to (x, y, z). True when we stand there; False at once when `stop()` says so."""
    mount_for_long_walk(x, y)
    try:
        Player.PathFindTo(x, y, z)
    except Exception:
        return False
    last, still_since = here(), time.time()
    deadline = time.time() + 5 + cheb(x, y, last[0], last[1]) * 0.6
    while time.time() < deadline:
        Misc.Pause(250)
        if stop is not None and stop():
            return False
        pos = here()
        if cheb(pos[0], pos[1], x, y) == 0:
            return True
        if pos != last:
            last, still_since = pos, time.time()
        elif time.time() - still_since > 2.5:
            break
    pos = here()
    return cheb(pos[0], pos[1], x, y) == 0


def walk_on(visit, radius):
    """No water in reach: walk to the nearest place to stand with fresh water in reach. True there."""
    cx, cy, _cz = here()
    m = Player.Map
    r = radius + PAN_RANGE
    wet = {}
    for dx in range(-r, r + 1):
        for dy in range(-r, r + 1):
            w = wet_tile(cx + dx, cy + dy, m)
            if w is not None:
                wet[(cx + dx, cy + dy)] = w
    if not wet:
        return False
    stands = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            x, y = cx + dx, cy + dy
            if (x, y) in wet or (m, x, y) in visit.walked or (dx, dy) == (0, 0):
                continue
            if risky_spot(x, y, m) or others_near(m, x, y):     # NOT THE SAME AREAS on the walk to more water too
                continue
            z = standable(x, y, m)
            if z is not None and water_near(x, y, m, wet, visit.tried, sight=False):
                stands.append((max(abs(dx), abs(dy)), x, y, z))
    stands.sort()
    tries = PAN_WALK_TRIES if radius <= PAN_WALK_RADIUS else PAN_SEEK_TRIES
    picked = []
    for d, x, y, z in stands:
        if len(picked) >= tries:
            break
        if any(cheb(x, y, px, py) < PAN_TRY_SPREAD for _d, px, py, _z in picked):
            continue
        if not water_near(x, y, m, wet, visit.tried, cz=z):
            continue                    # no walk to a stand whose water we could not see from it
        picked.append((d, x, y, z))
    for _d, x, y, z in picked:
        visit.walked.add((m, x, y))
        if walk_to(x, y, z, stop=in_danger):
            return True
        pos = here()
        if water_near(pos[0], pos[1], m, None, visit.tried):
            return True                  # stopped short, but with water in reach
    return False


SHORE_OUT_TILES = 150          # THE WALK OUT goes this far from the rune at most
SHORE_HOP_MIN = 15             # each hop takes us at least this much farther out
SHORE_HOPS = 10                # ... and a visit walks out this many hops at most
SHORE_WALK_FAILS = 4           # walks from one place that got no farther out before the walk out ends there


def walk_out_ended(visit, why):
    """THE WALK OUT's end, said once: how far out, where, and why. False."""
    ox, oy = visit.origin
    x, y, _z = here()
    log("The walk out from %s ended %d tiles out at %d,%d: %s." % (
        base_name(visit.rune["name"]), cheb(x, y, ox, oy), x, y, why), HUE_BAD if "danger" in why else HUE_GOOD)
    return False


def shore_walk_out(visit):
    """THE WALK OUT (owner, 10-15: "Yeah, build it." -- the town shores are everyone's, and spent): the water in reach
    of the rune spent, on along the shore, a hop at a time, each a place to stand by water at least SHORE_HOP_MIN
    farther from the rune than the last, up to SHORE_OUT_TILES -- until fresh water is in reach. A find there marks a
    rune (maybe_mark). THE DEFENSIVE EXIT (owner, 10-15: "Make sure rune building has defensive exit built in. Don't
    move through previously unsafe areas to find new ones."): any danger stops the walk at once and the visit flees;
    no hop goes to, or walks a line past, a danger spot; a walk that comes near one stops. True with fresh water in
    reach."""
    ox, oy = visit.origin
    m = Player.Map
    ended = lambda reason: walk_out_ended(visit, reason)
    while True:
        if visit.hops >= SHORE_HOPS:
            return ended("%d hops a visit" % SHORE_HOPS)
        cx, cy, _cz = here()
        d0 = cheb(cx, cy, ox, oy)
        if d0 >= SHORE_OUT_TILES:
            return ended("%d tiles out, as far as it goes" % SHORE_OUT_TILES)
        r = PAN_SEEK_RADIUS + PAN_RANGE
        wet = set()
        for dx in range(-r, r + 1):
            for dy in range(-r, r + 1):
                if wet_tile(cx + dx, cy + dy, m) is not None:
                    wet.add((cx + dx, cy + dy))
        if not wet:
            return ended("no water within %d tiles" % PAN_SEEK_RADIUS)
        stands = []
        for dx in range(-PAN_SEEK_RADIUS, PAN_SEEK_RADIUS + 1):
            for dy in range(-PAN_SEEK_RADIUS, PAN_SEEK_RADIUS + 1):
                x, y = cx + dx, cy + dy
                out = cheb(x, y, ox, oy)
                if (x, y) in wet or out < d0 + SHORE_HOP_MIN or out > SHORE_OUT_TILES or (m, x, y) in visit.walked:
                    continue
                if not any((x + ax, y + ay) in wet for ax in range(-PAN_RANGE, PAN_RANGE + 1)
                           for ay in range(-PAN_RANGE, PAN_RANGE + 1)):
                    continue
                stands.append((max(abs(dx), abs(dy)), x, y))
        stands.sort()
        moved = False
        skipped = 0
        failed = 0
        for _d, x, y in stands:
            if risky_spot(x, y, m) or others_near(m, x, y) or line_near_danger(m, cx, cy, x, y):
                skipped += 1
                continue
            z = standable(x, y, m)
            if z is None:
                continue
            visit.walked.add((m, x, y))
            walk_to(x, y, z, stop=lambda: in_danger() or near_danger(m, *here()[:2]))
            if in_danger():
                return ended("danger -- leaving")   # THE DEFENSIVE EXIT: the visit flees from here
            pos = here()
            if near_danger(m, pos[0], pos[1]):
                return ended("near a danger spot, so no farther")
            if cheb(pos[0], pos[1], ox, oy) <= d0:
                failed += 1             # got nowhere: the next stand (10-15 19:20: ten of these spent a visit's hops)
                if failed >= SHORE_WALK_FAILS:
                    break
                continue
            visit.hops += 1             # only a hop that took us farther out counts
            visit.out = max(visit.out, cheb(pos[0], pos[1], ox, oy))
            moved = True
            break
        if not moved and failed >= SHORE_WALK_FAILS:
            return ended("%d walks farther out from here got nowhere" % failed)
        if not moved:
            return ended("no shore farther out to walk to (%d set aside by danger, an invasion or another panner)" %
                         skipped if skipped else "no shore farther out to walk to")
        if walk_on(visit, PAN_WALK_RADIUS) or water_near(here()[0], here()[1], m, None, visit.tried):
            x, y, _z = here()
            log("Fresh water %d tiles out from %s, at %d,%d." % (cheb(x, y, ox, oy), base_name(visit.rune["name"]),
                                                                  x, y))
            return True


def dismount():
    try:
        if Player.Mount:
            Mobiles.UseMobile(Player.Serial)
            Misc.Pause(700)
            read_ethereal()             # KNOWN IN ADVANCE: the statue is back in the pack
    except Exception:
        pass


def classify(texts):
    """The first answer among `texts` that settles a sift; "busy" only when nothing else came."""
    busy = None
    for t in texts:
        low = t.lower()
        if not low or low.startswith("["):
            continue
        for verdict, keys in PAN_REPLIES:
            if any(k in low for k in keys):
                if verdict == "busy":
                    busy = busy or (verdict, t)
                    break
                return verdict, t
    return busy or (None, "")


FILL_WHILE_SIFTING = [True]    # a find since the last fill: the next sift's wait fills an order with it
SIFT_FILL_AT_S = 1.0           # ... this far into the sift (10-15 19:01-19:03: five fills at 1 s, every one taken, and
                               # the sifts with nuggets answered at 8.3 s as ever)


def fill_while_sifting(t0, visit):
    """FILL WHILE SIFTING (owner, 10-15: "Normal behavior."): the sift's own wait fills the open order closest to done
    with a stack of its size -- an order used while a sift is under way leaves the sift alone (tested 10-15 19:0x).
    The journal lines the fill brought, so the sift's answer is told from them; None when nothing was filled."""
    if not FILL_WHILE_SIFTING[0] or not orders_on():
        return None
    FILL_WHILE_SIFTING[0] = False
    have = goods()
    deed = next((d for d in sorted(order_deeds(), key=to_go) if d[1] < d[2] and have.get(d[3])), None)
    if deed is None:
        return None
    Misc.Pause(max(0, int((t0 + SIFT_FILL_AT_S - time.time()) * 1000)))
    stamp = newest_journal_timestamp()
    Items.UseItem(deed[0])
    if Target.WaitForTarget(2000, True):
        Target.TargetExecute(have[deed[3]][0].Serial)
    Misc.Pause(800)
    now = read_deed(Items.FindBySerial(deed[0].Serial) or deed[0])
    if now is not None and now[1] > deed[1]:
        visit.filled += now[1] - deed[1]
    return journal_texts_after(stamp)


# THE BOW IS THE PROOF (owner, 2026-10-16 01:2x: "why we kept waiting when no animation fired. can RE detect the
# animation?" -- "okay, do that"). A sift the shard takes starts with our bow: an animation packet (0xE2) after 894 of 992
# target replies in the Omni Panner's packet log, and nothing at all after the rest -- the targets it never took, which
# sat out SIFT_WAIT_S each (Cove, 10-16 01:11-01:14: eight of them). RazorEnhanced has no animation call, but its
# packet logger writes the packets it is told to (only 0xE2 here) to a file: a target is left at once when no bow of
# ours comes within BOW_WAIT_S. The log's lines are only trusted once BOW_PROVEN answered sifts have shown our bow in
# it; until then -- or if it never shows one -- every sift is waited out as before. THE LOG ONLY FOR THE SIFT (10-16
# 01:2x): the logger writes every packet whatever the whitelist says (620 KB in 2 minutes, ~18 MB an hour a panner), so
# it runs only from a sift's target to its answer -- started fresh then, stopped after -- and the file holds one sift.
BOW_FILE = "Bows.log"
BOW_WAIT_S = 1.5
BOW_PROVEN = 3
BOW_GIVE_UP = 5                # answered sifts with no bow read: the log is not read here -- said once, waited out
BOW = {"on": None, "size": 0, "seen": 0, "unseen": 0, "said": False}


def bow_start():
    """The packet logger on, writing only animation packets to BOW_FILE. Never raises."""
    if BOW["on"] is not None:
        return BOW["on"]
    BOW["on"] = False
    try:
        if not ensure_char_dir():
            return False
        path = char_path(BOW_FILE)
        bow_stop()                       # a logger left running by an earlier run
        PacketLogger.Reset()
        PacketLogger.AddWhitelist(0xE2)
        BOW["path"] = path
        BOW["on"] = True
    except Exception:
        BOW["on"] = False
    return BOW["on"]


def bow_mark():
    """THE LOG ONLY FOR THE SIFT: the logger started fresh, just before the target -- a sift looks only at what follows."""
    BOW["size"] = 0
    if not BOW.get("on"):
        return
    try:
        PacketLogger.Start(BOW["path"], False)
    except Exception:
        BOW["on"] = False


def bow_stop():
    """The logger off -- the sift is answered, or given up. Never raises."""
    try:
        PacketLogger.Stop()
    except Exception:
        pass


def bow_seen():
    """True when our own bow is in the log past the mark."""
    if not BOW.get("on"):
        return False
    try:
        with open(BOW["path"], "rb") as f:
            f.seek(BOW["size"])
            text = f.read().decode("latin-1", "replace")
    except Exception:
        return False
    flat = re.sub(r"[^0-9A-Fa-f]", "", text).upper()
    return ("E2%08X" % Player.Serial) in flat


def bow_trusted():
    return bool(BOW.get("on")) and BOW["seen"] >= BOW_PROVEN


def bow_answered(bowed):
    """A sift the shard answered: did its bow show? Proves the log, or gives it up."""
    if not BOW.get("on"):
        return
    if bowed:
        BOW["seen"] += 1
        if BOW["seen"] == BOW_PROVEN:
            log("The sift's bow is seen -- a target the shard will not take is left at once, not waited out.")
    elif BOW["seen"] < BOW_PROVEN:
        BOW["unseen"] += 1
        if BOW["unseen"] >= BOW_GIVE_UP and not BOW["said"]:
            BOW["said"] = True
            BOW["on"] = False
            log("The sift's bow could not be read from RazorEnhanced's packet log -- every sift is waited out.", HUE_BAD)


def sift(pan, w, visit):
    """One sift at water `w`: (the shard's verdict -- see PAN_REPLIES -- or None when it said nothing, its words)."""
    x, y, z, graphic = w
    clear_cursor()
    stamp = newest_journal_timestamp()
    Items.UseItem(pan)
    if not Target.WaitForTarget(2000, True):
        verdict, said = classify(journal_texts_after(stamp))
        return (verdict or "refused"), said
    bow_mark()                           # THE BOW IS THE PROOF: only a bow after this target counts
    if graphic:
        Target.TargetExecute(x, y, z, graphic)
    else:
        Target.TargetExecute(x, y, z)
    t0 = time.time()
    busy = None
    bowed = False
    fill_said = fill_while_sifting(t0, visit)
    while time.time() - t0 < SIFT_WAIT_S:
        Misc.Pause(100)
        if options_check():
            t0 = time.time()            # the time in Options is not the sift's: its answer is still read after
        if in_danger():
            bow_stop()
            return "danger", ""
        texts = journal_texts_after(stamp)
        if fill_said is not None:
            texts = [t for t in texts if t not in fill_said]
        verdict, said = classify(texts)
        if verdict == "busy":
            busy = (verdict, said)       # a sift still under way: its own answer is waited for
            continue
        bowed = bowed or bow_seen()      # THE BOW IS THE PROOF
        if verdict is not None:
            bow_stop()
            if verdict in ("find", "empty", "miss"):
                bow_answered(bowed)
            return verdict, said
        if not bowed and bow_trusted() and time.time() - t0 > BOW_WAIT_S:
            break                        # no bow: the shard did not take this target -- not waited out
    bow_stop()
    clear_cursor()
    return busy or (None, "")


def pan_at_rune(rune):
    """Pan where we stand until the water here is done. "done", "full", "flee", "invasion" or "nopan"."""
    visit = Visit(rune)
    reason = "stopped"                  # until the loop itself ends: a script stopped mid-visit records no visit
    doing("Panning at %s" % base_name(rune["name"]))
    aggro_reset()
    working_said = 0.0
    try:
        while True:
            tracker_tick()
            read_broadcasts()
            x, y, _z = here()
            m = Player.Map
            reserved = others_near(m, x, y) is not None
            if not reserved and time.time() - working_said > WORKING_FRESH_S / 3:
                note_working_at(m, x, y)        # THE PANNERS SHARE: where we work, for the others -- where we stand,
                working_said = time.time()      # never a rune we only came through (THROUGH ANOTHER'S GROUND)
            if risky_spot(x, y, m, rune["name"]):
                reason = "invasion"
                break
            if in_danger():
                reason = "flee"
                break
            if pack_full() and not (field_fill() and not pack_full()):   # FILL IN THE FIELD first
                reason = "full"
                break
            pan = find_pan()
            if pan is None and not keep_pans():
                reason = "nopan"
                break
            pan = pan or find_pan()
            water = [] if reserved else water_near(x, y, m, None, visit.tried)   # THROUGH ANOTHER'S GROUND
            under = wet_tile(x, y, m)
            if under is not None and under[3] == 0 and (m, x, y) not in visit.walked:
                visit.walked.add((m, x, y))     # standing on a dock or a bridge: dry land first
                water = []
            if not water:
                if walk_on(visit, PAN_WALK_RADIUS):
                    continue
                if not visit.sought:
                    visit.sought = True
                    if walk_on(visit, PAN_SEEK_RADIUS):
                        continue
                if shore_walk_out(visit):
                    continue
                if in_danger():
                    reason = "flee"
                    break
                reason = "done"
                break
            w = water[0]
            dismount()
            while time.time() < visit.ready_at:
                Misc.Pause(100)
                options_check()
            verdict, said = sift(pan, w, visit)
            if verdict == "danger":
                reason = "flee"
                break
            if verdict in ("find", "empty", "busy", "miss"):
                learn_note(w, (x, y, _z), True)         # THE PAN LEARNS ITS WATER
            elif verdict == "bad" and "cannot be seen" not in said.lower():
                learn_note(w, (x, y, _z), False)        # (a tile out of sight is that tile's, kept blind below)
            visit.sifts += 1
            TRACK["sifts"] += 1
            note_area(m, w[0], w[1])            # NOT THE SAME AREAS: the water we sifted
            if verdict == "find":
                visit.dry = 0
                TRACK["finds"] += 1
                FILL_WHILE_SIFTING[0] = True
            elif verdict in ("empty", "miss"):
                visit.dry += 1                  # water that answered and gave nothing; a tile it cannot see, or one it
                                                # never took as water, is set aside below and counts nothing
            if visit.dry >= VISIT_DRY_SIFTS:
                reason = "done"
                break                           # this long without a find: the water here is done
            if verdict == "mounted":
                dismount()
                continue
            if verdict == "busy":
                Misc.Pause(1000)
                continue
            if verdict in ("refused", "miss", "broke"):
                Misc.Pause(500)
                continue
            if verdict == "full":
                reason = "full"
                break
            if verdict == "not_dry":
                visit.walked.add((m, x, y))
                if not walk_on(visit, PAN_WALK_RADIUS):
                    reason = "done"
                    break
                continue
            if verdict in ("find", "empty"):
                visit.ready_at = time.time() + PAN_AFTER_ANSWER_S
            if verdict == "find":
                visit.finds += 1
                maybe_mark(rune)
                continue
            if verdict == "empty":
                REST[(m, w[0] // PAN_BANK_TILES, w[1] // PAN_BANK_TILES)] = time.time() + PAN_REST_S
                learn_save()                    # the rest kept: a restart does not try it again
                continue
            if verdict is None or "cannot be seen" in said.lower():
                BLIND.add((m, w[0], w[1]))      # never taken as water -- blind for good (THE PAN LEARNS ITS WATER)
            visit.tried.add((m, w[0], w[1]))
            learn_save()
    finally:
        note_working(None)
        if reason == "done" and visit.sifts == 0:
            NO_WATER[0] += 1             # THE STIFLED PANNER: visits that found no water to sift
        elif visit.sifts:
            NO_WATER[0] = 0
        if reason == "flee":
            note_danger_spot(AGGRO[0] or "danger")
            if visit.out < PAN_RUNE_GAP:
                blacklist_rune(rune, AGGRO[0] or "danger")
            else:                       # out on the shore: the spot, not the rune we walked out from
                log("Danger %d tiles out from %s -- that spot is never walked to or through again." % (
                    visit.out, base_name(rune["name"])), HUE_BAD)
        key = rune_key(rune)
        v, n = RUNE_STATS.get(key, [0, 0])
        if reason in ("done", "full") or visit.finds:
            RUNE_STATS[key] = [v + 1, n + visit.finds]
            save_rune_stats()
        log("%s: %d sift(s), %d find(s)%s in %.1f min -- %s." % (
            base_name(rune["name"]), visit.sifts, visit.finds,
            (", %d into orders as we sifted" % visit.filled if visit.filled else "") +
            (", walked out %d tiles along the shore" % visit.out if visit.out else ""), (time.time() - visit.t0) / 60.0,
            {"done": "no fresh water left", "full": "the pack is full", "flee": "danger",
             "invasion": "a Town Invasion", "nopan": "no Gold Pan"}.get(reason, reason)))
    return reason


# =============================================================================
# THE ROUTE -- the town runes every book starts with, the script's own Panning folder, and Harry's PO rune.
# =============================================================================

CITY_RUNES = []
OWN_RUNES = []
PO_RUNE = [None]
ROUTE_STALE = [True]


def route():
    return [r for r in CITY_RUNES + OWN_RUNES
            if not is_po_rune(r) and not is_service_rune(r) and rune_key(r) not in BLACKLIST]


def rune_in(folder_path, test):
    for r in ar_folder_runes(folder_path, quiet=True):
        if test(r):
            return r
    return None


def find_rune(test, path_key):
    """The first rune `test` takes: at the top of the book, or one folder down (the folder remembered under `path_key`
    once found). Or None."""
    saved = SETTINGS.get(path_key)
    if saved is not None and saved != "":
        hit = rune_in([p for p in saved.split(" > ") if p] if saved != "/" else [], test)
        if hit:
            return hit
    hit = rune_in([], test)
    if hit:
        SETTINGS[path_key] = "/"
        save_settings()
        return hit
    if not ar_go_root():
        return None
    top = []
    for _page, folders, _d in ar_iter_pages():
        top.extend(folders.values())
    for folder in top:
        hit = rune_in([folder], test)
        if hit:
            SETTINGS[path_key] = folder
            save_settings()
            return hit
    return None


def find_po_rune():
    """Harry's rune: at the top of the book, or one folder down. Or None."""
    return find_rune(is_po_rune, "po_path")


# THE WALK TO HARRY (owner, 2026-10-15 09:4x): with orders on and no PO rune, the first start walks to Harry from the
# Minoc town rune every book starts with -- the same street walk for everyone (planned once over the map's own walkable
# ground, about 157 steps; players cannot build in town) -- and marks "PO" beside him in the Panning folder.
PO_WAY_FROM = (2475, 417)
PO_WAY = ((2485, 420, 15), (2488, 429, 15), (2490, 439, 15), (2498, 449, 15), (2508, 459, 15), (2516, 466, 15),
          (2522, 476, 15), (2522, 486, 15), (2525, 496, 15), (2535, 499, 31), (2545, 501, 31), (2555, 508, 13),
          (2565, 515, 15), (2574, 525, 15), (2581, 531, 15), (2582, 538, 15))
PO_WAY_NEAR_TILES = 3          # a waypoint counts as reached this near
PO_WAY_START_TILES = 6         # ... and the walk starts only when the Minoc rune landed us this near its start


def walk_to_harry():
    """THE WALK TO HARRY: Minoc's town rune, PO_WAY on foot, Harry found and stood beside, "PO" marked. Harry's rune,
    or None (said why)."""
    minoc = next((r for r in CITY_RUNES if base_name(r["name"]).lower() == "minoc"), None)
    if minoc is None:
        log("No Minoc rune in %s -- orders wait for a rune named PO beside Harry." % " > ".join(CITY_FOLDER), HUE_BAD)
        return None
    doing("Walking to Harry from Minoc")
    log("No PO rune yet -- walking to Harry from Minoc to mark one.")
    if recall_rune(minoc) is not True:
        log("Could not recall to Minoc -- orders wait for a PO rune.", HUE_BAD)
        return None
    x, y, _z = here()
    if cheb(x, y, PO_WAY_FROM[0], PO_WAY_FROM[1]) > PO_WAY_START_TILES:
        log("The Minoc rune is not where the walk to Harry starts -- orders wait for a PO rune.", HUE_BAD)
        return None
    aggro_reset()
    for wx, wy, wz in PO_WAY:
        for _try in (1, 2):
            if in_danger():
                log("Danger on the walk to Harry -- orders wait for the next start.", HUE_BAD)
                return None
            walk_to(wx, wy, wz, stop=in_danger)
            x, y, _z = here()
            if cheb(x, y, wx, wy) <= PO_WAY_NEAR_TILES:
                break
        else:
            log("The walk to Harry stopped at %d,%d -- orders wait for a PO rune." % (x, y), HUE_BAD)
            return None
    mobs = find_vendors(["gold panner", "harry johnson"], rng=12)
    if not mobs or not approach(mobs[0]):
        log("Harry was not found at the end of the walk -- orders wait for a PO rune.", HUE_BAD)
        return None
    if not mark_rune("PO"):
        return None
    load_route()                        # the new rune, read back from the Panning folder
    return PO_RUNE[0]


HOME_RUNE = [None]


def is_home_rune(rune):
    low = base_name(rune["name"]).lower()
    return low == "home" or low.startswith("home ")


def find_home_rune():
    """THE WORKING CHEST's rune: one named Home, at the top of the book or one folder down. Or None."""
    return find_rune(is_home_rune, "home_path")


CITY_RUNES_SEEN = [0]          # the most town runes a read has found this run


def load_route():
    city = ar_folder_runes(CITY_FOLDER, quiet=True)
    if len(city) < CITY_RUNES_SEEN[0]:
        # A SHORT READ IS READ AGAIN (10-15 13:02: 9 of the 19 town runes came back, and ten towns left the route)
        again = ar_folder_runes(CITY_FOLDER, quiet=True)
        city = again if len(again) > len(city) else city
    CITY_RUNES_SEEN[0] = max(CITY_RUNES_SEEN[0], len(city))
    CITY_RUNES[:] = city
    own = ar_folder_runes([OWN_FOLDER], quiet=True)
    if len(own) < len(OWN_RUNES):
        again = ar_folder_runes([OWN_FOLDER], quiet=True)
        own = again if len(again) > len(own) else own
    OWN_RUNES[:] = own
    register_spots()
    own_po = next((r for r in OWN_RUNES if is_po_rune(r)), None)
    PO_RUNE[0] = own_po or PO_RUNE[0]
    ROUTE_STALE[0] = False
    usable = route()
    dead = sum(1 for r in usable if rune_dead(r))
    log("Route: %d town rune(s) in %s, %d of your own in %s%s." % (
        len(CITY_RUNES), " > ".join(CITY_FOLDER),
        len([r for r in OWN_RUNES if not is_po_rune(r) and not is_service_rune(r)]), OWN_FOLDER,
        "; %d passed over (no finds)" % dead if dead else ""))
    return usable


def maybe_mark(rune):
    if not opt("mark_runes") or len(OWN_RUNES) >= PAN_MAX_RUNES:
        return
    x, y, _z = here()
    world = WORLD_NAMES.get(Player.Map, "").lower()
    for r in route():
        c = r.get("coord")
        if c and len(c) >= 2 and world_label(r["name"]) in ("", world) and cheb(x, y, c[0], c[1]) < PAN_RUNE_GAP:
            return
    if hostiles_near() or risky_spot(x, y, Player.Map) or others_near(Player.Map, x, y) or \
            near_danger(Player.Map, x, y):
        return                          # THE PANNERS SHARE: never a rune by another panner's
    stem = re.sub(r"\s+\d+$", "", base_name(rune["name"])) or "Pan"
    names = set(base_name(r["name"]).lower() for r in route())
    n = 2
    while ("%s %d" % (stem, n)).lower() in names:
        n += 1
    name = "%s %d" % (stem, n)
    if mark_rune(name):
        OWN_RUNES.append({"name": "%s (%s)" % (name, WORLD_NAMES.get(Player.Map, "")), "coord": [x, y], "page": 0,
                          "button": 0, "path": [OWN_FOLDER]})
        ROUTE_STALE[0] = True


# =============================================================================
# UNLOADING -- at the nearest bank.
# =============================================================================

LOOT_WORDS = ("gold nugget", "gold brick", "rough stone", "bank check", "diamond", "ruby", "emerald", "sapphire",
              "amethyst", "citrine", "tourmaline", "amber", "pearl", "delicate scale")
KEEP_WORDS = ("gold pan", "panning order", "tinker", "iron ingot", "runebook", "rune book", "spellbook", "gold coin",
              "backpack", "bag", "pouch", "key", "book")
START_PACK = set()
NEVER_MOVED = ("storage", "book", "key")   # a storage key or an order book -- the Gold Panner key among them -- is never
                                         # banked or trashed, however many of one we hold


# WHAT THE PLAYER BROUGHT (owner, 2026-10-16 09:3x: "scan for panning items already in the pack. If they maybe have 30
# orders already when they start it, then we can just handle that situation. Same with any of the regular items
# collectable from panning. Not epics."): the panning goods in the pack at Start are the panner's to handle -- nuggets,
# bricks, rough stone, gems and checks unloaded and used for orders, the orders carried, filled and turned in, never
# trashed (prune_deeds()) -- but an Epic one is never moved.
_epic_seen = {}


def is_epic(it):
    """True when the item's properties call it Epic -- read once a serial."""
    if it.Serial not in _epic_seen:
        try:
            Items.WaitForProps(it.Serial, 1000)
            props = " | ".join(str(p) for p in (Items.GetPropStringList(it.Serial) or [])).lower()
        except Exception:
            props = ""
        _epic_seen[it.Serial] = re.search(r"\bepic\b", props) is not None
    return _epic_seen[it.Serial]


def brought_goods_said():
    """One line at Start: the panning goods and orders already in the pack, handled like the panner's own."""
    goods, orders, epics = 0, 0, 0
    for it in pack_items():
        low = name_of(it).lower()
        if any(w in low for w in NEVER_MOVED):
            continue
        if "panning order" in low:
            orders += 1
        elif any(w in low for w in LOOT_WORDS):
            if is_epic(it):
                epics += 1
            else:
                goods += 1
    if goods or orders:
        log("In your pack at Start: %s -- handled like the panner's own%s." % (
            ", ".join(x for x in ("%d stack(s) of panning goods" % goods if goods else "",
                                  "%d Gold Panning Order(s)" % orders if orders else "") if x),
            "; %d Epic item(s) left alone" % epics if epics else ""))


def loot_in_pack():
    out = []
    for it in pack_items():
        low = name_of(it).lower()
        if any(w in low for w in NEVER_MOVED):
            continue
        if any(w in low for w in LOOT_WORDS):
            if it.Serial in START_PACK and is_epic(it):
                continue                # WHAT THE PLAYER BROUGHT: an Epic one stays
            out.append(it)
            continue
        if it.Serial in START_PACK or is_pan(it) or any(w in low for w in KEEP_WORDS):
            continue
        out.append(it)
    return out


def move_all(items, dest_serial):
    moved = 0
    for it in items:
        Items.Move(it.Serial, dest_serial, -1)
        Misc.Pause(700)
        moved += 1
    return moved


GOOD_STONES = {"small": 1, "medium": 2, "large": 3, "brick": 5}   # a piece's weight, high side: the take's weight cap


def bank_goods(bank):
    """{tier: [stacks]} of nuggets and bricks at the top of the bank box."""
    out = {}
    for it in list(getattr(bank, "Contains", None) or []):
        t = tier_of(name_of(it))
        if t:
            out.setdefault(t, []).append(it)
    return out


def plan_take(tier, n, have, banked, take):
    """`n` more of `tier` made from the pack (`have`), then the bank (`banked`), then the tier below traded up on Harry
    in whole lots. What comes out of the bank is added to `take`. True when all `n` can be made."""
    use = min(n, have.get(tier, 0))
    have[tier] = have.get(tier, 0) - use
    n -= use
    use = min(n, banked.get(tier, 0))
    banked[tier] = banked.get(tier, 0) - use
    take[tier] = take.get(tier, 0) + use
    n -= use
    if n <= 0:
        return True
    lots = TIER_LOTS.get(tier)
    if not lots:
        return False
    return plan_take(TIERS[TIERS.index(tier) - 1], n * lots, have, banked, take)


def take_for_orders(bank, where="the bank"):
    """THE BANK FILLS THE ORDERS (owner, 2026-10-15 09:1x: "Build it."): with everything panned just banked, the nuggets
    and bricks the carried orders need come back out -- the orders Harry pays best for first, each one only when the
    pack and the bank together can finish it, and never past the pack's weight setting. Nuggets banked on an earlier
    trip fill an order as well as the ones just panned."""
    deeds = order_deeds()
    if not deeds:
        return 0
    have = dict((t, count_tier(t)) for t in TIERS)
    stock = bank_goods(bank)
    banked = dict((t, sum(int(it.Amount or 1) for it in items)) for t, items in stock.items())
    room = Player.MaxWeight * opt_int("pack_pct", 20, 95) / 100.0 - Player.Weight
    take, planned = {}, 0
    for d in sorted(deeds, reverse=True, key=lambda d: (d[1] >= d[2], stone_rate(d[3], d[2]), -(d[2] - d[1]))):
        if d[1] >= d[2]:
            continue
        h, b, t = dict(have), dict(banked), dict(take)
        if not plan_take(d[3], d[2] - d[1], h, b, t):
            continue
        weight = sum((t[k] - take.get(k, 0)) * GOOD_STONES[k] for k in t)
        if weight > room:
            continue
        have, banked, take, room, planned = h, b, t, room - weight, planned + 1
    moved = 0
    for tier, n in take.items():
        left = n
        for it in stock.get(tier, []):
            if left <= 0:
                break
            amount = min(left, int(it.Amount or 1))
            Items.Move(it.Serial, Player.Backpack.Serial, amount)
            Misc.Pause(700)
            left -= amount
            moved += amount
    if moved:
        log("From %s for %d order(s): %s." % (where, planned, ", ".join(
            "%d %s" % (n, k) for k, n in sorted(take.items(), key=lambda kv: TIERS.index(kv[0])) if n)))
    return planned


def chest_serial():
    try:
        return int(SETTINGS.get("chest") or "0", 16) or None
    except ValueError:
        return None


def working_chest_on():
    return chest_serial() is not None and HOME_RUNE[0] is not None


def open_working_chest():
    """THE WORKING CHEST (owner, 2026-10-15 09:3x): home by the Home rune, beside the chest set in Options, and open --
    the chest, or None (the bank is used instead)."""
    serial = chest_serial()
    home = HOME_RUNE[0]
    if serial is None or home is None:
        return None
    doing("Unloading at your working chest")
    if recall_rune(home) is not True:
        log("Could not recall to your Home rune -- the bank instead.", HUE_BAD)
        return None
    chest = Items.FindBySerial(serial)
    if chest is None:
        CHEST_MISSES[0] += 1
        if CHEST_MISSES[0] >= CHEST_MISSES_FORGET:
            forget_chest("was not by your Home rune %d trips running" % CHEST_MISSES[0])
        else:
            log("Your working chest is not in sight of your Home rune -- the bank instead.", HUE_BAD)
        return None
    CHEST_MISSES[0] = 0
    if Player.DistanceTo(chest) > CHEST_REACH_TILES:
        walk_beside(chest, CHEST_REACH_TILES)
    if Player.DistanceTo(chest) > CHEST_REACH_TILES:
        # WALK TO IT IN THE HOUSE (owner, 10-15 12:3x: "Walk to it if we're in the house with it"): a closed door between
        # the Home rune and the chest stops the client's own path -- the doors near are opened, the walk tried again,
        # and each door put back as it was
        doors = toggle_doors_near(CHEST_DOOR_TILES)
        if doors:
            walk_beside(chest, CHEST_REACH_TILES)
            if Player.DistanceTo(chest) > CHEST_REACH_TILES:
                walk_to(chest.Position.X, chest.Position.Y, chest.Position.Z)
            toggle_doors(doors)
    if Player.DistanceTo(chest) > CHEST_REACH_TILES:
        x, y, z = here()
        log("Your working chest could not be reached from your Home rune (we stand at %d,%d,%d; it is at %d,%d,%d; "
            "tried %s; by it: %s) -- the bank instead." % (x, y, z, chest.Position.X, chest.Position.Y,
                                                           chest.Position.Z, "; ".join(WALK_BESIDE_TRIES) or "nothing",
                                                           items_by(chest, 2)), HUE_BAD)
        return None
    stamp = newest_journal_timestamp()
    Items.UseItem(chest)
    try:
        Items.WaitForContents(chest, 3000)
    except Exception:
        Misc.Pause(1000)
    refused = next((t for t in journal_texts_after(stamp) if any(w in t.lower() for w in CHEST_REFUSALS)), None)
    if refused:
        forget_chest("refused us (\"%s\")" % refused)
        return None
    chest = Items.FindBySerial(serial) or chest
    if not any(r[0] == "0x%X" % chest.Serial for r in chest_rows()):
        register_chest(chest)           # THE PANNERS SHARE: on the shared list, for another panner to find
    return chest


CHEST_REACH_TILES = 2
CHEST_ITEM_LIMIT = 125         # a container's items
CHEST_FREE_KEPT = 15           # ... of which this many are left free: working space (owner, 10-15 10:3x)
CHEST_REFUSALS = ("permission", "cannot access", "can't access", "not accessible", "is locked", "do not own")
CHEST_MISSES = [0]
CHEST_MISSES_FORGET = 3        # the chest gone from by the Home rune this many trips running: forgotten
CHECKS_TO_BANK = 3             # with a working chest, bank checks wait in the pack until this many, then go to the bank


# THE PANNERS SHARE (owner, 10-15 10:4x: "If a fresh run detects a Home rune near the existing working chest, default to
# trying to share that. Also have them avoid using panning spots near the already marked runes of another panner" --
# "With multiple panners, designate one to handle turn ins."). Three small shared files: the working chests set (where
# each stands, and the panner that turns in the orders kept in it), every panner's marked spots, and the rune each is
# working now. A panner never marks or pans within PAN_RUNE_GAP of another's marked rune or of where another works.
CHESTS_FILE = "Chests.txt"     # chest serial, map, x, y, z, the turn-in panner's serial
SPOTS_FILE = "Spots.txt"       # panner serial, map, x, y, rune name
WORKING_FILE = "Working.txt"   # panner serial, map, x, y, when
# NOT THE SAME AREAS (owner, 2026-10-16 00:3x: "they should just not mark or pan the same areas" -- "not all towns are
# created equally, so dividing based on town runes is no good" -- held "while it's recent"). Where each panner actually
# sifts goes on a shared list; another panner neither pans nor marks within PAN_RUNE_GAP of a spot sifted there in the
# last AREA_HOLD_S. Nothing is divided ahead of time: a town with water enough holds two panners on different shores,
# and an area left alone that long is open again.
AREAS_FILE = "Areas.txt"       # panner serial, map, x, y, when it last sifted there
AREA_HOLD_S = 3 * 3600
AREA_CELL = 10                 # one row per panner a cell this many tiles across: the list stays small
# A PANNER'S RESERVE (owner, 2026-10-16 01:0x: "they should reserve larger areas to increase efficiency" -- "yes, set it
# to 40"): another panner keeps this far from our sifts, our runes and where we work -- PAN_SEEK_RADIUS, the most a visit
# looks for water from its rune, so each holds the stretch it can reach. At 20 (PAN_RUNE_GAP, our own runes' spacing)
# they leapfrogged: 10-16 00:53 one started at 1413,1696, 21 tiles from the other's 00:39 sifts on the same shore.
PANNER_RESERVE_TILES = 40
CHEST_SHARE_TILES = 20         # a Home rune this near a chest set by another panner shares that chest
WORKING_FRESH_S = 180          # a "working here" this old is a panner that stopped
SHARED_READ_S = 15             # the shared files are read again at most this often
_shared_cache = {}


def read_rows(name, fresh=False):
    hit = _shared_cache.get(name)
    if hit and not fresh and time.time() - hit[0] < SHARED_READ_S:
        return hit[1]
    rows = []
    try:
        with open(data_path(name)) as f:
            rows = [l.rstrip("\n").split("\t") for l in f if l.strip()]
    except Exception:
        rows = []
    _shared_cache[name] = (time.time(), rows)
    return rows


def write_rows(name, rows):
    if not ensure_data_dir():
        return
    try:
        with open(data_path(name), "w") as f:
            for r in rows:
                f.write("\t".join(str(v) for v in r) + "\n")
        _shared_cache[name] = (time.time(), [[str(v) for v in r] for r in rows])
    except Exception:
        pass


def chest_rows(fresh=False):
    return [r for r in read_rows(CHESTS_FILE, fresh=fresh) if len(r) >= 6]


def register_chest(chest):
    """The chest set here, on the shared list -- its turn-in panner kept, or this one when it has none."""
    serial = "0x%X" % chest.Serial
    rows = chest_rows(fresh=True)
    old = next((r for r in rows if r[0] == serial), None)
    turnin = old[5] if old and old[5] else my_id()
    p = chest.Position
    write_rows(CHESTS_FILE, [r for r in rows if r[0] != serial] + [[serial, Player.Map, p.X, p.Y, p.Z, turnin]])


def turnin_panner():
    """THE ONE WHO TURNS IN: the panner named on the shared list for our working chest -- ourselves with no chest (each
    panner turns in its own), or when the chest has nobody yet (the first to ask takes it)."""
    serial = SETTINGS.get("chest") or ""
    if not serial:
        return my_id()
    rows = chest_rows()
    row = next((r for r in rows if r[0] == serial), None)
    if row is None:
        return my_id()
    if not row[5]:
        rows = chest_rows(fresh=True)
        row = next((r for r in rows if r[0] == serial), row)
        if not row[5]:
            row[5] = my_id()
            write_rows(CHESTS_FILE, rows)
    return row[5]


def handles_turnins():
    return not working_chest_on() or turnin_panner() == my_id()


def set_turnin_panner(who):
    serial = SETTINGS.get("chest") or ""
    rows = chest_rows(fresh=True)
    for r in rows:
        if r[0] == serial:
            r[5] = who
    write_rows(CHESTS_FILE, rows)


def adopt_shared_chest():
    """A panner with no working chest whose Home rune stands by a chest another panner set: that chest is ours too."""
    if chest_serial() is not None or not chest_rows():
        return
    home = HOME_RUNE[0] or find_home_rune()
    HOME_RUNE[0] = home
    c = (home or {}).get("coord") or []
    if len(c) < 2:
        return
    for r in chest_rows():
        try:
            same_map = int(r[1]) == rune_map(home)
            near = cheb(int(r[2]), int(r[3]), c[0], c[1]) <= CHEST_SHARE_TILES
        except ValueError:
            continue
        if same_map and near:
            SETTINGS["chest"] = r[0]
            save_settings()
            chest_state_reset()
            log("Sharing the working chest by your Home rune (another panner set it)%s." % (
                "" if r[5] and r[5] != my_id() else " -- this panner turns in the orders"))
            return


def register_spots():
    """Our own marked runes on the shared spot list (THE PANNERS SHARE)."""
    mine = [[my_id(), rune_map(r), r["coord"][0], r["coord"][1], base_name(r["name"])] for r in OWN_RUNES
            if len(r.get("coord") or []) >= 2 and not is_po_rune(r) and not is_service_rune(r)]
    write_rows(SPOTS_FILE, [r for r in read_rows(SPOTS_FILE, fresh=True) if r and r[0] != my_id()] + mine)


def others_near(m, x, y):
    """Another panner's marked rune, the rune it is working now, or a spot it sifted in the last AREA_HOLD_S (NOT THE
    SAME AREAS), within PANNER_RESERVE_TILES of (x, y)."""
    now = time.time()
    for r in read_rows(SPOTS_FILE):
        try:
            if r[0] != my_id() and int(r[1]) == m and cheb(int(r[2]), int(r[3]), x, y) < PANNER_RESERVE_TILES:
                return "marked"
        except (ValueError, IndexError):
            continue
    for r in read_rows(WORKING_FILE):
        try:
            if (r[0] != my_id() and now - float(r[4]) < WORKING_FRESH_S and int(r[1]) == m
                    and cheb(int(r[2]), int(r[3]), x, y) < PANNER_RESERVE_TILES):
                return "working"
        except (ValueError, IndexError):
            continue
    for r in read_rows(AREAS_FILE):     # NOT THE SAME AREAS
        try:
            if (r[0] != my_id() and now - float(r[4]) < AREA_HOLD_S and int(r[1]) == m
                    and cheb(int(r[2]), int(r[3]), x, y) < PANNER_RESERVE_TILES):
                return "panned"
        except (ValueError, IndexError):
            continue
    return None


def note_area(m, x, y):
    """NOT THE SAME AREAS: we sifted at (x, y) now -- on the shared list (one row a cell; rows past AREA_HOLD_S go)."""
    now = time.time()
    cell = (int(m), int(x) // AREA_CELL, int(y) // AREA_CELL)
    keep = []
    for r in read_rows(AREAS_FILE, fresh=True):
        try:
            if now - float(r[4]) >= AREA_HOLD_S:
                continue
            if r[0] == my_id() and (int(r[1]), int(r[2]) // AREA_CELL, int(r[3]) // AREA_CELL) == cell:
                continue
        except (ValueError, IndexError):
            continue
        keep.append(r)
    write_rows(AREAS_FILE, keep + [[my_id(), int(m), int(x), int(y), "%.0f" % now]])


def rune_taken(rune):
    c = rune.get("coord") or []
    return len(c) >= 2 and others_near(rune_map(rune), c[0], c[1]) is not None


def note_working_at(m, x, y):
    """Where we work now -- (x, y) on map m -- on the shared list."""
    rows = [r for r in read_rows(WORKING_FILE, fresh=True) if r and r[0] != my_id()]
    write_rows(WORKING_FILE, rows + [[my_id(), int(m), int(x), int(y), "%.0f" % time.time()]])


def note_working(rune):
    """The rune we work now on the shared list -- None takes us off it."""
    rows = [r for r in read_rows(WORKING_FILE, fresh=True) if r and r[0] != my_id()]
    c = (rune or {}).get("coord") or []
    if rune is not None and len(c) >= 2:
        rows.append([my_id(), rune_map(rune), c[0], c[1], "%.0f" % time.time()])
    write_rows(WORKING_FILE, rows)


def chest_state_reset():
    """A chest set, cleared or forgotten: what was learned of the old one goes with it -- its misses, its room."""
    CHEST_MISSES[0] = 0
    CHEST_ROOM_SEEN[0] = 0


def forget_chest(why):
    """ACCESS REMOVED IS FOR GOOD (owner, 10-15 10:3x: "when access to a home chest is removed, don't access that
    again"): the chest is no longer used until the player sets one again in Options."""
    SETTINGS["chest"] = ""
    save_settings()
    chest_state_reset()
    log("Your working chest %s -- it is no longer used, and the bank is used again (Options sets a chest)." % why,
        HUE_BAD)


def stacks_onto(chest, it):
    """True when `it` joins a stack already in the chest -- nuggets, bricks, rough stone -- and takes no new slot."""
    if not any(w in name_of(it).lower() for w in ("gold nugget", "gold brick", "rough stone")):
        return False
    return any(c.ItemID == it.ItemID and c.Hue == it.Hue for c in list(getattr(chest, "Contains", None) or []))


def into_chest_or_trash(chest):
    """NEVER THE BANK FOR OVERFLOW (owner, 10-15 10:3x: "don't fill the bank if we have a working chest. Trash them."):
    everything panned into the chest while it has room past its working space -- a stack that joins one already there
    always fits -- and what would need a slot it has not got into the Trash Bag. Checks stay for the bank. The stacks
    moved."""
    moved, trashed = 0, []
    for it in [i for i in loot_in_pack() if not is_check(i)]:
        if chest_room(chest) > 0 or stacks_onto(chest, it):
            Items.Move(it.Serial, chest.Serial, -1)
            Misc.Pause(700)
            moved += 1
            chest = Items.FindBySerial(chest.Serial) or chest
            continue
        bag = trash_bag()
        if bag is None:
            log("Your working chest is down to its working space and there is no Trash Bag -- %s stays in the pack." %
                (name_of(it) or "an item"), HUE_BAD)
            continue
        Items.Move(it.Serial, bag.Serial, -1)
        Misc.Pause(700)
        trashed.append(name_of(it) or "?")
    if trashed:
        log("Your working chest is down to its working space (%d slots kept free) -- into the Trash Bag: %s." % (
            CHEST_FREE_KEPT, ", ".join(trashed[:6]) + (" and %d more" % (len(trashed) - 6) if len(trashed) > 6 else "")),
            HUE_BAD)
    return moved


def chest_room(chest):
    return CHEST_ITEM_LIMIT - CHEST_FREE_KEPT - len(list(getattr(chest, "Contains", None) or []))


def is_check(it):
    return "bank check" in name_of(it).lower()


def bank_stop_due(take_orders):
    """With a working chest: the bank too -- checks to deposit, or, on the way to Harry, the bank's own nuggets able to
    finish a carried order the pack cannot (THE BANK IS DRAINED). 10-15 14:42: the stop came every trip while the bank's
    nuggets finished nothing -- it is judged now by what the bank held at its last look."""
    if sum(1 for it in pack_items() if is_check(it)) >= CHECKS_TO_BANK:
        return True
    banked = SETTINGS.get("bank_goods") or ""
    if not (take_orders and banked and orders_on()):
        return False
    if banked == "1":
        return True                     # not looked at yet
    have = dict((t, count_tier(t)) for t in TIERS)
    both = dict(have)
    for part in banked.split(","):
        t, _sep, n = part.partition(":")
        if t in both and n.isdigit():
            both[t] += int(n)
    return any(d[1] < d[2] and not can_make(d[3], d[2] - d[1], have) and can_make(d[3], d[2] - d[1], both)
               for d in order_deeds())


def walk_beside(item, reach):
    """Beside `item` inside a house: the map files hold no house floors, so each try is walked at the height of the
    floor we stand on (10-15 10:14: the chest at home "could not be reached" -- the walk was aimed at the ground)."""
    ix, iy = item.Position.X, item.Position.Y
    # A STEP FIRST (owner, 10-15 12:3x: "it's just 1 tile north from our range to open"): straight steps toward it -- the
    # client's pathfinder would not take that one step at home; a plain step needs no path
    for _step in range(STEP_TRIES):
        if Player.DistanceTo(item) <= reach:
            return True
        x0, y0, _z0 = here()
        d = STEP_NAMES.get((max(-1, min(1, ix - x0)), max(-1, min(1, iy - y0))))
        if d is None:
            break
        try:
            Player.Walk(d)
        except Exception:
            break
        Misc.Pause(STEP_PAUSE_MS)
    if Player.DistanceTo(item) <= reach:
        return True
    px, py, pz = here()
    # every tile within `reach` of it, the nearest to us first -- not only the eight beside it (10:36: those were all
    # taken at home, the chest three tiles off and one step north enough)
    beside = sorted((cheb(ix + dx, iy + dy, px, py), ix + dx, iy + dy)
                    for dx in range(-reach, reach + 1) for dy in range(-reach, reach + 1) if (dx, dy) != (0, 0))
    WALK_BESIDE_TRIES[:] = []
    for _d, x, y in beside[:8]:
        walk_to(x, y, pz)
        if Player.DistanceTo(item) <= reach:
            return True
        ax, ay, _az = here()
        WALK_BESIDE_TRIES.append("%d,%d->%d,%d" % (x, y, ax, ay))
    return Player.DistanceTo(item) <= reach


WALK_BESIDE_TRIES = []         # the last walk_beside()'s tries: the tile asked, where the walk ended
STEP_NAMES = {(0, -1): "North", (1, -1): "Right", (1, 0): "East", (1, 1): "Down", (0, 1): "South", (-1, 1): "Left",
              (-1, 0): "West", (-1, -1): "Up"}   # RazorEnhanced's walk directions, by the step's (dx, dy)
STEP_TRIES = 6                 # a turn then a step each -- three tiles at most
STEP_PAUSE_MS = 450
CHEST_DOOR_TILES = 6           # doors this near are opened when the walk to the chest fails


def is_door(it):
    try:
        if Statics.GetTileFlag(it.ItemID, "Door"):
            return True
    except Exception:
        pass
    return "door" in name_of(it).lower()


def toggle_doors(doors):
    for it in doors:
        Items.UseItem(it)
        Misc.Pause(500)


def toggle_doors_near(rng):
    """The doors within `rng` of us, each used once (a closed one opens) -- the list, to put them back after."""
    try:
        f = Items.Filter()
        f.Enabled = True
        f.OnGround = True
        f.RangeMax = rng
        doors = [it for it in (Items.ApplyFilter(f) or []) if is_door(it)]
    except Exception:
        doors = []
    toggle_doors(doors)
    return doors


def items_by(item, rng):
    """The things lying within `rng` of `item` -- name and tile -- for the log."""
    try:
        f = Items.Filter()
        f.Enabled = True
        f.OnGround = True
        f.RangeMax = CHEST_DOOR_TILES + 4
        near = [it for it in (Items.ApplyFilter(f) or []) if it.Serial != item.Serial
                and cheb(it.Position.X, it.Position.Y, item.Position.X, item.Position.Y) <= rng]
        def blocks(it):
            try:
                return " (blocks)" if Statics.GetTileFlag(it.ItemID, "Impassable") else ""
            except Exception:
                return ""
        return ", ".join("%s@%d,%d%s" % ((name_of(it) or "0x%X" % it.ItemID)[:24], it.Position.X, it.Position.Y,
                                         blocks(it)) for it in near[:12]) or "nothing"
    except Exception:
        return "?"


def open_a_bank():
    """The bank box: THE ETHEREAL'S BANK where we stand when it is unlocked, else the nearest banker's. None, said."""
    bank = ethereal_bank()
    if bank is None:
        banker = find_service("bank")
        if banker is None:
            return None
        bank = open_bank_here(banker)
    if bank is None:
        log("The bank did not open beside the banker.", HUE_BAD)
    return bank


# THE CHECKS BANKED AT ONCE (owner, 2026-10-16 01:0x: "bank checks right after the turn-in(s), grouped together, not one
# at a time"): Harry pays the bulk turn-in in checks, and they rode in the pack until the next unload -- a full pack or
# the next half hour (10-16 00:5x: six of them) -- where a death would drop them. After the visit's turn-ins, every
# check goes to the bank in one stop; with no working chest a pack full anyway makes that stop the unload's own.
def bank_checks():
    checks = [it for it in pack_items() if is_check(it)]
    if not checks:
        return
    doing("Banking the checks from Harry")
    bank = open_a_bank()
    if bank is None:
        return
    n = move_all(checks, bank.Serial)
    log("Banked %d check(s) from Harry in one stop." % n)


def unload(take_orders=False):
    """To the nearest bank, and everything panned into it -- then, with `take_orders`, what the carried orders need
    back out (THE BANK FILLS THE ORDERS). True once done."""
    key_absorb()                        # INGOT STORAGE: the gems we found go into the key, not the bank
    chest = open_working_chest() if working_chest_on() else None
    if chest is not None:
        n = into_chest_or_trash(chest)  # THE CHECKS GO TO THE BANK; nothing else does
        chest = Items.FindBySerial(chest.Serial) or chest
        prune_deeds(chest)              # the orders past those carried: into the chest while it has room
        if take_orders:
            take_deeds_from_chest(chest)  # ONE TURNS IN: the best orders in the chest, every panner's, come along
            take_for_orders(chest, "your working chest")
        log("Unloaded %d stack(s) into your working chest; the pack holds %d of %d stones." % (
            n, Player.Weight, Player.MaxWeight))
        if not bank_stop_due(take_orders):
            return True
        take_orders = take_orders and bool(SETTINGS.get("bank_goods"))
    doing("Unloading at a bank")
    bank = open_a_bank()
    if bank is None:
        return False
    # with the working chest just unloaded, the bank takes only the checks -- the nuggets now in the pack were taken
    # for orders and stay for Harry
    n = move_all([it for it in loot_in_pack() if chest is None or is_check(it)], bank.Serial)
    log("Unloaded %d stack(s) at the bank; the pack holds %d of %d stones." % (n, Player.Weight, Player.MaxWeight))
    if take_orders:
        Misc.Pause(600)
        take_for_orders(Player.Bank or bank)
    bank = Player.Bank or bank
    SETTINGS["bank_goods"] = ",".join("%s:%d" % (t, sum(int(it.Amount or 1) for it in items))   # THE BANK IS DRAINED
                                      for t, items in sorted(bank_goods(bank).items()))         # until none is left
    save_settings()
    if working_chest_on():
        fetch_orders_for_chest(bank)
    return True


def fetch_orders_for_chest(bank):
    """THE ORDERS GO HOME (owner, 10-15 10:3x: "move any POs from the bank to the chest at home if there is room"): the
    panning orders kept in the bank come out, as many as the chest had room for at its last look, and go into it at
    the next unload there (prune_deeds). Gems stay in the bank."""
    room = CHEST_ROOM_SEEN[0]

    def is_deed(it):
        low = name_of(it).lower()
        return "panning order" in low and not any(w in low for w in NEVER_MOVED)
    top = list(getattr(bank, "Contains", None) or [])
    deeds = [it for it in top if is_deed(it)]
    for bag in [it for it in top if getattr(it, "IsContainer", False)]:   # one bag deep too
        try:
            Items.WaitForContents(bag, 1500)
            deeds.extend(it for it in list(getattr(Items.FindBySerial(bag.Serial) or bag, "Contains", None) or [])
                         if is_deed(it))
        except Exception:
            pass
    moved = 0
    for it in deeds[:max(0, room)]:
        Items.Move(it.Serial, Player.Backpack.Serial, 1)
        Misc.Pause(700)
        moved += 1
    CHEST_ROOM_SEEN[0] -= moved
    if deeds:
        log("%d panning order(s) in the bank; %d out for your working chest%s." % (
            len(deeds), moved, "" if moved == len(deeds) else " (its room, past the working space, took no more)"))


CHEST_ROOM_SEEN = [0]          # the working chest's free room at its last look


# =============================================================================
# GOLD PANNING ORDERS AT HARRY -- a deed asks one kind: small, medium or large nuggets, or gold bricks.
# Harry trades nuggets up in whole lots (10 small a medium, 5 medium a large, 3 large a brick). A deed is
# filled by using it on the goods; a full one dropped on Harry pays a check and rough stone.
# =============================================================================

ORDER_RE = re.compile(r"(\d+)\s*/\s*(\d+)\s+(small gold nugget|medium gold nugget|large gold nugget|gold brick)", re.I)
ORDER_DONE_RE = re.compile(r"order fulfilled\s*\[\s*(\d+)\s+(small gold nugget|medium gold nugget|large gold nugget|"
                           r"gold brick)", re.I)
TIERS = ("small", "medium", "large", "brick")
TIER_LOTS = {"medium": 10, "large": 5, "brick": 3}
CHECK_PER = {"small": 33.5, "medium": 333.5, "large": 1666.5, "brick": 5000.0}
SMALL_WORTH = {"small": 1, "medium": 10, "large": 50, "brick": 150}
ORDER_ASK_EVERY_S = 30 * 60   # Harry gives one order every 30 minutes, and the next at once after a turn-in
ORDER_ASK_RETRY_S = 10 * 60   # a visit that could not ask (no recall, Harry not found) is tried again after this
ORDER_ASK_FILE = "OrderAsk.txt"   # when we last asked -- a restart does not send us to Harry early
ORDER_WAIT_RE = re.compile(r"available in about (\d+) (second|minute|hour)", re.I)
DEEDS_KEPT = 10               # THE BEST ORDERS KEPT: the orders carried past this many, the least rough stone a nugget
                              # first, go into the Trash Bag (a deed whose words were not read is never trashed)
TRASH_BAG_ID = 0x09B2
LAST_ASK = [0.0]


def load_last_ask():
    try:
        with open(char_path(ORDER_ASK_FILE)) as f:
            LAST_ASK[0] = float(f.read().strip() or 0)
    except Exception:
        LAST_ASK[0] = 0.0


def save_last_ask():
    if not ensure_char_dir():
        return
    try:
        with open(char_path(ORDER_ASK_FILE), "w") as f:
            f.write("%.0f\n" % LAST_ASK[0])
    except Exception:
        pass


def ask_due():
    return time.time() - LAST_ASK[0] >= ORDER_ASK_EVERY_S


def tier_of(name):
    low = (name or "").lower()
    if "gold brick" in low:
        return "brick"
    for t in ("small", "medium", "large"):
        if t + " gold nugget" in low:
            return t
    return None


def goods():
    out = {}
    for it in pack_items():
        t = tier_of(name_of(it))
        if t:
            out.setdefault(t, []).append(it)
    return out


def count_tier(t):
    return sum(int(it.Amount or 1) for it in goods().get(t, []))


def take_deeds_from_chest(chest):
    """ONE TURNS IN: the turn-in panner carries the best of the orders kept in the shared chest -- its own and the other
    panners' -- up to DEEDS_KEPT, judged against the nuggets in the pack and the chest together."""
    carried = order_deeds()
    room = DEEDS_KEPT - len(carried)
    if room <= 0:
        return
    stored = order_deeds(chest)
    if not stored:
        return
    stock = dict((t, count_tier(t)) for t in TIERS)
    for t, items in bank_goods(chest).items():
        stock[t] = stock.get(t, 0) + sum(int(it.Amount or 1) for it in items)
    ranked = [d for d in carry_rank(carried + stored, stock) if d[0].Serial not in set(c[0].Serial for c in carried)]
    taken = 0
    for d in ranked[:room]:
        Items.Move(d[0].Serial, Player.Backpack.Serial, 1)
        Misc.Pause(700)
        taken += 1
    if taken:
        log("%d order(s) out of the working chest to fill." % taken)


FIELD_TIERS = ("small", "medium", "large")   # the sizes a pan turns up; a brick is made only at Harry


def carry_rank(deeds, stock):
    """The orders, best to carry first: a full one (Harry's next), then EVERY SIZE CARRIED (10-15 16:16: the pack held
    185 small while the ten carried all wanted medium or large -- FILL IN THE FIELD had nowhere to put them): for each
    size a pan turns up, the open order of that size closest to done; then one `stock` can finish, one with nuggets
    in it, the most rough stone a nugget, the fewest still wanted."""
    field = {}
    for d in deeds:
        if d[1] < d[2] and d[3] in FIELD_TIERS:
            best = field.get(d[3])
            if best is None or (d[2] - d[1], -stone_rate(d[3], d[2])) < (best[2] - best[1], -stone_rate(best[3], best[2])):
                field[d[3]] = d
    slots = set(d[0].Serial for d in field.values())
    return sorted(deeds, reverse=True, key=lambda d: (
        d[1] >= d[2], d[0].Serial in slots, can_make(d[3], d[2] - d[1], stock), d[1] > 0, stone_rate(d[3], d[2]),
        -(d[2] - d[1])))


def order_deeds(container=None):
    items = list(getattr(container, "Contains", None) or []) if container is not None else pack_items()
    return [d for d in (read_deed(it) for it in items) if d is not None]


def read_deed(it):
    """(deed, got, wanted, tier) from a panning order's words, or None (not an order, or its words not read)."""
    low = name_of(it).lower()
    if "panning order" not in low or any(w in low for w in NEVER_MOVED):
        return None
    try:
        Items.WaitForProps(it.Serial, 1500)
        words = " | ".join(Items.GetPropStringList(it.Serial) or [])
    except Exception:
        words = ""
    m = ORDER_RE.search(words)
    if m:
        return (it, int(m.group(1)), int(m.group(2)), tier_of(m.group(3)))
    m = ORDER_DONE_RE.search(words)
    if m:
        return (it, int(m.group(1)), int(m.group(1)), tier_of(m.group(2)))
    return None


def field_fill():
    """FILL IN THE FIELD (owner, 10-15: "We could actually go home and bank less often as well by just filling the best
    order instead. Then we just need another method to determine storage cadence."): the pack full, its nuggets go into
    the carried orders of their own size where we stand -- for each size the order closest to done first, so it is the
    first to finish -- and only a pack still full after that goes home (the cadence: what no carried order takes). Sizes
    are traded up only at Harry. True when anything went in."""
    if not orders_on():
        return False
    filled = []
    open_deeds = [d for d in order_deeds() if d[1] < d[2]]
    for deed, got, wanted, tier in sorted(open_deeds, key=to_go):
        now = fill_deed(deed, got, wanted, tier)
        if now > got:
            filled.append("%d %s (%d / %d)" % (now - got, tier, now, wanted))
    clear_cursor()
    if filled:
        log("Filled in the field: %s; the pack holds %d of %d stones." % (
            ", ".join(filled), Player.Weight, Player.MaxWeight))
    else:
        have = goods()
        log("Nothing to fill in the field -- the orders want %s; the pack holds %s." % (
            ", ".join("%d %s" % (d[2] - d[1], d[3]) for d in open_deeds) or "nothing (none open)",
            ", ".join("%d %s" % (sum(int(it.Amount or 1) for it in have[t]), t) for t in TIERS if have.get(t))
            or "no nuggets"))
    return bool(filled)


def fill_deed(deed, got, wanted, tier):
    """The pack's `tier` nuggets into one order, stack by stack, until it is full or takes no more. Its count now."""
    for st in goods().get(tier, []):
        if got >= wanted:
            break
        clear_cursor()
        Items.UseItem(deed)
        if Target.WaitForTarget(2000, True):
            Target.TargetExecute(st.Serial)
        Misc.Pause(1200)
        now = read_deed(Items.FindBySerial(deed.Serial) or deed)
        if now is None or now[1] <= got:
            break                       # the order took none of it: left as it is
        got = now[1]
    return got


FILL_AT_HARRY_ROOM = 0.75      # FILL AT HARRY only when it leaves the pack this far under its weight setting


def absorb(tier, n, have):
    """Up to `n` of `tier` from `have` (a count per size, spent), the sizes below traded up in whole lots as Harry
    does. How many were had."""
    use = min(n, have.get(tier, 0))
    have[tier] = have.get(tier, 0) - use
    n -= use
    lots = TIER_LOTS.get(tier)
    if n <= 0 or not lots:
        return use
    lower = TIERS[TIERS.index(tier) - 1]
    got = absorb(lower, n * lots, have)
    have[lower] += got % lots           # a part lot is not traded: it stays
    return use + got // lots


def fill_at_harry_due():
    """FILL AT HARRY (owner, 10-15 17:4x: "Do it"): the pack is still full after FILL IN THE FIELD, and the carried
    orders would take enough of its nuggets, traded up at Harry, to leave it well under its weight setting -- then
    Harry, not home (17:04-17:36: every trip home carried ~185 small nuggets while ten medium and large orders waited)."""
    if not (orders_on() and handles_turnins()) or ask_due() or trip_risky(PO_RUNE[0]):
        return False                    # on the half hour THE BULK TURN-IN goes to Harry anyway; NO TRIP INTO THE HOUR
    have = dict((t, count_tier(t)) for t in TIERS)
    before = dict(have)
    for d in sorted([d for d in order_deeds() if d[1] < d[2]], key=to_go):
        absorb(d[3], d[2] - d[1], have)
    freed = sum((before[t] - have[t]) * GOOD_STONES[t] for t in TIERS)
    return freed > 0 and Player.Weight - freed <= Player.MaxWeight * opt_int("pack_pct", 20, 95) / 100.0 * \
        FILL_AT_HARRY_ROOM


def fill_at_harry():
    """FILL AT HARRY: beside Harry, the pack's nuggets traded up and into the carried orders -- closest to done first --
    and nothing turned in, no order asked: the half hour's visit does that (THE BULK TURN-IN). True when anything
    went in."""
    harry = reach_harry()
    if harry is None:
        return False
    doing("Filling orders at Harry")
    filled = []
    for deed, got, wanted, tier in sorted([d for d in order_deeds() if d[1] < d[2]],
                                          key=to_go):
        if trade_up(tier, wanted - got, harry) <= 0:
            continue
        now = fill_deed(deed, got, wanted, tier)
        if now > got:
            filled.append("%d %s (%d / %d)" % (now - got, tier, now, wanted))
    clear_cursor()
    log("Filled at Harry: %s; the pack holds %d of %d stones." % (", ".join(filled) or "nothing", Player.Weight,
                                                                 Player.MaxWeight), HUE_GOOD if filled else HUE_BAD)
    return bool(filled)


def can_make(tier, n, stock):
    made = 0
    for t in TIERS[:TIERS.index(tier) + 1]:
        lots = TIER_LOTS.get(t)
        made = int(stock.get(t, 0)) + (made // lots if lots else 0)
    return made >= n


def to_go(d):
    """Closest to done first: what an order still wants, in small nuggets (10-15 18:49: counted in its own size, a 7 brick
    order looked nearer than a 50 medium one, and 150 small went into a brick order still 900 small from done)."""
    return (d[2] - d[1]) * SMALL_WORTH[d[3]], -stone_rate(d[3], d[2])


def stone_rate(tier, wanted):
    stones = max(1, int(wanted * CHECK_PER[tier] // 5000.0))
    return stones / float(wanted * SMALL_WORTH[tier])


def trade_up(tier, n, harry):
    """At least `n` of `tier` in the pack, trading the tier below on Harry in whole lots. How many now."""
    have = count_tier(tier)
    if have >= n or tier not in TIER_LOTS:
        return have
    lower = TIERS[TIERS.index(tier) - 1]
    lots = TIER_LOTS[tier]
    got = trade_up(lower, (n - have) * lots, harry)
    give = (min(got, (n - have) * lots) // lots) * lots
    left = give
    for st in goods().get(lower, []):
        if left <= 0:
            break
        amount = min(left, int(st.Amount or 1))
        Items.Move(st.Serial, harry, amount)
        Misc.Pause(1200)
        left -= amount
    Misc.Pause(800)
    return count_tier(tier)


def ask_order(harry):
    """Ask Harry for an order. Asked too soon, he says when the next is ready -- the next ask waits for that."""
    stamp = newest_journal_timestamp()
    if not context_pick(harry, "talk"):
        return False
    LAST_ASK[0] = time.time()
    Misc.Pause(600)
    for text in journal_texts_after(stamp):
        m = ORDER_WAIT_RE.search(text)
        if m:
            n = int(m.group(1))
            wait = n * {"second": 1, "minute": 60, "hour": 3600}[m.group(2).lower()]
            LAST_ASK[0] = time.time() - ORDER_ASK_EVERY_S + wait + 30
            break
    save_last_ask()
    return True


def trash_bag():
    for it in pack_items():
        if it.ItemID == TRASH_BAG_ID and "trash bag" in name_of(it).lower():
            return it
    return None


def prune_deeds(chest=None):
    """THE BEST ORDERS KEPT: of the orders carried, the DEEDS_KEPT Harry's visits would reach first are kept -- a full
    one, then one the pack can finish, then the most rough stone a nugget, then the fewest still wanted -- and the rest,
    worst first, go into the Trash Bag. With a working chest they go into it while it has room (`chest` open now), and
    wait in the pack for it between unloads; only what it has no room for is trashed."""
    deeds = order_deeds()
    kept = DEEDS_KEPT if handles_turnins() else 0    # ONE TURNS IN: a panner that does not keeps none
    if chest is not None:
        CHEST_ROOM_SEEN[0] = max(0, chest_room(chest))
        deeds = swap_with_chest(chest, deeds, kept)
    if len(deeds) <= kept:
        return
    if chest is None and working_chest_on():
        return                          # the chest takes them at the next unload
    bag = trash_bag()
    if bag is None:
        log("%d orders carried, more than the %d kept, and no Trash Bag in the pack to put the rest in." % (
            len(deeds), DEEDS_KEPT), HUE_BAD)
        return
    # THE TRASH GOES BY VALUE (owner, 10-15 12:5x: "do we ever trash one that might have been our best option
    # later?"): what to carry is judged by what the pack can finish now; what to throw away never is -- the nuggets on
    # hand change every trip. Kept first: a full order, then one with nuggets already in it, then the most rough stone
    # a nugget, then the fewest still wanted.
    ranked = sorted(deeds, reverse=True, key=lambda d: (
        d[1] >= d[2], d[1] > 0, stone_rate(d[3], d[2]), -(d[2] - d[1])))
    trashed = 0
    for d in reversed(ranked[DEEDS_KEPT:]):
        if d[1] > 0:
            continue                    # an order with nuggets in it is never thrown away (FILL IN THE FIELD)
        if d[0].Serial in START_PACK:
            continue                    # WHAT THE PLAYER BROUGHT: their own orders are worked, never thrown away
        Items.Move(d[0].Serial, bag.Serial, -1)
        Misc.Pause(700)
        trashed += 1
    if trashed:
        log("%d order(s) into the Trash Bag -- the least worth filling, past the %d kept." % (trashed, DEEDS_KEPT))


def swap_with_chest(chest, deeds, kept):
    """At the working chest: the `kept` best to carry (carry_rank) of the pack's orders and the chest's together come
    along, the rest of the pack's go in while it has room. The pack's orders after."""
    stored = order_deeds(chest) if kept else []
    stock = dict((t, count_tier(t)) for t in TIERS)
    for t, items in bank_goods(chest).items():
        stock[t] = stock.get(t, 0) + sum(int(it.Amount or 1) for it in items)
    carry = set(d[0].Serial for d in carry_rank(deeds + stored, stock)[:kept])
    taken = 0
    for d in stored:
        if d[0].Serial in carry:
            Items.Move(d[0].Serial, Player.Backpack.Serial, 1)
            Misc.Pause(700)
            taken += 1
    CHEST_ROOM_SEEN[0] += taken
    put = 0
    for d in [d for d in deeds if d[0].Serial not in carry][:max(0, CHEST_ROOM_SEEN[0])]:
        Items.Move(d[0].Serial, chest.Serial, -1)
        Misc.Pause(700)
        put += 1
    CHEST_ROOM_SEEN[0] -= put
    if taken or put:
        log("Orders carried: %d out of your working chest, %d into it -- %d carried." % (taken, put, kept))
    return order_deeds() if taken or put else deeds


CHECK_VALUE_RE = re.compile(r"value:?\s*([\d,]+)", re.I)


def pay_snapshot():
    """What a turn-in pays, as it stands in the pack: {check serial: gold}, and the rough stones carried."""
    checks, stones = {}, 0
    for it in pack_items():
        low = name_of(it).lower()
        if "rough stone" in low:
            stones += int(it.Amount or 1)
        elif "bank check" in low:
            try:
                Items.WaitForProps(it.Serial, 1500)
                m = CHECK_VALUE_RE.search(" | ".join(Items.GetPropStringList(it.Serial) or []))
                checks[it.Serial] = int(m.group(1).replace(",", "")) if m else 0
            except Exception:
                checks[it.Serial] = 0
    return checks, stones


NEW_FROM_HARRY_FILE = "NewFromHarry.txt"


def count_pay(before, pack_before=None):
    """THE PAY ON THE TRACKER: the gold of each new bank check and the rough stones gained since `before`. Anything else
    new in the pack since `pack_before` (a set of serials) is said and kept on file -- the Gold Panner storage key comes
    this way."""
    if pack_before is not None:
        for it in pack_items():
            low = name_of(it).lower()
            if it.Serial in pack_before or any(w in low for w in ("bank check", "rough stone", "panning order")):
                continue
            try:
                Items.WaitForProps(it.Serial, 1500)
                words = " | ".join(Items.GetPropStringList(it.Serial) or []) or name_of(it)
            except Exception:
                words = name_of(it)
            log("Harry gave something new: %s (0x%X, hue 0x%X)." % (words, it.ItemID, it.Hue))
            try:
                if ensure_data_dir():
                    with open(data_path(NEW_FROM_HARRY_FILE), "a") as f:
                        f.write("%s\t0x%X\t0x%X\t%s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), it.ItemID, it.Hue, words))
            except Exception:
                pass
    checks, stones = pay_snapshot()
    gold = sum(v for k, v in checks.items() if k not in before[0])
    rough = max(0, stones - before[1])
    TRACK["gold"] += gold
    TRACK["rough"] += rough
    return gold, rough


def reach_harry():
    """Beside Harry by the PO rune: his serial, or None."""
    rune = PO_RUNE[0]
    if rune is None:
        return None
    if recall_rune(rune) is not True:
        return None
    mobs = find_vendors(["gold panner", "harry johnson"], rng=12)
    if not mobs or not approach(mobs[0]):
        log("Harry is not beside your PO rune.", HUE_BAD)
        return None
    return mobs[0].Serial


def visit_harry():
    harry = reach_harry()
    if harry is None:
        return False
    doing("Filling orders at Harry")
    turned = 0
    asked = False
    if ask_due():
        asked = True
        ask_order(harry)
        Misc.Pause(1000)
    if not handles_turnins():
        return True                     # ONE TURNS IN: our order goes to the shared chest for the turn-in panner
    for _pass in range(20):
        deeds = order_deeds()
        if not deeds:
            if not asked:
                asked = True
                ask_order(harry)
                Misc.Pause(1000)
                continue
            break
        stock = dict((t, count_tier(t)) for t in TIERS)
        full = [d for d in deeds if d[1] >= d[2]]
        ready = full[:1] or [d for d in deeds if can_make(d[3], d[2] - d[1], stock)]
        if not ready:
            break
        deed, got, wanted, tier = max(ready, key=lambda d: (d[1] >= d[2], stone_rate(d[3], d[2]), -(d[2] - d[1])))
        for _round in range(6):
            if got >= wanted:
                break
            if trade_up(tier, wanted - got, harry) <= 0:
                break
            for st in goods().get(tier, []):
                clear_cursor()
                Items.UseItem(deed)
                if Target.WaitForTarget(2000, True):
                    Target.TargetExecute(st.Serial)
                Misc.Pause(1200)
            now = next((d for d in order_deeds() if d[0].Serial == deed.Serial), None)
            if now is None or now[1] <= got:
                got = now[1] if now else got
                break
            got = now[1]
        if got < wanted:
            log("An order stayed at %d / %d %s -- left as it is." % (got, wanted, tier), HUE_BAD)
            break
        paid_before = pay_snapshot()
        pack_before = set(it.Serial for it in pack_items())
        Items.Move(deed.Serial, harry, 1)
        Misc.Pause(2500)
        if any(it.Serial == deed.Serial for it in pack_items()):
            # HARRY WANDERS (10-15 12:28: the second full order of a visit stayed in the pack): beside him again, once
            near = find_vendors(["gold panner", "harry johnson"], rng=12)
            if near and approach(near[0]):
                harry = near[0].Serial
                Items.Move(deed.Serial, harry, 1)
                Misc.Pause(2500)
        if any(it.Serial == deed.Serial for it in pack_items()):
            log("Harry did not take a full order.", HUE_BAD)
            break
        turned += 1
        TRACK["orders"] += 1
        gold, rough = count_pay(paid_before, pack_before)
        log("Order turned in: %d %s -- paid %s gold and %d rough stone(s)." % (wanted, tier, "{:,}".format(gold),
                                                                            rough))
        ask_order(harry)
    if turned:
        log("%d order(s) turned in at Harry." % turned)
    prune_deeds()
    return True


# =============================================================================
# THE START SCREEN -- what was found, a few options, Start.
# =============================================================================

SETUP_GUMP_ID = 0x50414E31     # "PAN1"
BTN_CLOSE, BTN_START = 1, 2
CHECKS = (("orders", 103, "Fill Gold Panning Orders at Harry (needs your PO rune)"),
          ("mark_runes", 104, "Mark new runes where gold turns up"),
          ("avoid_invasions", 106, "Stay out of Town Invasions"))
GUMP_WAIT_MS = 24 * 60 * 60 * 1000


def status_rows():
    """[(ok, text)] -- what the script found."""
    rows = []
    towns = len(CITY_RUNES)
    own = len([r for r in OWN_RUNES if not is_po_rune(r)])
    rows.append((towns > 0, "Route: %d town rune(s) in %s%s" % (towns, " > ".join(CITY_FOLDER),
                                                               ", %d of your own" % own if own else "")
                 if towns else "Route: no %s folder in your Account Runebook" % " > ".join(CITY_FOLDER)))
    banks = sorted(base_name(n) for (k, n), ok in VENDORS.items() if k == "bank" and ok)
    if working_chest_on():
        rows.append((True, "Unloading: your working chest, by your Home rune"))
    else:
        rows.append((True, "Unloading: at the bank -- %s" % (", ".join(banks[:3]) if banks else
                                                             "found on the first trip")))
    have = pans_in_pack()
    if have:
        rows.append((True, "Gold Pan: %d carried" % have))
    elif tinker_kits() and ingots_on_hand() >= PAN_INGOTS:
        rows.append((True, "Gold Pan: made from your tinker's kit and %d iron ingots" % ingots_on_hand()))
    else:
        rows.append((True, "Gold Pan: none yet -- the first is made for you (a tinker sells the kit and ingots)"))
    po = PO_RUNE[0]
    rows.append((True, "Harry: your PO rune%s" % (" in %s" % " > ".join(po["path"]) if po and po["path"] else "")
                 if po else "Harry: no PO rune yet -- the first start walks to him from Minoc and marks one"))
    return rows


BTN_SETTINGS, BTN_BACK = 3, 4
BTN_RESCAN, BTN_SET_CHEST, BTN_USE_BANK = 5, 6, 7


def rescan():
    """Options' Rescan: the Account Runebook read again -- the route, Harry's rune, the Home rune."""
    log("Reading your Account Runebook...")
    load_route()
    PO_RUNE[0] = find_po_rune()
    HOME_RUNE[0] = find_home_rune()
    log("Home rune: %s; Harry's PO rune: %s." % ("found" if HOME_RUNE[0] else "none named Home",
                                                  "found" if PO_RUNE[0] else "none named PO"))


def set_working_chest():
    """Options' Set working chest: the player targets the chest; it is used instead of the bank while there is a Home
    rune to recall to."""
    log("Target your working chest.")
    try:
        serial = Target.PromptTarget("Target your working chest", HUE_GOOD)
    except TypeError:
        serial = Target.PromptTarget("Target your working chest")
    chest = Items.FindBySerial(serial) if serial and serial > 0 else None
    if chest is None or not chest.IsContainer:
        log("That is not a container -- no working chest set.", HUE_BAD)
        return
    SETTINGS["chest"] = "0x%X" % chest.Serial
    save_settings()
    chest_state_reset()
    register_chest(chest)
    if HOME_RUNE[0] is None:
        HOME_RUNE[0] = find_home_rune()
    if HOME_RUNE[0] is None:
        log("Working chest set -- but your Account Runebook has no rune named Home, so the bank is used until it does "
            "(mark one by the chest, then Rescan).", HUE_BAD)
    else:
        log("Working chest set: everything panned goes there instead of the bank.")


def send_screen(gd, width, height):
    Gumps.SendGump(SETUP_GUMP_ID, Player.Serial, 150, 150, gd.gumpDefinition, gd.gumpStrings)
    if not Gumps.WaitForGump(SETUP_GUMP_ID, GUMP_WAIT_MS):
        return None
    return Gumps.GetGumpData(SETUP_GUMP_ID)


# EVERY WINDOW FITS ITS TEXT (owner, 2026-10-16: "width should be based on the needs of the text. for all guis."): a
# window is as wide as its longest line, measured at the label font's width per character, and no wider.
TEXT_PX = 7                    # the label font, a character on average (44 characters filled 302 pixels)
EDGE_PX = 20                   # the margin right of the longest line
BUTTON_PX = 34                 # a button's art and the gap before its label
BUTTON_GAP_PX = 24             # between one button's label and the next button


def text_px(text):
    return len(text) * TEXT_PX


def button_row(gd, x, y, buttons):
    """Buttons side by side from `x`, each placed after the last one's label: [(button id, label, tooltip or None)].
    The x where the row ends."""
    for bid, label, tip in buttons:
        Gumps.AddButton(gd, x, y, 4005, 4007, bid, 1, 0)
        if tip:
            Gumps.AddTooltip(gd, tip)
        Gumps.AddLabel(gd, x + BUTTON_PX, y + 2, HUE_GOOD, label)
        x += BUTTON_PX + text_px(label) + BUTTON_GAP_PX
    return x - BUTTON_GAP_PX


def new_screen(width, height, title):
    gd = Gumps.CreateGump(movable=True)
    Gumps.AddPage(gd, 0)
    Gumps.AddBackground(gd, 0, 0, width, height, 30546)
    Gumps.AddAlphaRegion(gd, 0, 0, width, height)
    Gumps.AddLabel(gd, 20, 15, HUE_GOOD, title)
    return gd


def settings_screen():
    """The options, behind the start screen's Options button and the panning window's. Saved on every button."""
    while True:
        chest = chest_serial()
        mine = handles_turnins()
        title = "%s -- options" % SCRIPT_TITLE
        chest_text = "Working chest: %s" % ("set -- used instead of the bank" if chest else "none -- the bank is used")
        home_text = "Home rune: %s" % ("found" if HOME_RUNE[0] else "none named Home in your Account Runebook")
        turn_text = "Turn-ins at Harry: %s" % ("this panner" if mine else "another panner sharing the working chest")
        row = [(BTN_RESCAN, "Rescan", "Read your Account Runebook again (your Home and PO runes, your route)."),
               (BTN_SET_CHEST, "Set working chest",
                "Target a chest at home to unload into instead of the bank (needs a rune named Home).")]
        if chest:
            row.append((BTN_USE_BANK, "Use the bank", None))
        width = EDGE_PX + max([20 + text_px(t) for t in (title, chest_text, home_text)] +
                              [46 + text_px(c) for _k, _s, c in CHECKS] +
                              [20 + text_px(turn_text)] +
                              [20 + sum(BUTTON_PX + text_px(l) + BUTTON_GAP_PX for _b, l, _t in row) - BUTTON_GAP_PX])
        height = 60 + len(CHECKS) * 26 + 24 * 3 + 50 + 60
        gd = new_screen(width, height, title)
        y = 50
        for key, sid, caption in CHECKS:
            Gumps.AddCheck(gd, 20, y, 210, 211, opt(key), sid)
            Gumps.AddLabel(gd, 46, y, HUE_GOOD, caption)
            y += 26
        y += 6
        Gumps.AddLabel(gd, 20, y, HUE_GOOD, chest_text)
        y += 24
        Gumps.AddLabel(gd, 20, y, HUE_GOOD if HOME_RUNE[0] or not chest else HUE_BAD, home_text)
        y += 24
        Gumps.AddLabel(gd, 20, y, HUE_GOOD, turn_text)
        y += 34
        button_row(gd, 20, y, row)
        by = height - 38
        Gumps.AddButton(gd, 20, by, 4014, 4015, BTN_BACK, 1, 0)
        Gumps.AddLabel(gd, 54, by + 2, HUE_GOOD, "Back")
        resp = send_screen(gd, width, height)
        if resp is None:
            return
        switches = set(int(s) for s in (resp.switches or []))
        for key, sid, _c in CHECKS:
            SETTINGS[key] = "1" if sid in switches else "0"
        save_settings()
        if resp.buttonid == BTN_RESCAN:
            rescan()
        elif resp.buttonid == BTN_SET_CHEST:
            set_working_chest()
        elif resp.buttonid == BTN_USE_BANK:
            if working_chest_on() and turnin_panner() == my_id():
                set_turnin_panner("")    # another panner sharing it takes the turn-ins
            SETTINGS["chest"] = ""
            save_settings()
            chest_state_reset()
            log("No working chest -- the bank is used again.")
        else:
            return


def show_setup():
    """The start screen: what was found, Start, and Options. True when the player pressed Start."""
    while True:
        rows = status_rows()
        buttons = BUTTON_PX + text_px("Close") + BUTTON_GAP_PX + BUTTON_PX + text_px("Options") + BUTTON_GAP_PX + \
            BUTTON_PX + text_px("Start")
        width = EDGE_PX + max([20 + text_px(t) for _ok, t in rows] + [20 + text_px(SCRIPT_TITLE), 20 + buttons])
        height = 60 + len(rows) * 24 + 80
        gd = new_screen(width, height, SCRIPT_TITLE)
        y = 50
        for ok, text in rows:
            Gumps.AddLabel(gd, 20, y, HUE_GOOD if ok else HUE_BAD, text)
            y += 24
        by = height - 38
        Gumps.AddButton(gd, 20, by, 4014, 4015, BTN_CLOSE, 1, 0)
        Gumps.AddLabel(gd, 54, by + 2, HUE_GOOD, "Close")
        Gumps.AddButton(gd, width // 2 - 50, by, 4005, 4007, BTN_SETTINGS, 1, 0)
        Gumps.AddTooltip(gd, "Orders, buying, new runes, safety.")
        Gumps.AddLabel(gd, width // 2 - 16, by + 2, HUE_GOOD, "Options")
        Gumps.AddButton(gd, width - 110, by, 4005, 4007, BTN_START, 1, 0)
        Gumps.AddTooltip(gd, "Start panning.")
        Gumps.AddLabel(gd, width - 76, by + 2, HUE_GOOD, "Start")
        resp = send_screen(gd, width, height)
        if resp is None:
            return False
        if resp.buttonid == BTN_SETTINGS:
            settings_screen()
            continue
        if resp.buttonid != BTN_START:
            log("Closed.")
            return False
        problems = start_problems()
        if not problems:
            return True
        for p in problems:
            log(p, HUE_BAD)


# =============================================================================
# THE TRACKER -- what the panner is doing, this run's count, and Options.
# =============================================================================

TRACKER_GUMP_ID = 0x50414E32   # "PAN2"
TRACKER_SETTINGS_IDS = (11, 12)   # the Options button takes the other id after each press: the window's answer stays
                                  # the last button pressed, so only a press of the id it carries now is a new one
TRACKER_REDRAW_S = 2           # at most this often when something changed
TRACKER_RESEND_S = 60          # ... and this often when nothing did (a window closed by a right-click comes back)
OPTIONS_POLL_MS = 100          # a long wait asks the Options button this often (OPTIONS AT ONCE)
TRACK = {"now": "Starting", "t0": time.time(), "sifts": 0, "finds": 0, "orders": 0, "gold": 0, "rough": 0}
TRACKER = {"button": TRACKER_SETTINGS_IDS[0], "drawn": None, "at": 0.0, "size": None, "last": None}


def doing(text):
    """What the tracker shows the panner doing now."""
    TRACK["now"] = text
    tracker_draw()


NO_WATER = [0]                 # visits running that found no water to sift
STIFLED_RUNES = 3              # fewer usable runes than this: THE STIFLED PANNER
_runes_said = [0.0, None]


def runes_status():
    """THE STIFLED PANNER (owner, 10-15 10:4x: "Give an indicator in the status if the Panner is stifled from not enough
    safe runes available to find water from"): (usable, on the route, passed over, invaded now, another panner's,
    off the route for danger) -- read again at most every SHARED_READ_S."""
    if _runes_said[1] is not None and time.time() - _runes_said[0] < SHARED_READ_S:
        return _runes_said[1]
    rs = route()
    dead = [r for r in rs if rune_dead(r)]
    risky = [r for r in rs if not rune_dead(r) and rune_risky(r)]
    taken = [r for r in rs if not rune_dead(r) and not rune_risky(r) and rune_taken(r)]
    usable = len(rs) - len(dead) - len(risky) - len(taken)
    _runes_said[:] = [time.time(), (usable, len(rs), len(dead), len(risky), len(taken), len(BLACKLIST))]
    return _runes_said[1]


def tracker_rows():
    """[(text, hue)] -- the panning window's lines."""
    mins = int((time.time() - TRACK["t0"]) // 60)
    rows = [("Now: %s" % TRACK["now"], HUE_GOOD),
            ("This run: %s -- %d sift(s), %d find(s)" % (
                "%dh %02dm" % (mins // 60, mins % 60) if mins >= 60 else "%d min" % mins, TRACK["sifts"],
                TRACK["finds"]), HUE_GOOD)]
    if orders_on():
        rows.append(("Earned: %s gold, %d rough stone(s)" % ("{:,}".format(TRACK["gold"]), TRACK["rough"]), HUE_GOOD))
        if handles_turnins():
            rows.append(("Orders turned in at Harry: %d" % TRACK["orders"], HUE_GOOD))
        else:
            rows.append(("Orders: to the chest; another turns them in", HUE_GOOD))
    try:
        usable, total, dead, risky, taken, banned = runes_status()
        rows.append(("Runes: %d of %d usable" % (usable, total), HUE_GOOD if usable >= STIFLED_RUNES else HUE_BAD))
        why = [w for w in ("%d no finds" % dead if dead else "", "%d invaded" % risky if risky else "",
                           "%d another panner's" % taken if taken else "", "%d unsafe" % banned if banned else "")
               if w]
        if why:
            rows.append(("  " + ", ".join(why), HUE_GOOD if usable >= STIFLED_RUNES else HUE_BAD))
        if usable < STIFLED_RUNES:
            rows.append(("Stifled: too few safe runes with water", HUE_BAD))
        if NO_WATER[0] >= 3:
            rows.append(("Last %d visits found no water" % NO_WATER[0], HUE_BAD))
    except Exception:
        pass
    return rows


TRACKER_LINE_CHARS = 44        # a row longer than this goes on to the next line, never cut off


def tracker_wrap(rows):
    """A LONG ROW WRAPS (owner, 2026-10-16: "2 off for what?" -- the row was cut at "off for"): each row split at a
    space into lines that fit, the later lines indented."""
    out = []
    for text, hue in rows:
        lead = "    " if text.startswith("  ") else "  "
        while len(text) > TRACKER_LINE_CHARS:
            cut = text.rfind(" ", 0, TRACKER_LINE_CHARS + 1)
            if cut <= len(lead):
                cut = TRACKER_LINE_CHARS
            out.append((text[:cut].rstrip(), hue))
            text = lead + text[cut:].strip()
        out.append((text, hue))
    return out


def tracker_draw(force=False):
    rows = tracker_wrap(tracker_rows())
    key = (tuple(rows), TRACKER["button"])
    now = time.time()
    if not force and (now - TRACKER["at"] < (TRACKER_RESEND_S if key == TRACKER["drawn"] else TRACKER_REDRAW_S)):
        return
    TRACKER["drawn"], TRACKER["at"] = key, now
    height = 44 + len(rows) * 22 + 34
    width = EDGE_PX + max([14 + text_px(t) for t, _h in rows] + [14 + text_px(SCRIPT_TITLE),
                                                                  48 + text_px("Options")])
    try:
        gd = Gumps.CreateGump(movable=True)
        Gumps.AddPage(gd, 0)
        Gumps.AddBackground(gd, 0, 0, width, height, 30546)
        Gumps.AddAlphaRegion(gd, 0, 0, width, height)
        Gumps.AddLabel(gd, 14, 10, HUE_GOOD, SCRIPT_TITLE)
        y = 36
        for text, hue in rows:
            Gumps.AddLabel(gd, 14, y, hue, text)
            y += 22
        Gumps.AddButton(gd, 14, height - 30, 4005, 4007, TRACKER["button"], 1, 0)
        Gumps.AddTooltip(gd, "Orders, buying, new runes, safety.")
        Gumps.AddLabel(gd, 48, height - 28, HUE_GOOD, "Options")
        # THE CLICKABLE BOX IS THE FIRST ONE (2026-10-16, the owner: "this options button isn't working"): the client
        # keeps the clickable bounds a window had when it was first sent under its id -- a re-send redraws it but a
        # window grown since is dead below its old bottom edge, and Options sits at the bottom of a window that starts
        # at "Starting" and gains rows. Closed first when the size changes, it is built fresh -- and on this run's first
        # draw too: a window left up by the run before (a reload, a restart) kept that run's first box.
        if TRACKER["size"] != (width, height):
            Gumps.CloseGump(TRACKER_GUMP_ID)
        TRACKER["size"] = (width, height)
        Gumps.SendGump(TRACKER_GUMP_ID, Player.Serial, 60, 60, gd.gumpDefinition, gd.gumpStrings)
    except Exception:
        pass


def tracker_tick():
    """Between steps: the tracker brought up to date, and its Options button answered (panning waits while the
    options are open)."""
    if options_check():
        return
    tracker_draw()


def options_check():
    """The Options button answered now: True when it was pressed and the options were shown. The press is read as the
    Status Tracker reads its buttons -- WaitForGump on our own window, then its response, EDGE-TRIGGERED: the response
    latches, so only a CHANGE to one of our ids is a press, and the id the button carries flips with every press, so
    the next press differs again. OPTIONS AT ONCE (owner, 2026-10-16 00:2x: "it takes well over 5 seconds, but i'd
    expect to be instant"): asked from every wait -- a sift's, the wait for the next, the long ones -- not only between
    sifts (8 s apart)."""
    pressed = None
    try:
        if Gumps.WaitForGump(TRACKER_GUMP_ID, 1):
            r = Gumps.GetGumpData(TRACKER_GUMP_ID)
            pressed = getattr(r, "buttonid", None) if r is not None else None
    except Exception:
        pressed = None
    if pressed != TRACKER["last"]:
        TRACKER["last"] = pressed
    else:
        pressed = None
    if pressed not in TRACKER_SETTINGS_IDS:
        return False
    a, b = TRACKER_SETTINGS_IDS
    TRACKER["button"] = b if pressed == a else a
    was = TRACK["now"]
    TRACK["now"] = "Options open -- panning waits"
    tracker_draw(force=True)
    settings_screen()
    TRACK["now"] = was
    tracker_draw(force=True)
    return True


def pause(ms):
    """Misc.Pause that answers Options at once (options_check() every OPTIONS_POLL_MS)."""
    end = time.time() + ms / 1000.0
    while True:
        left = int((end - time.time()) * 1000)
        if left <= 0:
            return
        Misc.Pause(min(left, OPTIONS_POLL_MS))
        options_check()


def start_problems():
    out = []
    if not CITY_RUNES and not [r for r in OWN_RUNES if not is_po_rune(r)]:
        out.append("No runes to pan from: your Account Runebook has no %s folder (and no %s folder)." % (
            " > ".join(CITY_FOLDER), OWN_FOLDER))
    return out


# =============================================================================
# THE RUN
# =============================================================================

def orders_on():
    return opt("orders") and PO_RUNE[0] is not None


def trip():
    """The pack still full after FILL IN THE FIELD: FILL AT HARRY when that leaves it well under its setting, else (or
    still full after it) everything into the bank or the working chest; then pans. Turn-ins wait for the half hour --
    THE BULK TURN-IN."""
    if fill_at_harry_due():
        fill_at_harry()
    if pack_full() and not unload():
        return False
    keep_pans()
    if supplies_low():
        supply_run()
    return True


def wait_out_invasion():
    doing("Waiting out a Town Invasion")
    log("Every town on the route may be invaded now -- waiting at the bank.", HUE_BAD)
    unload()
    t0 = time.time()
    while time.time() - t0 < INVASION_AWAY_MAX_S + INVASION_BEFORE_S + 60:
        read_broadcasts()
        if not invasion_window():
            break
        pause(10000)


def run():
    load_settings()
    learn_load()                        # THE PAN LEARNS ITS WATER
    bow_start()                         # THE BOW IS THE PROOF
    prune_logs()
    load_rune_stats()
    load_blacklist()
    load_danger_spots()
    load_invaded()
    load_last_ask()
    load_vendors()
    JOURNAL_MARK[0] = newest_journal_timestamp()
    log("Reading your Account Runebook...")
    load_route()
    PO_RUNE[0] = PO_RUNE[0] or find_po_rune()
    if chest_serial() is not None:
        HOME_RUNE[0] = find_home_rune()
    else:
        adopt_shared_chest()            # THE PANNERS SHARE: a chest another panner set by our Home rune
    read_ethereal()                     # THE ETHEREAL'S BANK, known in advance
    if SETTINGS.get("eth_bank") == "1":
        log("Your Sosarian Ethereal opens the bank -- banking where we stand, no trip to a banker.")
    if opt("started") and not start_problems():
        log("Starting -- Options are on the panning window.")     # START ONCE: Start was pressed on an earlier run
    else:
        if not show_setup():
            return
        SETTINGS["started"] = "1"
        save_settings()
    tracker_draw(force=True)
    if opt("orders") and PO_RUNE[0] is None:
        walk_to_harry()                 # THE WALK TO HARRY
    START_PACK.clear()
    START_PACK.update(it.Serial for it in pack_items())
    brought_goods_said()                # WHAT THE PLAYER BROUGHT
    log("Panning %d town(s)%s." % (len(route()), "; Gold Panning Orders at Harry" if orders_on() else ""))
    if not keep_pans() and not (supplies_low() and supply_run()):
        log("No Gold Pan, and none could be made or bought -- stopping.", HUE_BAD)
        return
    if orders_on() and not order_deeds():
        log("No Gold Panning Order carried -- to Harry for one first.")
        visit_harry()
    index = 0
    fails = 0
    while True:
        tracker_tick()
        read_broadcasts()
        if ROUTE_STALE[0]:
            load_route()
        usable = route()
        if not usable:
            log("No runes to pan from -- stopping.", HUE_BAD)
            return
        if pack_full():
            if not trip():
                fails += 1
                if fails >= 3:
                    log("Three unloads in a row failed -- stopping so nothing is lost.", HUE_BAD)
                    return
                pause(5000)
                continue
            fails = 0
        if orders_on() and ask_due() and not trip_risky(PO_RUNE[0]):   # NO TRIP INTO THE HOUR: after it
            # THE BULK TURN-IN (owner, 10-15 13:0x: "wait 30 minutes from the last turn in, get order upon arrival, and
            # then do a bulk turn in"): a turn-in's ask starts Harry's half hour again, so turning in whenever an order
            # is ready gives the timed order away. Every half hour: the orders' nuggets out of the bank or the working
            # chest, then Harry -- the timed order first, then every order ready, the next asked after each
            if handles_turnins():
                unload(take_orders=True)
            visit_harry()
            if working_chest_on() or not pack_full():
                bank_checks()           # THE CHECKS BANKED AT ONCE
            if pack_full():
                unload()                # what Harry did not take goes back
            if ask_due():
                LAST_ASK[0] = time.time() - ORDER_ASK_EVERY_S + ORDER_ASK_RETRY_S
                save_last_ask()
        live = [r for r in usable if not rune_dead(r)] or usable
        order = live[index % len(live):] + live[:index % len(live)]
        rune = next((r for r in order if not rune_risky(r) and not rune_taken(r)), None)
        if rune is None:
            # THROUGH ANOTHER'S GROUND (owner, 2026-10-16 01:0x: "we should still be able to travel to the other panners
            # locations, we just have to expand further or in different locations to mark our own runes"): a rune in
            # another panner's reserve is still a way out -- we go there, sift nothing inside the reserve (pan_at_rune()),
            # and walk on or out past it to water of our own, marking our own rune there.
            rune = next((r for r in order if not rune_risky(r)), None)
        if rune is None:
            wait_out_invasion()
            continue
        index = live.index(rune) + 1
        doing("Going to %s" % base_name(rune["name"]))
        landed = recall_rune(rune)
        if landed is None:
            ROUTE_STALE[0] = True
            continue
        if not landed:
            Misc.Pause(1000)
            continue
        reason = pan_at_rune(rune)
        if reason == "full":
            trip()
            index -= 1                   # back to the same town
        elif reason == "nopan":
            if not (supplies_low() and supply_run()):
                log("No Gold Pan left, and none could be made or bought -- stopping.", HUE_BAD)
                return


run()
