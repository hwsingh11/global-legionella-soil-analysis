#!/usr/bin/env python3
import argparse, os, sys, subprocess, shlex, datetime

def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr); sys.exit(code)

def count_headers(path):
    n = 0
    with open(path, "r", newline="") as fh:
        for line in fh:
            if line.startswith(">"): n += 1
    return n

def run(cmd):
    print("+", " ".join(shlex.quote(x) for x in cmd), flush=True)
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(p.stdout, end="")
    if p.returncode != 0:
        die(f"command failed (exit {p.returncode}): {' '.join(cmd)}")

def main():
    ap = argparse.ArgumentParser(
        description="Exact-sequence overlap vs fixed search FASTA for each DB in a list (no UC output)."
    )
    ap.add_argument("--search", default="final_deblur_comb_derep_cluster99_remove_singletons_final_asvs.fasta",
                    help="Search (query) FASTA. Default: %(default)s")
    ap.add_argument("--list", default="db_list.txt",
                    help="Text file with one DB FASTA name per line. Default: %(default)s")
    ap.add_argument("--outdir", default="overlaps_finaldeblur",
                    help="Output directory. Default: %(default)s")
    ap.add_argument("--threads", type=int, default=os.cpu_count() or 4,
                    help="Threads for vsearch. Default: all CPUs")
    ap.add_argument("--strand", choices=["both","plus"], default="both",
                    help="Match reverse complements too (both) or only same strand (plus). Default: %(default)s")
    ap.add_argument("--mode", choices=["dbmatched","matched"], default="dbmatched",
                    help="Write DB headers (dbmatched) or SEARCH headers (matched). Default: %(default)s")
    ap.add_argument("--gzip", action="store_true",
                    help="Gzip-compress each output FASTA to save space.")
    args = ap.parse_args()

    # vsearch available?
    try:
        vver = subprocess.check_output(["vsearch","--version"], text=True).splitlines()[0]
        print(vver)
    except Exception:
        die("vsearch not found on PATH. Install with Homebrew: 'brew install vsearch' or conda.", 1)

    search = os.path.abspath(args.search)
    flist  = os.path.abspath(args.list)
    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)

    if not os.path.isfile(search) or os.path.getsize(search) == 0:
        die(f"search FASTA missing/empty: {search}")
    if not os.path.isfile(flist) or os.path.getsize(flist) == 0:
        die(f"list file missing/empty: {flist}")

    qn = count_headers(search)
    print(f"[env] time={datetime.datetime.now().isoformat(timespec='seconds')} threads={args.threads} strand={args.strand}")
    print(f"[search] {search} (nseq={qn})")
    print(f"[outdir] {outdir}\n")

    summary = os.path.join(outdir, "overlap_summary_vs_finaldeblur.tsv")
    with open(summary, "w") as sf:
        sf.write("db_path\tdb_basename\tquery_nseq\tdb_nseq\thits_unique\tmatched_fasta\n")

    with open(flist) as fh:
        for raw in fh:
            db = raw.strip()
            if not db or db.startswith("#"):  # skip blanks/comments
                continue
            db = os.path.abspath(db)
            if not os.path.isfile(db) or os.path.getsize(db) == 0:
                print(f"[skip] not found/empty: {db}")
                continue
            # avoid self-match
            try:
                if os.path.samefile(db, search):
                    print(f"[skip] DB equals SEARCH: {db}")
                    continue
            except FileNotFoundError:
                pass

            bname = os.path.basename(db)
            stem  = os.path.splitext(bname)[0]
            outpref = os.path.join(outdir, f"{stem}.overlap_vs_finaldeblur")
            if args.mode == "dbmatched":
                out_fa = f"{outpref}.dbmatched.fasta"
                out_flag = "--dbmatched"
            else:
                out_fa = f"{outpref}.matched.fasta"
                out_flag = "--matched"

            ndb = count_headers(db)
            print(f"[run] {bname}: db_nseq={ndb} → {os.path.basename(out_fa)}")

            cmd = [
                "vsearch", "--search_exact", search,
                "--db", db,
                "--strand", args.strand,
                "--threads", str(args.threads),
                out_flag, out_fa
            ]
            run(cmd)

            hits = count_headers(out_fa) if os.path.exists(out_fa) else 0

            if args.gzip and os.path.exists(out_fa):
                run(["gzip", "-f", out_fa])  # produces out_fa + ".gz"
                out_fa = out_fa + ".gz"

            with open(summary, "a") as sf:
                sf.write("\t".join([db, bname, str(qn), str(ndb), str(hits), out_fa]) + "\n")

    print(f"\n[done] summary -> {summary}")

if __name__ == "__main__":
    main()

