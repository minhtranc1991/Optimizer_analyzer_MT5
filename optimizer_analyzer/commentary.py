"""Plain-language (Vietnamese) comments generated from the analysis result.

Every function returns an HTML fragment. Notes are rules over the data, not
model output: each states the number it is based on.
"""
import pandas as pd

from .config import Config

FIGURE_HELP = {
    "fwd_back": (
        "Mỗi chấm là một bộ tham số. Trục X = kết quả Back, trục Y = kết quả Forward. "
        "Chấm càng sát đường chéo thì hai kỳ càng giống nhau (ổn định). "
        "Xanh = Stable (qua bộ lọc), đỏ = Elite (Forward và Back cùng vượt ngưỡng), xám = còn lại. "
        "Rê chuột để xem tham số của từng điểm."
    ),
    "importance": (
        "Độ ảnh hưởng của từng tham số tới lợi nhuận (Forward) và tới độ nhất quán, "
        "tính bằng RandomForest trên toàn bộ dữ liệu. Tham số có dấu * được chọn để tối ưu; "
        "tham số còn lại ít ảnh hưởng nên có thể cố định."
    ),
    "pair": (
        "Bản đồ điểm số (FinalScore) theo hai tham số quan trọng nhất. Màu sáng = điểm cao. "
        "Khung đỏ là vùng khuyến nghị cho hai tham số này. Vùng tốt là một mảng sáng liền nhau "
        "(plateau), không phải một chấm sáng đơn lẻ."
    ),
    "profiles": (
        "FinalScore theo giá trị của từng tham số được chọn. Vùng đỏ = range khuyến nghị, "
        "vạch đứt = giá trị trung tâm. Đường xu hướng đi lên/xuống cho biết nên tăng hay giảm tham số; "
        "chấm tụ thành dải cao là vùng ổn định."
    ),
    "box": (
        "Phân bố Forward Result của các set Stable trong mỗi cluster. Hộp thấp và hẹp = ổn định "
        "nhưng lợi nhuận thấp; hộp cao và rộng = lợi nhuận cao nhưng biến động."
    ),
    "parallel": (
        "Mỗi đường là một set Stable đi qua giá trị các tham số rồi tới kết quả. "
        "Kéo chọn một đoạn trên trục để lọc. Các đường cùng màu (cùng cluster) tụ lại ở tham số nào "
        "thì tham số đó quyết định cluster."
    ),
}


def _box(title, body, kind="note"):
    return f"<div class='{kind}'><b>{title}</b>{body}</div>"


