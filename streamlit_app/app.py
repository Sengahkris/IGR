"""Rwanda Insurance Gap Radar - lookalike edition (NISR Big Data Hackathon 2026, Track 2).

Finds uninsured/unpensioned adults who statistically resemble people who already hold the
product ("lookalikes") versus those who don't ("dissimilar").

Run: streamlit run app.py
Reads only pre-aggregated / model artifacts - no respondent-level survey rows.
"""
import json
from pathlib import Path

import joblib
import pandas as pd
import shap
import streamlit as st

import ai_chat
import charts
import theme

st.set_page_config(page_title="Rwanda Insurance Gap Radar", layout="wide")
theme.inject_theme()

ART = Path(__file__).resolve().parent / "artifacts"
TARGET_LABEL = {"insurance_uptake": "Insurance", "pension_uptake": "Pension"}
PENSION_PRODUCTS = {"RSSB public pension", "Private pension", "Ejo Heza"}


@st.cache_resource
def load_bundle():
    return joblib.load(ART / "insurance_model.joblib")


@st.cache_data
def load_tables():
    facts = json.load(open(ART / "national_facts.json"))
    archetypes = json.load(open(ART / "archetype_names.json"))
    briefs = json.load(open(ART / "briefs.json"))
    seg_agg = pd.read_csv(ART / "segment_aggregates.csv")
    seg_drivers = pd.read_csv(ART / "segment_top_drivers.csv")
    arch_drivers = pd.read_csv(ART / "archetype_top_drivers.csv")
    return facts, archetypes, briefs, seg_agg, seg_drivers, arch_drivers


bundle = load_bundle()
facts, archetypes, briefs, seg_agg, seg_drivers, arch_drivers = load_tables()
FEATURES = bundle["features"]
LABELS = facts["feature_labels"]


def driver_label(name):
    return LABELS.get(name, name.replace("_", " "))


theme.hero(
    "Rwanda National Insurance Gap Radar",
    "Who looks like an insured or pension-holding adult but isn't one yet.",
)

top3 = briefs[:3]
total_lookalike_millions = sum(b["adults_k"] for b in briefs) / 1000
theme.finding_strip(
    f"<b>{total_lookalike_millions:.2f} million</b> adults statistically resemble people who already "
    f"hold insurance or a pension, but don't yet. The three easiest segments to reach: "
    + " · ".join(f"{b['title'].split('—')[-1].strip()} ({b['adults_k']/1000:.2f}M)" for b in top3)
)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "National picture", "Insured profile", "Lookalike finder", "Score a profile", "Insights",
])

# ================================================================== TAB 1
with tab1:
    c1, c2, c3 = st.columns(3)
    c1.metric("Financially included", f"{facts['financial_inclusion']:.0%}")
    c2.metric("Hold health cover", f"{facts['health_cover']:.1%}")
    c3.metric("Hold any non-health product", f"{facts['any_uptake']:.1%}")

    st.markdown(
        f"Split into two gaps with different drivers: **Insurance** "
        f"{facts['insurance_uptake']:.1%} and **Pension** {facts['pension_uptake']:.1%}."
    )

    st.caption("Insurance vs. pension by province")
    st.plotly_chart(charts.province_comparison(facts["province_uptake"]), use_container_width=True)

    g1, g2 = st.columns(2)
    with g1:
        st.caption("Commercial insurance products (13 types)")
        commercial = pd.Series({k: v for k, v in facts["product_uptake"].items() if k not in PENSION_PRODUCTS}).sort_values()
        st.plotly_chart(charts.pct_bar(commercial, color=charts.BLUE, height=360), use_container_width=True)
    with g2:
        st.caption("Pension & long-term savings")
        pension = pd.Series({k: v for k, v in facts["product_uptake"].items() if k in PENSION_PRODUCTS}).sort_values()
        st.plotly_chart(charts.pct_bar(pension, color=charts.GREEN, height=360), use_container_width=True)
        st.caption("Shown separately: Ejo Heza's reach (19%) would otherwise visually mask how small every commercial product is.")

    st.caption("Lookalike density by province")
    map_target = st.radio("Gap", list(TARGET_LABEL), format_func=TARGET_LABEL.get, horizontal=True, key="t1_map_target")
    rates = charts.province_lookalike_rates(seg_agg, map_target)
    top_prov = rates.idxmax()
    st.caption(f"{top_prov} has the highest share of lookalikes ({rates.max():.1f}% of adults).")
    st.plotly_chart(charts.province_choropleth(rates), use_container_width=True)

