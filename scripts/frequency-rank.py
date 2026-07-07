"""
Ranks un-annotated roots by corpus frequency to target annotation batches
(issue #14, frequency-driven mode).

Each root is scored as the sum of corpus frequencies over all of its
surface forms in the generated search index, so verbs that mostly occur
affixed (melakukan, menjadi) attribute to their roots. Already-annotated
roots, pos:"proper"/"derived" roots (#62/#52 -- already covered via
another headword), and function words with no affix value are filtered
out.

The frequency list is data/frequency-id-50k.txt (see data/SOURCES.md for
origin and license). Run `npm run build:index` first so the index exists.

Usage:
    python scripts/frequency-rank.py [N]     # top N candidates, default 40
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

root_dir = Path(__file__).parent.parent

# Function words, pronouns, and particles: high-frequency but not
# productive affix targets. Extend as new ones surface in the ranking.
SKIP = set('''yang tidak ini itu dan dia akan apa kita untuk bisa tak mereka dengan anda saya
dari tapi sudah kamu jika hanya semua bukan bagaimana lagi jangan mana sini situ saja juga
ke di pada belum ya oh hei ah eh nya lah kah pun kami kalian aku kau begitu begini kenapa
mengapa siapa kapan sangat telah bahwa atau tetapi namun agar supaya karena sebab
demi tanpa antara dalam luar atas bawah depan belakang saat ketika selama hingga
sampai sejak kalau masih sedang seperti sesuatu beberapa semuanya ayo kan hal mau
bagi para oleh yaitu yakni sang si nan seseorang bahkan sebenarnya setiap ayolah
setelah halo hai seharusnya sebentar segala astaga kumohon daripada
kedua bajingan permisi nona bung sementara semacam brengsek
terhadap betapa saling meskipun kemarin nyonya kulihat inggris malah
jerman meski perancis kolonel got dewan semesta kok
bapa episode nasional berantakan pecundang nih bersulang kantin
aduh bangsat hong pingsan serikat sejujurnya gay ketat universitas
ilmuwan not peri barusan seperti sanggup mayor pemuda bencana
senator makasih nol jarang kaisar padahal oppa peristiwa
generasi apalagi sipil mahasiswa maya zona gubernur bong pas
misterius gurun senin ksatria hadirin divisi petani industri
internasional negro hamba berisik suster gang pejabat amin modern
nyenyak pirang rak dragon babak tong padang galaksi bijak
emosional lembah anti bersikeras marinir konferensi house
imbalan merunduk pertanda buronan dewi avatar perwira festival
ronde homo porno fajar berengsek fantastis tragedi krisis brilian
liga'''.split())


def main():
    top_n = int(sys.argv[1]) if len(sys.argv) > 1 else 40

    freq = {}
    with (root_dir / 'data' / 'frequency-id-50k.txt').open(encoding='utf-8') as f:
        for line in f:
            word, count = line.split()
            freq[word] = int(count)

    index = json.loads((root_dir / 'data' / 'search-index.json').read_text(encoding='utf-8'))
    words = {w['root']: w for w in json.loads((root_dir / 'data' / 'words.json').read_text(encoding='utf-8'))['words']}
    annotated = set(json.loads((root_dir / 'data' / 'annotations.json').read_text(encoding='utf-8')))

    score = defaultdict(int)
    forms = defaultdict(list)
    for form, root, *_ in index:
        count = freq.get(form)
        if count:
            score[root] += count
            forms[root].append((form, count))

    print(f'{"root":14}{"score":>10}  top forms')
    shown = 0
    for root, total in sorted(score.items(), key=lambda kv: -kv[1]):
        if root in annotated or root in SKIP or words.get(root, {}).get('pos') in ('proper', 'derived'):
            continue
        top = sorted(forms[root], key=lambda t: -t[1])[:4]
        print(f'{root:14}{total:>10}  ' + ', '.join(f'{f}({n})' for f, n in top))
        shown += 1
        if shown >= top_n:
            break


if __name__ == '__main__':
    main()
