from process_recipe.recipe import Recipe

def return_time_response(recipe: Recipe) -> str:
    step = recipe.current_step
    tinfo = getattr(step, "time", None) or {}
    def fmt(sec: int) -> str:
        m, s = divmod(int(sec), 60)
        h, m = divmod(m, 60)
        if h: 
            return f"{h} hr {m} min" if m else f"{h} hr"
        if m: 
            return f"{m} min"
        return f"{s} sec"
    answer = "I couldn't find an explicit time for this step."
    if tinfo:
        if tinfo.get("min_seconds") is not None and tinfo.get("max_seconds") is not None:
            if tinfo["min_seconds"] == tinfo["max_seconds"]:
                answer = f"This step takes about {fmt(tinfo['min_seconds'])}."
            else:
                answer = f"This step takes about {fmt(tinfo['min_seconds'])}–{fmt(tinfo['max_seconds'])}."
        elif tinfo.get("duration"):
            answer = f"This step takes {tinfo['duration']}."
        elif tinfo.get("qualitative"):
            answer = " / ".join(tinfo["qualitative"])
    
    return answer