# ================================================================== TAB 2
with tab2:
    target = st.radio("Gap", list(TARGET_LABEL), format_func=TARGET_LABEL.get, horizontal=True, key="t2_target")
    st.caption("Four archetypes per gap, clustered from people who already hold the product.")

    arch = archetypes[target]
    st.plotly_chart(charts.archetype_sizes(arch), use_container_width=True)
    st.plotly_chart(charts.archetype_comparison(arch), use_container_width=True)

    cols = st.columns(2)
    for i, a in enumerate(arch):
        drivers_row = arch_drivers[(arch_drivers.target == target) & (arch_drivers.cluster_id == a["cluster_id"])]
        driver_text = ", ".join(
            driver_label(drivers_row.iloc[0][f"top_driver_{k}"]) for k in (1, 2, 3)
        ) if len(drivers_row) else "—"
        small_sample = a["n"] < 50
        warn_pill = '<span class="pill pill-warn">small sample</span>' if small_sample else ""
        card_html = (
            '<div class="card">'
            f'<span class="pill">{a["adults_k"]/1000:.2f}M adults</span>'
            f'<span class="pill">n={a["n"]}</span>{warn_pill}'
            f'<h4>{a["name"].title()}</h4>'
            f'<p style="font-size:0.85rem;margin:0">Top distinguishing factors: {driver_text}</p>'
            '</div>'
        )
        with cols[i % 2]:
            st.markdown(card_html, unsafe_allow_html=True)

# ================================================================== TAB 3
with tab3:
    target = st.radio("Gap", list(TARGET_LABEL), format_func=TARGET_LABEL.get, horizontal=True, key="t3_target")
    st.caption(
        "A **lookalike** is an uninsured/unpensioned adult whose calibrated propensity score "
        f"clears the model's F1-optimised threshold ({bundle['thresholds'][target]:.2f}) — "
        "i.e. the model would have called them a holder."
    )
    sa = seg_agg[seg_agg.target == target]
    sd = seg_drivers[seg_drivers.target == target]

    f1, f2, f3, f4 = st.columns(4)
    sel_prov = f1.multiselect("Province", sorted(sa.province.unique()), key="t3_prov")
    sel_area = f2.multiselect("Urban / rural", sorted(sa.urban_rural.unique()), key="t3_area")
    sel_live = f3.multiselect("Livelihood", sorted(sa.main_livelihood.unique()), key="t3_live")
    sel_edu = f4.multiselect("Education", sorted(sa.education.unique()), key="t3_edu")

    mask = pd.Series(True, index=sa.index)
    for col, sel in [("province", sel_prov), ("urban_rural", sel_area),
                     ("main_livelihood", sel_live), ("education", sel_edu)]:
        if sel:
            mask &= sa[col].isin(sel)
    sub = sa[mask]

    if sub["n"].sum() < 20:
        st.warning(f"Only {int(sub['n'].sum())} surveyed respondents match - widen the filters.")
    else:
        total_adults = sub["adults_k"].sum()
        holder_adults = (sub["adults_k"] * sub["holder_rate"]).sum()
        lookalike_adults = (sub["adults_k"] * sub["lookalike_rate"]).sum()
        dissimilar_adults = (sub["adults_k"] * sub["dissimilar_rate"]).sum()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Adults in filter", f"{total_adults/1000:,.2f}M")
        m2.metric("Already hold it", f"{holder_adults/1000:,.2f}M", f"{holder_adults/total_adults:.0%}", delta_color="off")
        m3.metric("Lookalikes", f"{lookalike_adults/1000:,.2f}M", f"{lookalike_adults/total_adults:.0%}", delta_color="off")
        m4.metric("Dissimilar", f"{dissimilar_adults/1000:,.2f}M", f"{dissimilar_adults/total_adults:.0%}", delta_color="off")
        st.caption("Holders + Lookalikes + Dissimilar = Adults in filter, by construction.")

        key_cols = ["province", "urban_rural", "education", "main_livelihood"]
        sub_drivers = sd.merge(sub[key_cols].drop_duplicates(), on=key_cols, how="inner")
        if len(sub_drivers):
            all_drivers = pd.concat([sub_drivers[f"top_driver_{k}"] for k in (1, 2, 3)])
            top = all_drivers.value_counts().head(3)
            st.caption("Most distinguishing factors: " + ", ".join(driver_label(x) for x in top.index))

        st.caption("Top segments by lookalike count")
        sa_t = sa.copy()
        sa_t["lookalike_adults_k"] = sa_t["adults_k"] * sa_t["lookalike_rate"]
        # Summed across Ubudehe category so each displayed row is genuinely distinct (the
        # filter columns below don't include Ubudehe, so two rows differing only by it would
        # otherwise look like duplicates).
        top_segs = (
            sa_t.groupby(["province", "urban_rural", "education", "main_livelihood"], observed=True)
            .agg(lookalike_adults_k=("lookalike_adults_k", "sum"))
            .reset_index()
            .sort_values("lookalike_adults_k", ascending=False)
            .head(8)
        )
        top_segs.columns = ["Province", "Area", "Education", "Livelihood", "Lookalikes (k)"]
        st.dataframe(top_segs.style.format({"Lookalikes (k)": "{:,.0f}"}), hide_index=True, use_container_width=True)

