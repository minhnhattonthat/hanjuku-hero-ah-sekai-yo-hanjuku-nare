"""Release gate + package: check -> build -> checksum -> smoke -> jpcheck -> BPS (re-applied, verified) -> zip.

    python -X utf8 tools/release.py [--version 1.0]
Writes release/hanjuku-hero-ah-sekai-yo-hanjuku-nare_en.zip (BPS + README.txt). Never publishes anything.
"""
import hashlib
import subprocess
import sys
import zipfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = Path(r"C:\Users\Nathan\.claude\plugins\marketplaces\retro-translation\skills\translate-retro-game\scripts")
SLUG = "hanjuku-hero-ah-sekai-yo-hanjuku-nare"
ORIG = ROOT / "rom" / "Hanjuku Hero - Ah, Sekai yo Hanjuku Nare...!! (Japan).sfc"
PY = [sys.executable, "-X", "utf8"]


def run(cmd, **kw):
    print(">", " ".join(str(c) for c in cmd))
    r = subprocess.run([str(c) for c in cmd], cwd=ROOT, **kw)
    if r.returncode:
        sys.exit(f"release gate failed: {cmd}")


def hashes(data):
    return (f"CRC32 {zlib.crc32(data):08x}", f"MD5 {hashlib.md5(data).hexdigest()}",
            f"SHA-1 {hashlib.sha1(data).hexdigest()}")


def main():
    ver = sys.argv[sys.argv.index("--version") + 1] if "--version" in sys.argv else "1.0"
    rel = ROOT / "release"
    rel.mkdir(exist_ok=True)
    built = ROOT / "build" / "release.sfc"
    run(PY + [ROOT / "tools" / "check.py"])
    run(PY + [ROOT / "build.py", "--out", built])
    run(PY + [SKILL / "bps.py", "snes-checksum", built])
    run(PY + [SKILL / "emu.py", built, "--out", ROOT / "work" / "qa" / "release_smoke", "--route",
              ROOT / "tools" / "routes" / "boot.txt", "--frames", "2400", "--smoke"])
    run(PY + [ROOT / "tools" / "jpcheck.py", built])
    bps = rel / f"Hanjuku_Hero_EN_v{ver}.bps"
    run(PY + [SKILL / "bps.py", "make", ORIG, built, bps])
    check = ROOT / "work" / "reapplied.sfc"
    run(PY + [SKILL / "bps.py", "apply", ORIG, bps, check])
    if check.read_bytes() != built.read_bytes():
        sys.exit("re-applied patch differs from the build")
    o, b = ORIG.read_bytes(), built.read_bytes()
    readme = (ROOT / "docs" / "README_release.txt").read_text(encoding="utf-8")
    readme = readme.replace("{VERSION}", ver).replace("{ORIG_HASHES}", "\n  ".join(hashes(o))) \
        .replace("{PATCHED_HASHES}", "\n  ".join(hashes(b)))
    zp = rel / f"{SLUG}_en.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(bps, bps.name)
        z.writestr("README.txt", readme.replace("\n", "\r\n"))
    print("wrote", zp, "patch sha1", hashlib.sha1(bps.read_bytes()).hexdigest(), "patched", hashes(b))


if __name__ == "__main__":
    main()
