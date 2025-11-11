import re
from typing import Dict, List, Optional, Tuple, Any

# -----------------------------
# Time patterns
# -----------------------------
VULGAR_MAP = {
    '½': '1/2', '⅓': '1/3', '¼': '1/4', '¾': '3/4', '⅔': '2/3',
    '⅛': '1/8', '⅜': '3/8', '⅝': '5/8', '⅞': '7/8'
}

def _normalize_frac(s: str) -> str:
    for k,v in VULGAR_MAP.items():
        s = s.replace(k, v)
    return s

def _to_float(num: str) -> Optional[float]:
    num = num.strip()
    num = _normalize_frac(num)
    try:
        if ' ' in num and '/' in num:  # "1 1/2"
            a,b = num.split(' ',1)
            n,d = b.split('/',1)
            return float(a) + float(n)/float(d)
        if '/' in num:  # "1/2"
            n,d = num.split('/',1)
            return float(n)/float(d)
        return float(num)
    except Exception:
        return None

RE_RANGE = re.compile(
    r'(?P<a>\d+)\s*(?:-|to|–|—)\s*(?P<b>\d+)\s*(?P<u>hours?|hrs?|hr|h|minutes?|mins?|min|m|seconds?|secs?|sec|s)\b',
    re.I
)
RE_COMBO = re.compile(
    r'(?P<h>\d+(?:\s+\d+/\d+|/\d+|[½⅓¼¾⅔⅛⅜⅝⅞])?)\s*(?:hours?|hrs?|hr|h)\s*(?:and|,)?\s*'
    r'(?P<m>\d+(?:\s+\d+/\d+|/\d+|[½⅓¼¾⅔⅛⅜⅝⅞])?)\s*(?:minutes?|mins?|min|m)\b',
    re.I
)
RE_HOURS = re.compile(r'(?P<h>\d+(?:\s+\d+/\d+|/\d+|[½⅓¼¾⅔⅛⅜⅝⅞])?)\s*(hours?|hrs?|hr|h)\b', re.I)
RE_MIN   = re.compile(r'(?P<m>\d+(?:\s+\d+/\d+|/\d+|[½⅓¼¾⅔⅛⅜⅝⅞])?)\s*(minutes?|mins?|min|m)\b', re.I)
RE_SEC   = re.compile(r'(?P<s>\d+(?:\s+\d+/\d+|/\d+|[½⅓¼¾⅔⅛⅜⅝⅞])?)\s*(seconds?|secs?|sec|s)\b', re.I)
RE_PER_SIDE = re.compile(r'\bper\s+side\b', re.I)
RE_AT_LEAST = re.compile(r'\b(at\s+least|minimum(?: of)?)\b', re.I)
RE_AT_MOST  = re.compile(r'\b(at\s+most|no\s+more\s+than|maximum(?: of)?)\b', re.I)
RE_APPROX   = re.compile(r'\b(about|around|approximately|approx\.?)\b', re.I)
DONE_CUES   = re.compile(r'\buntil\b[^.]+', re.I)  # grab "until ..." clause loosely

def _unit_to_minutes(u: str) -> float:
    u = u.lower()
    if u.startswith('h'): return 60.0
    if u.startswith('m'): return 1.0
    if u.startswith('s'): return 1/60.0
    return 1.0

def extract_time_info(text: str) -> Dict[str, Any]:
    """Return a dict ready to be attached to step['time']"""
    info: Dict[str, Any] = {"mentions": []}
    tmin: Optional[float] = None
    tmax: Optional[float] = None

    # Range like 20-25 minutes
    for m in RE_RANGE.finditer(text):
        a,b,u = int(m.group('a')), int(m.group('b')), m.group('u')
        mult = _unit_to_minutes(u)
        mn, mx = a*mult, b*mult
        info["mentions"].append({
            "text": m.group(0), "min_s": int(mn*60), "max_s": int(mx*60),
            "approx": False, "per_side": bool(RE_PER_SIDE.search(text)),
            "at_least": False, "at_most": False
        })
        tmin = mn if tmin is None else min(tmin, mn)
        tmax = mx if tmax is None else max(tmax, mx)

    # Combo like 1 hr 30 min
    for m in RE_COMBO.finditer(text):
        h = _to_float(m.group('h')) or 0.0
        mn = _to_float(m.group('m')) or 0.0
        minutes = h*60 + mn
        info["mentions"].append({
            "text": m.group(0), "min_s": int(minutes*60), "max_s": int(minutes*60),
            "approx": False, "per_side": bool(RE_PER_SIDE.search(text)),
            "at_least": False, "at_most": False
        })
        tmin = minutes if tmin is None else min(tmin, minutes)
        tmax = minutes if tmax is None else max(tmax, minutes)

    # Standalone units
    for m in RE_HOURS.finditer(text):
        h = _to_float(m.group('h')) or 0.0
        minutes = h*60
        approx = bool(RE_APPROX.search(text))
        at_least = bool(RE_AT_LEAST.search(text))
        at_most = bool(RE_AT_MOST.search(text))
        info["mentions"].append({
            "text": m.group(0), "min_s": int(minutes*60), "max_s": int(minutes*60),
            "approx": approx, "per_side": bool(RE_PER_SIDE.search(text)),
            "at_least": at_least, "at_most": at_most
        })
        tmin = minutes if tmin is None else min(tmin, minutes)
        tmax = minutes if tmax is None else max(tmax, minutes)

    for m in RE_MIN.finditer(text):
        mm = _to_float(m.group('m')) or 0.0
        approx = bool(RE_APPROX.search(text))
        at_least = bool(RE_AT_LEAST.search(text))
        at_most = bool(RE_AT_MOST.search(text))
        info["mentions"].append({
            "text": m.group(0), "min_s": int(mm*60), "max_s": int(mm*60),
            "approx": approx, "per_side": bool(RE_PER_SIDE.search(text)),
            "at_least": at_least, "at_most": at_most
        })
        tmin = mm if tmin is None else min(tmin, mm)
        tmax = mm if tmax is None else max(tmax, mm)

    for m in RE_SEC.finditer(text):
        ss = _to_float(m.group('s')) or 0.0
        approx = bool(RE_APPROX.search(text))
        at_least = bool(RE_AT_LEAST.search(text))
        at_most = bool(RE_AT_MOST.search(text))
        info["mentions"].append({
            "text": m.group(0), "min_s": int(ss), "max_s": int(ss),
            "approx": approx, "per_side": bool(RE_PER_SIDE.search(text)),
            "at_least": at_least, "at_most": at_most
        })
        # seconds are tiny; we keep aggregate in minutes
        mn = ss/60.0
        tmin = mn if tmin is None else min(tmin, mn)
        tmax = mn if tmax is None else max(tmax, mn)

    # qualitative done cues
    quals = []
    for m in DONE_CUES.finditer(text):
        quals.append(m.group(0).strip())
    if quals:
        info["qualitative"] = quals

    # overall numbers
    if tmin is not None:
        info["min_seconds"] = int(tmin*60)
    if tmax is not None:
        info["max_seconds"] = int(tmax*60)

    # convenience string for UI
    def _fmt(sec: int) -> str:
        m, s = divmod(int(sec), 60)
        h, m = divmod(m, 60)
        if h: return f"{h} hr {m} min" if m else f"{h} hr"
        if m: return f"{m} min"
        return f"{s} sec"
    if "min_seconds" in info and "max_seconds" in info:
        if info["min_seconds"] == info["max_seconds"]:
            info["duration"] = _fmt(info["min_seconds"])
        else:
            info["duration"] = f"{_fmt(info['min_seconds'])}–{_fmt(info['max_seconds'])}"
    elif quals:
        info["duration"] = quals[0]

    return info

