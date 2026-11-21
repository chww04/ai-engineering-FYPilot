"""FYPilot real-data pilot pipeline (Week 4).

Builds the three real knowledge sources from files in data/raw_real/ and checks them:

  S01  FYP Handbook BAI 2026/2027 (PDF)       -> rules, timeline, integrity (FR5, RAI3)
  S02  Handbook Table 2.1 AI domains (PDF)    -> topic domains and example directions (FR1, FR3)
  S03  Four FAI department staff pages (HTML)
       + UTM Scholar researcher keywords (JSON) -> lecturer expertise (FR2, NFR3)

Real files stay in data/raw_real/ (gitignored). Only data/real_data_manifest.json
(checksums and counts) is committed.

Usage (from the repo root):
    python src/real_pilot_pipeline.py --fetch   # download staff pages + UTM Scholar list
    python src/real_pilot_pipeline.py           # prepare, validate, write manifest

The handbook PDF must be placed in data/raw_real/ by hand (it is a UTM internal document).
"""
import argparse
import hashlib
import html
import json
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path

RAW = Path("data/raw_real")
MANIFEST = Path("data/real_data_manifest.json")
HANDBOOK = "Handbook FYP BAI 20262027.pdf"
RETRIEVED = "2026-11-21"
DEPARTMENTS = {
    "II": ("Intelligence Informatics", "department-of-intelligence-informatics-2", "fai_intelligence_informatics"),
    "SEAT": ("Smart Engineering and Advanced Technology", "department-of-smart-engineering-and-advanced-technology", "fai_seat"),
    "BIHG": ("Business Intelligence, Humanities and Governance", "department-of-business-intelligent-humanities-and-governance", "fai_bihg"),
    "CAI": ("Creative Artificial Intelligence", "department-of-creative-artificial-intelligence", "fai_cai"),
}
SCHOLAR_API = "https://utmscholar.utm.my/api/researchers"
SCHOLAR_FILE = f"utmscholar_fai_{RETRIEVED}.json"
CHUNK_MAX = 800  # configuration C from Week 3


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_jsonl(path, rows):
    with open(path, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- fetch
def fetch():
    for code, (_, slug, stem) in DEPARTMENTS.items():
        url = f"https://fai.utm.my/{slug}/"
        out = RAW / f"{stem}_{RETRIEVED}.html"
        out.write_bytes(urllib.request.urlopen(url, timeout=60).read())
        print("saved", out)
    everyone, page = [], 1
    while True:
        d = json.load(urllib.request.urlopen(f"{SCHOLAR_API}?limit=500&page={page}", timeout=60))
        everyone += d["data"]
        if page >= d.get("totalPages", 1):
            break
        page += 1
    fai = [r for r in everyone if (r.get("faculty") or {}).get("name", "").upper() == "FACULTY OF ARTIFICIAL INTELLIGENCE"]
    (RAW / SCHOLAR_FILE).write_text(json.dumps(fai, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"saved {len(fai)} FAI researchers of {len(everyone)}")


# ---------------------------------------------------------------- S01 handbook
def chunk_text(text, maxc=CHUNK_MAX):
    paras = [p.strip() for p in re.split(r"\n\s*\n|(?<=[.:;])\n(?=[A-Z0-9])", text) if p.strip()]
    out, cur = [], ""
    for p in paras:
        if len(cur) + len(p) + 1 <= maxc:
            cur = (cur + "\n" + p).strip()
            continue
        if cur:
            out.append(cur)
        while len(p) > maxc:
            cut = p.rfind(". ", 0, maxc)
            cut = cut + 1 if cut > 200 else maxc
            out.append(p[:cut].strip())
            p = p[cut:].strip()
        cur = p
    if cur:
        out.append(cur)
    return out


def prepare_handbook():
    import pypdf
    path = RAW / HANDBOOK
    sha = sha256(path)
    pages = [(p.extract_text() or "") for p in pypdf.PdfReader(path).pages]
    rows, skipped, repeated, total_lines = [], [], 0, 0
    for n, raw in enumerate(pages, 1):
        lines = []
        for line in raw.split("\n"):
            line = re.sub(r"[ \t]+", " ", line).strip()
            if line:
                total_lines += 1
            if line and lines and line == lines[-1]:
                repeated += 1  # doubled text layer
                continue
            lines.append(line)
        text = "\n".join(lines)
        if len(text) < 100:
            skipped.append(n)  # figure or form page
            continue
        for j, ch in enumerate(chunk_text(text), 1):
            rows.append(dict(record_id=f"handbook_fyp_bai_2026-p{n:03d}-{j:02d}", text=ch, source=HANDBOOK,
                             source_type="guidelines", source_sha256=sha, page=n,
                             processing="pypdf; drop repeated lines; whitespace-normalised; paragraph-aware-char-800"))
    write_jsonl(RAW / "prepared_handbook_real.jsonl", rows)
    return rows, dict(pages=len(pages), skipped_pages=skipped, repeated_lines=repeated, total_lines=total_lines)


# ---------------------------------------------------------------- S02 Table 2.1
def prepare_domains():
    import pdfplumber
    path = RAW / HANDBOOK
    sha = sha256(path)

    def lines_of(words):
        rows = {}
        for w in words:
            rows.setdefault(round(w["top"] / 3), []).append(w)
        return [(min(w["top"] for w in rows[k]), " ".join(w["text"] for w in sorted(rows[k], key=lambda w: w["x0"])))
                for k in sorted(rows)]

    fix = lambda s: re.sub(r"(\w)- (\w)", r"\1-\2", re.sub(r"\s+", " ", s)).strip()
    out = []
    with pdfplumber.open(path) as pdf:
        for n in (26, 27, 28):  # Table 2.1 spans printed pages 20-22
            words = pdf.pages[n - 1].extract_words()
            y0 = [w for w in words if w["text"] == "Domain" and w["x0"] < 200][0]["top"] + 8
            stop = [w for w in words if w["text"] == "2.2.2"]
            y1 = stop[0]["top"] - 5 if stop else 770
            words = [w for w in words if y0 < w["top"] < y1]
            c1 = [w for w in words if w["x0"] < 180]
            c2 = [w for w in words if 180 <= w["x0"] < 355]
            c3 = [w for w in words if w["x0"] >= 355]
            starts = []
            for t, s in lines_of(c1):
                if not starts or t - starts[-1][1] > 22:
                    starts.append([t, t, s])
                else:
                    starts[-1][1], starts[-1][2] = t, starts[-1][2] + " " + s
            for i, (t, _, name) in enumerate(starts):
                top = y0 if i == 0 else t - 16
                bot = starts[i + 1][0] - 16 if i + 1 < len(starts) else y1
                cell = lambda c: " ".join(s for _, s in lines_of([w for w in c if top <= w["top"] < bot]))
                out.append(dict(domain=fix(name.replace("&", " & ")), topics=fix(cell(c2)), directions=fix(cell(c3)), page=n))
    rows = [dict(record_id=f"handbook_table21_domain-{i:02d}",
                 text=f"AI Domain: {d['domain']}\nIllustrative topics: {d['topics']}\nExample FYP directions: {d['directions']}\n"
                      f"Source: FYP Handbook BAI 2026/2027, Table 2.1",
                 source=HANDBOOK, source_type="ai_domains", source_sha256=sha, page=d["page"],
                 processing="pdfplumber word positions; column split by x; one domain per chunk")
            for i, d in enumerate(out, 1)]
    write_jsonl(RAW / "prepared_domains_real.jsonl", rows)
    return rows


# ---------------------------------------------------------------- S03 staff
SECTIONS = {"Head of Department", "Adjunct Professors", "Distinguised Adjunct Professors", "Distinguished Adjunct Professors",
            "Professors", "Associate Professors", "Senior Lecturers & Lecturers", "Senior Lecturers", "Lecturers",
            "Senior Fellow", "Senior Fellows"}
EXTERNAL = {"Adjunct Professors", "Distinguised Adjunct Professors", "Distinguished Adjunct Professors", "Senior Fellow", "Senior Fellows"}
TITLE = re.compile(r"(Assoc\.?\s*Prof|Prof|Dr\.|Ts\.|Ir\.|Sr\.|Datuk|Dato|Tan Sri)")
POSITION = re.compile(r"(Lecturer|Professor|Program|Coordinator|Director|Head|Dean|Manager|Senior|Associate|Deputy|Research|"
                      r"Principal|Coursework|Laboratory|Alumni|Facility|Information|Postgraduate|External|Project|Administrative|"
                      r"Universiti|Univeristi|UTM|Fellow|Rector|Executive|Advisor)")


def page_lines(path):
    s = Path(path).read_text(encoding="utf-8", errors="ignore")
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", s, flags=re.S)
    s = re.sub(r"<br\s*/?>|</(p|div|h\d|li|span)>", "\n", s)
    s = html.unescape(re.sub(r"<[^>]+>", "", s))
    return [l.strip() for l in s.split("\n") if l.strip()]


def parse_department(path):
    L = page_lines(path)
    first = next(k for k, l in enumerate(L) if l == "Expertise")
    heads = [k for k in range(first) if L[k] in SECTIONS]
    L = L[(max(heads) if heads else first):L.index("About Us", first)]
    category, people, i = "Head of Department", [], 0
    while i < len(L):
        line = L[i]
        if line in SECTIONS:
            category, i = line, i + 1
            continue
        if line != "Expertise":
            i += 1
            continue
        i += 1
        expertise = None
        if i < len(L) and not TITLE.match(L[i]) and L[i] not in SECTIONS:
            expertise, i = L[i], i + 1
        if i >= len(L) or L[i] in SECTIONS or L[i] == "Expertise":
            continue
        if expertise and re.search(r"\b(bin|binti|bt)$", expertise):  # name without a title, split over two lines
            name, expertise, i = expertise + " " + L[i], None, i + 1
        else:
            name, i = L[i], i + 1
        while (i < len(L) and L[i] != "Expertise" and L[i] not in SECTIONS and "[at]" not in L[i] and
               (re.match(r"(bin|binti|bt|@|a/p|a/l)\b", L[i]) or re.search(r"(Dr\.|binti|bin|bt\.?)$", name) or
                (re.fullmatch(r"[A-Z][a-z']+( [A-Z][a-z']+){0,3}", L[i]) and not POSITION.search(L[i])))):
            name, i = name + " " + L[i], i + 1
        position = []
        while i < len(L) and L[i] != "Expertise" and L[i] not in SECTIONS:
            if not ("[at]" in L[i] or L[i].startswith(("Phone", "Email", "[dot]", "Tel"))):  # drop contact details
                position.append(L[i])
            i += 1
        people.append(dict(name=name, category=category, position=" ".join(position), expertise=expertise))
    return people


def name_tokens(n):
    n = n.upper().replace("’", "'")
    n = re.sub(r"\b(ASSOC\.?|PROF\.?|EMERITUS|DATO'?|DATUK|DATIN|TAN SRI|IR\.|TS\.|DR\.|SR\.|CHM|HJH\.|PROF)\b", " ", n)
    n = re.sub(r"\b(BIN|BINTI|BT\.?|BTE|A/P|A/L)\b", " ", n)
    return {w for w in re.sub(r"[^A-Z ]", " ", n).split() if len(w) > 1}


def overlap(a, b):
    return len(a & b) / max(1, len(a | b))


def prepare_staff():
    scholar_path = RAW / SCHOLAR_FILE
    scholar = json.loads(scholar_path.read_text(encoding="utf-8"))
    scholar_sha = sha256(scholar_path)
    people, page_info = [], []
    for code, (dept, slug, stem) in DEPARTMENTS.items():
        f = RAW / f"{stem}_{RETRIEVED}.html"
        recs = parse_department(f)
        page_info.append(dict(dept=code, file=f.name, sha256=sha256(f), url=f"https://fai.utm.my/{slug}/", entries=len(recs)))
        for k, r in enumerate(recs, 1):
            people.append(dict(r, sid=f"FAI-{code}-{k:02d}", dept=code, file=f.name, file_sha=page_info[-1]["sha256"]))
    links = {}
    for s in scholar:
        st = name_tokens(s["name"])
        best = max(people, key=lambda p: overlap(name_tokens(p["name"]), st))
        if overlap(name_tokens(best["name"]), st) >= 0.6:
            links[best["sid"]] = s
    rows, counts = [], dict(entries=len(people), external=0, no_expertise=0, dept_only=0, scholar_only=0, both=0)
    for p in people:
        if p["category"] in EXTERNAL:
            counts["external"] += 1
            continue
        s = links.get(p["sid"])
        kws = list(dict.fromkeys(k.strip() for k in (s.get("keywords") or []) if k.strip() and not k.strip().isupper())) if s else []
        if not p["expertise"] and not kws:
            counts["no_expertise"] += 1
            continue
        counts["both" if p["expertise"] and kws else ("scholar_only" if kws else "dept_only")] += 1
        text = (f"Staff ID: {p['sid']}\nName: {p['name']}\nDepartment: {DEPARTMENTS[p['dept']][0]}\n"
                f"Position: {p['position'] or 'Not listed'}\n"
                f"Research areas (department page): {p['expertise'] or 'Not listed'}\n"
                f"Research keywords (UTM Scholar): {'; '.join(kws) if kws else 'Not listed'}")
        sources = [dict(source=p["file"], source_sha256=p["file_sha"])]
        if s:
            sources.append(dict(source=SCHOLAR_FILE, source_sha256=scholar_sha, scholar_link=s.get("link")))
        rows.append(dict(record_id=f"fai_staff_real-{p['dept'].lower()}-{int(p['sid'].split('-')[-1]):04d}", text=text,
                         sources=sources, source=p["file"], source_sha256=p["file_sha"], source_type="staff_profiles",
                         processing="html-to-text + UTM Scholar keywords merged by name; one lecturer per chunk; "
                                    "contact details removed; external staff excluded",
                         retrieved=RETRIEVED, page=None))
    write_jsonl(RAW / "prepared_staff_real.jsonl", rows)
    counts.update(scholar_fai_records=len(scholar), scholar_linked=len(links), scholar_unlinked=len(scholar) - len(links))
    return rows, counts, page_info, scholar_sha


# ---------------------------------------------------------------- validation
def validate(rows):
    hashes = {}

    def ok(src, digest):
        if src not in hashes:
            hashes[src] = sha256(RAW / src)
        return digest == hashes[src]

    v1 = sum(1 for r in rows if r.get("source") and all(ok(s["source"], s["source_sha256"]) for s in r.get("sources", [r])))
    staff = [r for r in rows if r["source_type"] == "staff_profiles"]
    v2 = sum(1 for r in staff if r["text"].count("Staff ID:") == 1)
    pdf = [r for r in rows if r["source"] == HANDBOOK]
    paged = sum(1 for r in pdf if r["page"])
    return dict(V1=f"{v1}/{len(rows)}", V2=f"{v2}/{len(staff)}", page_kept=f"{paged}/{len(pdf)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download department pages and UTM Scholar list first")
    args = ap.parse_args()
    if args.fetch:
        fetch()
    hb, hb_stats = prepare_handbook()
    dom = prepare_domains()
    staff, staff_stats, pages, scholar_sha = prepare_staff()
    checks = validate(hb + dom + staff)
    manifest = dict(
        pipeline_version="real-pilot-v2", generated=str(date.today()),
        note="Real data kept locally in data/raw_real/ (gitignored). This manifest holds checksums and counts only.",
        checks=checks,
        records=[
            dict(source_id="S01-real", source="FYP Handbook BAI 2026/2027 (PDF), FAI FYP Committee",
                 source_sha256=sha256(RAW / HANDBOOK), prepared_output="data/raw_real/prepared_handbook_real.jsonl",
                 prepared_sha256=sha256(RAW / "prepared_handbook_real.jsonl"), chunks=len(hb), **hb_stats,
                 access_rights="UTM internal handbook; not for public redistribution"),
            dict(source_id="S02-real", source="FYP Handbook BAI 2026/2027, Table 2.1 (AI domains, topics, example FYP directions)",
                 source_sha256=sha256(RAW / HANDBOOK), prepared_output="data/raw_real/prepared_domains_real.jsonl",
                 prepared_sha256=sha256(RAW / "prepared_domains_real.jsonl"), chunks=len(dom),
                 access_rights="UTM internal handbook; not for public redistribution"),
            dict(source_id="S03-real", source="Four FAI department staff pages + UTM Scholar researcher keywords",
                 department_pages=pages, utm_scholar=dict(file=SCHOLAR_FILE, sha256=scholar_sha, endpoint=SCHOLAR_API),
                 prepared_output="data/raw_real/prepared_staff_real.jsonl",
                 prepared_sha256=sha256(RAW / "prepared_staff_real.jsonl"), chunks=len(staff), **staff_stats,
                 access_rights="Public pages naming real staff; raw copies kept out of the public repo"),
        ])
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(checks), f"handbook={len(hb)} domains={len(dom)} staff={len(staff)}")
    return 0 if checks["V1"].split("/")[0] == checks["V1"].split("/")[1] else 1


if __name__ == "__main__":
    sys.exit(main())