# ================================================================== TAB 4
with tab4:
    st.caption(
        "Describe a person and see their calibrated propensity score for each product — a "
        "lookalike-match strength, not a causal prediction."
    )

    profile = {}
    PRIMARY = ["age", "sex", "education", "marital_status", "ubudehe_category", "main_livelihood",
               "owns_motor_vehicle", "urban_rural", "time_to_insurance_branch", "used_mobile_money"]

    def render_input(name, container):
        if name in bundle["numeric"]:
            lo, hi = (16, 99) if name == "age" else (1, 10)
            default = 35 if name == "age" else 4
            profile[name] = container.slider(driver_label(name), lo, hi, default, key=f"in_{name}")
        else:
            opts = bundle["choices"][name]
            profile[name] = container.selectbox(driver_label(name), opts, key=f"in_{name}")

    form_col, result_col = st.columns([1, 1.3])
    with form_col:
        for name in PRIMARY:
            render_input(name, st)
        with st.expander("More questions (optional)"):
            for name in FEATURES:
                if name not in PRIMARY:
                    render_input(name, st)

    X = pd.DataFrame([profile])[FEATURES]

    @st.cache_resource
    def get_explainers():
        return {t: shap.TreeExplainer(bundle["pipelines"][t].named_steps["model"]) for t in bundle["targets"]}

    explainers = get_explainers()

    with result_col:
        rc1, rc2 = st.columns(2)
        for col, t in zip([rc1, rc2], bundle["targets"]):
            pipe = bundle["pipelines"][t]
            raw_prob = pipe.predict_proba(X)[0, 1]
            cal_prob = float(bundle["calibrators"][t].predict([raw_prob])[0])
            col.metric(
                f"{TARGET_LABEL[t]} — propensity score", f"{cal_prob:.0%}",
                f"{(cal_prob - facts[t]) * 100:+.0f} pts vs national", delta_color="off",
                help="Calibrated to the true national rate, not a raw model output — a 50%-everyone score from an uncalibrated balanced classifier would be misleading.",
            )

        archetype_lines = []
        for t in bundle["targets"]:
            prep = bundle["pipelines"][t].named_steps["prep"]
            x_enc = bundle["archetype_scalers"][t].transform(prep.transform(X))
            cl = int(bundle["archetype_models"][t].predict(x_enc)[0])
            name = next(a["name"] for a in archetypes[t] if a["cluster_id"] == cl)
            archetype_lines.append(f"{TARGET_LABEL[t]}: {name}")
        st.caption("Closest archetype — " + " · ".join(archetype_lines))

        for t in bundle["targets"]:
            pipe = bundle["pipelines"][t]
            prep = pipe.named_steps["prep"]
            sv = explainers[t].shap_values(prep.transform(X), check_additivity=False)
            sv_pos = sv[1] if isinstance(sv, list) else sv[..., 1]
            contrib = pd.Series(sv_pos[0]).groupby(bundle["column_to_feature"]).sum()
            st.caption(f"{TARGET_LABEL[t]} — what moved the score")
            st.plotly_chart(charts.waterfall(contrib, LABELS), use_container_width=True)

# ================================================================== TAB 5
with tab5:
    st.caption("Grounded in the exact numbers in this dashboard. Ask the chatbox for more detail.")
    for i, b in enumerate(briefs, start=1):
        card_html = (
            '<div class="card">'
            f'<span class="priority-badge priority-{min(i, 3)}">PRIORITY {i}</span>'
            f'<span class="pill">{b["gap"]} · {b["adults_k"]/1000:.2f}M</span>'
            f'<h4>{b["title"]}</h4>'
            f'<p style="margin:4px 0">{b["body"]}</p>'
            f'<p class="muted" style="margin:0"><b>Channel:</b> {b["channel"]}</p>'
            f'<p class="muted" style="margin:0"><b>Product angle:</b> {b["product_angle"]}</p>'
            '</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

# ------------------------------------------------------------- floating chat
_insights = [f"{b['title']}: {b['body']} Channel: {b['channel']} Product angle: {b['product_angle']}" for b in briefs]
ai_chat.render_floating_chat(ai_chat.build_context(facts, archetypes, _insights))