# -----------------------------
# Temperature patterns
# -----------------------------
RE_F = re.compile(r'(?P<v>\d{2,3})\s*°?\s*(?:degrees?\s*)?F\b', re.I)
RE_C = re.compile(r'(?P<v>\d{2,3})\s*°?\s*(?:degrees?\s*)?C\b', re.I)
RE_BOTH = re.compile(r'(?P<f>\d{2,3})\s*°?\s*(?:degrees?\s*)?F\s*\(\s*(?P<c>\d{2,3})\s*°?\s*C\s*\)', re.I)
RE_STOVE = re.compile(r'\b(low|medium|high|medium-low|medium-high)\s+heat\b', re.I)
RE_PREHEAT = re.compile(r'\b(preheat|heat)\s+(the\s+)?oven\s+(to|at)\b', re.I)

def extract_temperature_info(text: str, context: Optional[Dict[str, Any]] = None) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """Return (temperature_dict, context_update)"""
    context = context or {}
    t: Dict[str, Any] = {"mentions": []}
    ctx_upd: Dict[str, Any] = {}

    both = RE_BOTH.search(text)
    if both:
        f = int(both.group('f')); c = int(both.group('c'))
        t["mentions"].append({"text": both.group(0), "value": f, "unit": "F", "device": "oven"})
        t["mentions"].append({"text": both.group(0), "value": c, "unit": "C", "device": "oven"})
        t["oven"] = f" {f} F".strip()
        ctx_upd["oven"] = {"F": f, "C": c}
        ctx_upd["preheated"] = bool(RE_PREHEAT.search(text))
    else:
        mf = RE_F.search(text)
        mc = RE_C.search(text)
        if mf:
            val = int(mf.group('v'))
            t["mentions"].append({"text": mf.group(0), "value": val, "unit": "F", "device": "oven"})
            t["oven"] = f"{val} F"
            ctx_upd["oven"] = {"F": val}
            ctx_upd["preheated"] = bool(RE_PREHEAT.search(text))
        if mc:
            val = int(mc.group('v'))
            t["mentions"].append({"text": mc.group(0), "value": val, "unit": "C", "device": "oven"})
            # Don't overwrite 'oven' string if F already set
            if "oven" not in t:
                t["oven"] = f"{val} C"
            ctx_upd.setdefault("oven", {})
            ctx_upd["oven"]["C"] = val
            ctx_upd["preheated"] = bool(RE_PREHEAT.search(text))

    ms = RE_STOVE.search(text)
    if ms:
        qual = ms.group(1).lower()
        t["mentions"].append({"text": ms.group(0), "qualitative": f"{qual} heat", "device": "stovetop"})
        t["stovetop"] = f"{qual} heat"

    # If baking verbs but no explicit temp, try to fill from context
    if re.search(r'\b(bake|roast|broil)\b', text, re.I) and "oven" in context and "oven" not in t:
        ov = context["oven"]
        if "F" in ov:
            t["oven"] = f"{ov['F']} F"
            t["mentions"].append({"text": "(from context)", "value": ov["F"], "unit": "F", "device": "oven"})
        elif "C" in ov:
            t["oven"] = f"{ov['C']} C"
            t["mentions"].append({"text": "(from context)", "value": ov["C"], "unit": "C", "device": "oven"})

    # Clean if nothing found
    if not t.get("mentions"):
        t = {}

    return t, ctx_upd