def _ul(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def _fmt(x, d=2):
    return f"{x:,.{d}f}"


def _edges(p, low, high, lo, hi, step):
    """('lower'/'upper') when the range touches an edge of the tested domain
    that is NOT a hard limit of the parameter."""
    hard_lo, hard_hi = Config.PARAM_BOUNDS.get(p, (None, None))
    out = []
    if low <= lo + step and high < hi and not (hard_lo is not None and lo <= hard_lo):
        out.append("lower")
    if high >= hi - step and low > lo and not (hard_hi is not None and hi >= hard_hi):
        out.append("upper")
    return out


def _best(r):
    best = r["summary"].iloc[0]
    sub = r["stable"][r["stable"]["Cluster"] == int(best["Cluster"])]
    return best, sub


# ---------------------------------------------------------------- summary

def summary_html(r):
    full, stable, elite = r["full"], r["stable"], r["elite"]
    best, sub = _best(r)
    cutoff = full["FinalScore"].quantile(1 - Config.TOP_PERCENT)
    n_top = int((full["FinalScore"] >= cutoff).sum())
    steps = [
        f"Dữ liệu gốc: <b>{r['n_raw']:,}</b> bộ tham số",
        f"Sau pre-filter (Trades ≥ {Config.MIN_TRADES}): <b>{len(full):,}</b>",
        f"Top {int(Config.TOP_PERCENT * 100)}% theo FinalScore: <b>{n_top:,}</b>",
        f"Stable (gap tương đối ≤ phân vị {int(Config.RELATIVE_GAP_PERCENTILE * 100)}% + Elite): "
        f"<b>{len(stable):,}</b>",
        f"Elite (Forward > {Config.ELITE_MIN_FORWARD} và Back > {Config.ELITE_MIN_BACK}): "
        f"<b>{len(elite):,}</b>",
    ]
    notes = []
    if len(stable) and len(elite) / len(stable) > 0.8:
        notes.append(
            f"Elite chiếm {len(elite) / len(stable):.0%} số set Stable, nên danh sách Elite "
            f"không còn phân biệt được set tốt. Ngưỡng {Config.ELITE_MIN_FORWARD} có lẽ quá thấp "
            "cho file này; nên nâng ELITE_MIN_FORWARD/ELITE_MIN_BACK trong config.py."
        )
    if len(full) < r["n_raw"]:
        notes.append(f"Pre-filter đã loại {r['n_raw'] - len(full):,} set ít lệnh.")
    if not best["Eligible"]:
        notes.append("Không có cluster nào đủ lớn; khuyến nghị có độ tin cậy thấp.")
    rec = (
        f"Cluster <b>{int(best['Cluster'])}</b> ({int(best['Count'])} set): "
        f"Forward trung vị <b>{_fmt(best['ForwardMedian'])}</b>, Back trung vị "
        f"<b>{_fmt(best['BackMedian'])}</b>, Consistency <b>{_fmt(best['Consistency'], 3)}</b>, "
        f"điểm xung quanh (neighbour) <b>{_fmt(best['NeighbourScore'], 3)}</b>."
    )
    return (
        "<h2>1. Tóm tắt</h2>"
        + _box("Từ dữ liệu đến khuyến nghị", _ul(steps))
        + _box("Kết quả khuyến nghị", f"<p>{rec}</p>", "good")
        + (_box("Lưu ý", _ul(notes), "warn") if notes else "")
    )


# ------------------------------------------------------ parameter choice

def parameters_html(r):
    p, c = r["profit_importance"], r["consistency_importance"]
    m = p.merge(c, on="Parameter", suffixes=("_Profit", "_Consistency"))
    m["Score"] = (m["Importance_Profit"] + m["Importance_Consistency"]) / 2
    m = m.sort_values("Score", ascending=False).reset_index(drop=True)
    total = m["Score"].sum()
    m["Share"] = m["Score"] / total
    m["Cum"] = m["Share"].cumsum()
    best, sub = _best(r)
    selected = set(r["parameters"])

    rows = []
    for _, x in m.iterrows():
        name = x["Parameter"]
        if name in selected:
            if x["Importance_Profit"] >= 2 * x["Importance_Consistency"]:
                why = "Chủ yếu ảnh hưởng tới lợi nhuận."
            elif x["Importance_Consistency"] >= 2 * x["Importance_Profit"]:
                why = "Chủ yếu ảnh hưởng tới độ nhất quán Forward/Back."
            else:
                why = "Ảnh hưởng cả lợi nhuận và độ nhất quán."
            action = f"<b>Tối ưu</b>. {why}"
        else:
            action = (f"<b>Cố định</b> ở {sub[name].median():g} "
                      "(trung vị của cluster khuyến nghị). Ảnh hưởng thấp, không đáng tốn thời gian tối ưu.")
        rows.append({
            "Tham số": name,
            "Importance (lợi nhuận)": _fmt(x["Importance_Profit"], 3),
            "Importance (nhất quán)": _fmt(x["Importance_Consistency"], 3),
            "Tỷ trọng": f"{x['Share']:.1%}",
            "Tích lũy": f"{x['Cum']:.1%}",
            "Quyết định": action,
        })
    table = pd.DataFrame(rows).to_html(index=False, escape=False, classes="t")

    n_dropped = len(m) - len(selected)
    mode_text = {
        "cumulative": f"giữ tham số cho tới khi tích lũy ≥ {Config.SELECT_CUMULATIVE:.0%} tổng importance",
        "median": "giữ tham số có điểm ≥ trung vị",
        "relative": f"giữ tham số có điểm ≥ {Config.SELECT_RELATIVE:.0%} điểm cao nhất",
        "top_n": f"giữ {Config.SELECT_TOP_N} tham số đầu",
        "all": "giữ tất cả",
    }[Config.SELECT_MODE]
    notes = [
        f"Chế độ chọn: <b>{Config.SELECT_MODE}</b> ({mode_text}); luôn giữ tối thiểu {Config.SELECT_MIN}.",
        f"Chọn <b>{len(selected)}</b>/{len(m)} tham số, cố định {n_dropped}.",
    ]
    top2 = m.head(2)["Share"].sum()
    if top2 > 0.4:
        notes.append(
            f"Hai tham số đầu ({', '.join(m.head(2)['Parameter'])}) chiếm {top2:.0%} importance: "
            "tối ưu hai tham số này trước, các tham số còn lại chỉ tinh chỉnh."
        )
    flat = m[m["Share"] < 1 / (2 * len(m))]
    if len(flat):
        notes.append("Ảnh hưởng gần như bằng 0: " + ", ".join(flat["Parameter"]) + ".")
    notes.append("Nếu muốn tối ưu nhiều hơn/ít hơn, đổi SELECT_MODE hoặc SELECT_CUMULATIVE trong config.py.")
    return "<h2>2. Chọn bộ tham số</h2>" + _box("Cách chọn", _ul(notes)) + table


# --------------------------------------------------------- figure notes

def fwd_back_note(r):
    df, stable, elite = r["full"], r["stable"], r["elite"]
    above = (df["Forward Result"] > df["Back Result"]).mean()
    corr = df["Forward Result"].corr(df["Back Result"])
    med_gap = stable["RelativeGap"].median()
    items = [
        f"Tương quan Forward–Back toàn bộ dữ liệu: <b>{corr:.2f}</b> "
        + ("(cao: kết quả Back dự báo được Forward)." if corr > 0.7 else
           "(thấp: Back ít dự báo được Forward, tham số dễ overfit)." if corr < 0.3 else "(trung bình)."),
        f"<b>{above:.0%}</b> số set có Forward > Back (nằm trên đường chéo).",
        f"Gap tương đối trung vị của set Stable: <b>{med_gap:.2f}</b> "
        f"({'tốt' if med_gap < 0.15 else 'chấp nhận được' if med_gap < 0.3 else 'cao'}).",
    ]
    return _box("Nhận xét", _ul(items))


def importance_note(r):
    p, c = r["profit_importance"], r["consistency_importance"]
    items = [
        f"Ảnh hưởng lợi nhuận nhiều nhất: <b>{p.iloc[0]['Parameter']}</b> ({p.iloc[0]['Importance']:.1%}).",
        f"Ảnh hưởng nhất quán nhiều nhất: <b>{c.iloc[0]['Parameter']}</b> ({c.iloc[0]['Importance']:.1%}).",
    ]
    only_cons = set(c.head(3)["Parameter"]) - set(p.head(3)["Parameter"])
    if only_cons:
        items.append("Tham số quyết định độ ổn định chứ không phải lợi nhuận: "
                     + ", ".join(sorted(only_cons)) + ".")
    return _box("Nhận xét", _ul(items))


def pair_note(r):
    a, b = r["parameters"][:2]
    rg = r["ranges"].set_index("Parameter")
    df = r["full"]
    inside = df[df[a].between(rg.loc[a, "Low"], rg.loc[a, "High"])
                & df[b].between(rg.loc[b, "Low"], rg.loc[b, "High"])]
    if inside.empty:
        return _box("Nhận xét", "<p>Không có set nào nằm trong khung đỏ.</p>", "warn")
    lift = inside["FinalScore"].mean() / df["FinalScore"].mean() - 1
    items = [
        f"Khung đỏ chứa <b>{len(inside):,}</b> set ({len(inside) / len(df):.0%} dữ liệu), "
        f"FinalScore trung bình <b>{inside['FinalScore'].mean():.3f}</b> so với "
        f"<b>{df['FinalScore'].mean():.3f}</b> toàn bộ ({lift:+.0%}).",
        f"Forward trung vị trong khung: <b>{inside['Forward Result'].median():.1f}</b>; "
        f"Back trung vị: <b>{inside['Back Result'].median():.1f}</b>.",
    ]
    kind = "good" if lift > 0.1 else "warn"
    if lift <= 0.1:
        items.append("Khung chỉ tốt hơn trung bình không đáng kể: hai tham số này không đủ để tách vùng tốt.")
    return _box("Nhận xét", _ul(items), kind)


def profiles_note(r):
    df, rg = r["full"], r["ranges"].set_index("Parameter")
    items = []
    for p in r["parameters"]:
        if df[p].nunique() < 3:
            continue
        rho = df[p].corr(df["FinalScore"], method="spearman")
        trend = ("tăng" if rho > 0.15 else "giảm" if rho < -0.15 else "gần như không đổi")
        lo, hi = df[p].min(), df[p].max()
        edge = ""
        flags = _edges(p, rg.loc[p, "Low"], rg.loc[p, "High"], lo, hi, rg.loc[p, "Step"])
        if "upper" in flags:
            edge = " Range chạm <b>biên trên</b> của vùng đã test: nên mở rộng dải test lên cao hơn."
        elif "lower" in flags:
            edge = " Range chạm <b>biên dưới</b> của vùng đã test: nên mở rộng dải test xuống thấp hơn."
        elif Config.PARAM_BOUNDS.get(p, (None, None))[0] is not None and rg.loc[p, "Low"] <= Config.PARAM_BOUNDS[p][0]:
            edge = f" Range đã ở giới hạn tối thiểu của tham số ({Config.PARAM_BOUNDS[p][0]:g}), không cần mở rộng."
        width = (rg.loc[p, "High"] - rg.loc[p, "Low"]) / (hi - lo) if hi > lo else 0
        items.append(
            f"<b>{p}</b>: giá trị cao hơn thì điểm {trend} (Spearman {rho:+.2f}). "
            f"Range {rg.loc[p, 'Low']:g} → {rg.loc[p, 'High']:g} "
            f"chiếm {width:.0%} vùng đã test, center {rg.loc[p, 'Center']:g}.{edge}"
        )
    return _box("Nhận xét theo tham số", _ul(items))


def box_note(r):
    st, s = r["stable"], r["summary"]
    items = []
    for _, x in s.iterrows():
        iqr = st[st["Cluster"] == x["Cluster"]]["Forward Result"].quantile([.25, .75])
        items.append(f"Cluster {int(x['Cluster'])}: {int(x['Count'])} set, "
                     f"Forward trung vị {x['ForwardMedian']:.1f} (IQR {iqr.iloc[0]:.1f}–{iqr.iloc[1]:.1f}).")
    return _box("Nhận xét", _ul(items))


# --------------------------------------------------------------- tables

def clusters_html(r):
    s = r["summary"].copy()
    top_fwd = s["ForwardMedian"].idxmax()
    stable_idx = s["RelativeGap"].idxmin()
    rows = []
    for i, x in s.iterrows():
        tags = []
        if i == 0:
            tags.append("<b>Khuyến nghị</b> (điểm cao nhất)")
        if i == top_fwd:
            tags.append("lợi nhuận Forward cao nhất")
        if i == stable_idx:
            tags.append("ổn định nhất (gap thấp nhất)")
        if not x["Eligible"]:
            tags.append(f"nhỏ hơn {Config.MIN_CLUSTER_SIZE} set, không đáng tin")
        if x["RelativeGap"] > 0.3:
            tags.append("gap lớn: Forward và Back lệch nhau nhiều")
        if x["NeighbourScore"] < s["NeighbourScore"].median() * 0.9:
            tags.append("vùng xung quanh yếu (dễ là đỉnh nhọn)")
        rows.append({
            "Cluster": int(x["Cluster"]), "Số set": int(x["Count"]),
            "Forward": _fmt(x["ForwardMedian"], 1), "Back": _fmt(x["BackMedian"], 1),
            "Gap tương đối": _fmt(x["RelativeGap"], 3), "Neighbour": _fmt(x["NeighbourScore"], 3),
            "Điểm cluster": _fmt(x["ClusterScore"], 3),
            "Nhận xét": "; ".join(tags) or "—",
        })
    return ("<h2>4. Các cluster</h2>"
            + _box("Cách đọc", "<p>Cluster là nhóm bộ tham số có giá trị gần nhau. "
                   "Điểm cluster = Forward + Consistency + Neighbour + kích thước (xem config.py). "
                   "Nên ưu tiên cluster vừa điểm cao, vừa đủ lớn.</p>")
            + pd.DataFrame(rows).to_html(index=False, escape=False, classes="t"))


def recommendation_html(r):
    best, sub = _best(r)
    full, rg = r["full"], r["ranges"]
    rows, warns = [], []
    for x in rg.itertuples():
        lo, hi = full[x.Parameter].min(), full[x.Parameter].max()
        width = (x.High - x.Low) / (hi - lo) if hi > lo else 0
        cm = []
        if width < 0.15:
            cm.append("range hẹp: đã hội tụ")
        elif width > 0.6:
            cm.append("range rộng: tham số ít nhạy trong cluster này")
        flags = _edges(x.Parameter, x.Low, x.High, lo, hi, x.Step)
        if "upper" in flags:
            cm.append("chạm biên trên của vùng test")
            warns.append(f"{x.Parameter}: mở rộng dải test lên trên {hi:g}.")
        if "lower" in flags:
            cm.append("chạm biên dưới của vùng test")
            warns.append(f"{x.Parameter}: mở rộng dải test xuống dưới {lo:g}.")
        rows.append({
            "Tham số": x.Parameter, "Từ": f"{x.Low:g}", "Đến": f"{x.High:g}",
            "Center": f"{x.Center:g}", "Bước": f"{x.Step:g}",
            "Vùng đã test": f"{lo:g} → {hi:g}", "Nhận xét": "; ".join(cm) or "—",
        })
    n = int(best["Count"])
    conf = []
    conf.append(f"Cluster có {n} set: " + ("đủ lớn." if n >= 20 else "nhỏ, cẩn thận."))
    conf.append(f"Neighbour score {sub['NeighbourScore'].mean():.3f} "
                f"({'vùng xung quanh cũng tốt' if sub['NeighbourScore'].mean() > r['full']['FinalScore'].mean() else 'vùng xung quanh kém trung bình'}).")
    iso = (sub["NeighbourCount"] == 0).mean()
    if iso > 0.2:
        warns.append(f"{iso:.0%} set trong cluster không có láng giềng (điểm cô lập).")
    out = ("<h2>5. Range khuyến nghị cho lần tối ưu kế tiếp</h2>"
           + pd.DataFrame(rows).to_html(index=False, escape=False, classes="t")
           + _box("Độ tin cậy", _ul(conf), "good" if not warns else "note"))
    if warns:
        out += _box("Cần xem lại", _ul(warns), "warn")
    return out


def top_sets_html(r, n=15):
    pool = pd.concat([r["stable"], r["elite"]]).loc[lambda d: ~d.index.duplicated()]
    pool = pool.sort_values("FinalScore", ascending=False).head(n)
    nb_med = r["stable"]["NeighbourScore"].median() if "NeighbourScore" in r["stable"] else None
    elite_idx = set(r["elite"].index)
    rows = []
    for idx, x in pool.iterrows():
        cm = []
        if idx in elite_idx:
            cm.append("Elite")
        g = x["RelativeGap"]
        cm.append("rất ổn định" if g < 0.1 else "lệch lớn Forward/Back" if g > 0.3 else "ổn định vừa")
        if x["Forward Result"] < 0.6 * x["Back Result"]:
            cm.append("Forward yếu hơn Back nhiều: có thể overfit Back")
        if "NeighbourCount" in x and x["NeighbourCount"] == 0:
            cm.append("điểm cô lập, không có láng giềng: dễ là nhiễu")
        elif nb_med is not None and x.get("NeighbourScore", nb_med) < nb_med * 0.9:
            cm.append("vùng xung quanh yếu")
        if x.get("Trades", 1e9) < 150:
            cm.append("ít lệnh")
        if x.get("Equity DD %", 0) > 30:
            cm.append(f"DD cao ({x['Equity DD %']:.0f}%)")
        row = {p: f"{x[p]:g}" for p in r["parameters"]}
        row.update({
            "Forward": _fmt(x["Forward Result"], 1), "Back": _fmt(x["Back Result"], 1),
            "Gap tương đối": _fmt(g, 2), "Score": _fmt(x["FinalScore"], 3),
            "Cluster": int(x["Cluster"]) if "Cluster" in x and pd.notna(x["Cluster"]) else "—",
            "Nhận xét": "; ".join(cm),
        })
        rows.append(row)
    return ("<h2>6. Các bộ tham số tốt nhất</h2>"
            + _box("Cách đọc", "<p>Top theo FinalScore trong tập Stable + Elite. "
                   "Dùng để kiểm tra từng set cụ thể; khuyến nghị nên dựa vào range của "
                   "cả cluster chứ không chọn một set đơn lẻ.</p>")
            + pd.DataFrame(rows).to_html(index=False, escape=False, classes="t"))
