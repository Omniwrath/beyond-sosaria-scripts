# Beyond Sosaria Scripts

Free, standalone RazorEnhanced scripts for the Beyond Sosaria shard, written for the TazUO client.

Each script is a single file: no other files to install, and no setup outside the game. Every script creates its own
data folder named after the file, so you can rename it if you like.

## Scripts

| Script | What it does |
|---|---|
| [Omni_Panning.py](Omni_Panning.py) | Pans for gold from town to town and along the shore, unloads at the bank or your own chest, and fills Harry Johnson's Gold Panning Orders. Several characters can run it together without fighting over the same water. See [Omni Panning](#omni-panning) below. |

What each script needs is written at the top of the file.

## Omni Panning

Press Start and it pans for gold, town after town, from the runes every Account Runebook comes with (Trammel > Cities).

### What it does

- **Finds its own water.** From each rune it looks for water nearby, then walks out along the shore (up to 150 tiles) to
  water nobody has panned. Emptied water rests 20 minutes. A rune that pays nothing three visits running is passed over.
- **Marks new runes** where it finds gold 20+ tiles from every rune you have, in a folder named Panning in your Account
  Runebook (made the first time).
- **Learns the water.** A kind of water the shard refuses three times is not tried again; the water that pays is tried
  first.
- **Keeps a Gold Pan.** With Tinkering it makes its own, buying Tinker's Tools and iron ingots from a tinker in town
  when it needs them.
- **Unloads** at a banker (it remembers which towns have one), through a Sosarian Ethereal with its bank unlocked, or
  into your own working chest at home. Everything panned goes: nuggets, bricks, rough stone, gems and anything else that
  came into the pack since it started -- never pans, kits, ingots, orders or gold. Bank checks go to the bank together,
  after the turn-ins.
- **Gold Panning Orders.** Nuggets stay in the pack. When it fills, they go into your carried orders where you stand;
  a pack still full goes to Harry, who trades nuggets up, takes every order the pack can finish (never a partial) and
  gives the next. Orders paying the most rough stone a nugget are filled first.
- **Rides long walks** on an ethereal mount statue from your pack, when the walk is over 40 tiles.
- **Stays safe.** Lost hits, poison, or a red or orange mobile nearby, and it leaves for the next rune; that spot goes
  on a list no panner walks near again. Town Invasions start every even hour (UTC) in Cove, Delucia, Jhelom, Minoc,
  Moonglow, Skara Brae, Umbra and Yew: from just before each start it keeps out of all eight and takes no trip that
  would land in one, until the shard names the town -- then it keeps out of that town until it is saved.
- **Plays well with others.** Several of your characters can run it from the same Scripts folder. Each keeps 40 tiles
  from the water another has panned in the last 3 hours, from its runes and from where it is working: the towns are
  shared, the shores are not. Characters whose Home runes stand by the same working chest share it, and one of them
  turns in the orders kept there.

### What you need

- The Account Runebook (`[ar`) your account started with. Its **Trammel > Cities** folder is the route.
- A Gold Pan in your backpack, or Tinkering to make one (the tinker takes the gold for tools and ingots from your pack
  or your bank).
- Mana to recall with.
- **For Gold Panning Orders:** a rune named **PO** beside Harry Johnson, the Gold Panner in Minoc, at the top of your
  Account Runebook or one folder down. If you don't have one, the first start recalls to the **Minoc** rune in
  Trammel > Cities, walks to Harry and marks it for you. **If your book no longer has that default Minoc rune, mark
  your own PO rune beside Harry.**
- Optional: a rune named **Home** beside a chest of yours, to unload there instead of the bank.
- Optional: a **Sosarian Ethereal** in your backpack with its bank unlocked -- the bank opens where you stand. The
  script reads the statue in your pack, so it learns this while you are not riding it.

### Mark your own runes

The town runes are the same for every player, so everyone running this script competes for the same easy water. **Mark
your own runes beside quiet, safe water** -- away from towns and monster spawns -- in a folder named **Panning** at the
top of your Account Runebook (make it yourself if the script has not made it yet). They join the route at the next
start, or at Options > Rescan, and keep you clear of the crowd. The town runes get you started; your own runes are
where the steady gold is.

### Using it

Press Play. A short screen shows what it found (your route, how it will unload, your Gold Pan, Harry's rune); press
**Start**. After that, the start screen is skipped: pressing Play starts panning. A small panning window shows
what it is doing now, this run's sifts and finds, what it has earned, your orders and how many runes are usable.

### Options

Open them from the start screen or the panning window's **Options** button. Every change is saved at once.

| Option | What it does |
|---|---|
| Fill Gold Panning Orders at Harry | On by default. Fills and turns in Harry's orders (needs the PO rune). Off: nuggets are unloaded with everything else. |
| Mark new runes where gold turns up | On by default. Marks a rune in your Panning folder where it finds gold far from your other runes. |
| Stay out of Town Invasions | On by default. Keeps out of the invasion towns around each invasion hour, as described above. |
| Set working chest | Target a chest at home. With a rune named Home in your book, everything panned goes there instead of the bank. |
| Use the bank | Shown while a working chest is set: forget the chest and use the bank again. |
| Rescan | Reads your Account Runebook again -- after you add, move or rename a rune. |

One setting is in the file only: how full the pack gets before it unloads. It is `pack_pct` in `Setup.txt`, in your
character's folder inside the script's data folder (`60` = 60% of your carrying weight, between 20 and 95).

### Its data folder

Next to the script, named after it (`Omni_Panning`). The files there are shared by every panner running from that
Scripts folder -- the towns' vendors, the runes' records, the unsafe spots, the working chests, who is panning where.
Each character has its own folder inside it for its settings and its daily log (`Log_YYYY_MM_DD.txt`, kept 14 days).
To give the passed-over runes another chance, delete `RuneStats.txt`; to let a rune that was taken off for danger back
on the route, delete its line in `Blacklist.txt`.

## Install

1. Download the script: open it above, then use **Download raw file**.
2. Put it in your RazorEnhanced `Scripts` folder.
3. In RazorEnhanced, add it to your script list and press Play. The first run shows a start screen; press Start.

## Update

Download the file again and replace the old one. Your settings live in the script's data folder, so they survive an
update. The [Releases](../../releases) page lists what changed in each version.

## Problems and ideas

Open an [issue](../../issues). Say which script, its version, what you expected and what happened, and copy the lines
it printed in your journal.

## License

GNU General Public License v3.0 -- see [LICENSE](LICENSE). You may share and change these scripts; a changed version you hand out must stay under the same license, with its source.
