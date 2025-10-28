"""
Streamlit App V4 — Local Housing Policy Assessment Tool
Adds: Sidebar navigation and Literature Dataset viewer
"""

import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Local Housing Policy Tool", page_icon="🏘️", layout="wide")

# -------------------------
# Sidebar Navigation
# -------------------------
st.sidebar.title("🏡 Navigation")
page = st.sidebar.radio(
    "Go to:",
    ["🏘️ Policy Assessment Tool", "📚 Literature Dataset"],
    index=0
)

# -------------------------
# PAGE 1: Main Policy Assessment Tool
# -------------------------
if page == "🏘️ Policy Assessment Tool":
    st.title("🏘️ Local Housing Policy Assessment Tool")
    st.markdown("""
    Welcome! Answer the four questions below to receive **tailored policy category recommendations** for your community.
    """)

    st.divider()

    # Local Toolkit PDF link
    pdf_path = "Local Housing Policy Toolkit.pdf"
    try:
        with open(pdf_path, "rb") as _pdf_file:
            pdf_bytes = _pdf_file.read()
        st.markdown("### 📘 Local Housing Policy Toolkit")
        st.markdown("For deeper context and step-by-step instructions on how to use this app:")
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                "Download Toolkit (PDF)",
                data=pdf_bytes,
                file_name="Local_Housing_Policy_Toolkit.pdf",
                mime="application/pdf"
            )
        with col2:
            safe_href = pdf_path.replace(" ", "%20")
            st.markdown(f'<a href="{safe_href}" target="_blank">Open Toolkit in new tab</a>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Toolkit PDF not found at: {pdf_path}.")

    st.divider()

    # -------------------------
    # QUESTIONS
    # -------------------------
    st.subheader("1️⃣ Legal Local Authority")
    st.markdown("""
    What best describes your jurisdiction's legal authority to adopt housing policies?  
    *Research the level of preemptions that may exist for your community.*
    """)
    st.markdown(
        '[🔗 View state-by-state Dillon Rule vs Home Rule map (ALEC White Paper, 2016)](https://alec.org/wp-content/uploads/2016/01/2016-ACCE-White-Paper-Dillon-House-Rule-Final.pdf)',
        unsafe_allow_html=True
    )
    authority = st.radio(
        "Select one:",
        ["Strong Local Authority (Home Rule - broad powers; few preemptions)",
         "Limited Local Authority (Dillon Rule - state restricts key areas; significant preemptions)",
         "Unsure"]
    )

    st.divider()

    st.subheader("2️⃣ Municipal Capacity")
    capacity = st.radio(
        "How would you describe your organization’s financial and administrative resources for implementing housing policies?",
        ["Strong Capacity (dedicated funding, deep staffing levels)",
         "Moderate Capacity (limited budget, small or inexperienced staff)",
         "Minimal Capacity (near-zero budget, minimal staff)"]
    )

    st.divider()

    st.subheader("3️⃣ Housing Market Dynamics")
    market = st.radio(
        "What best describes your local housing market?",
        ["Hot Market", "Stable Market", "Weak/Declining Market"]
    )

    st.divider()

    st.subheader("4️⃣ Primary Housing Challenge")
    challenge = st.radio(
        "What is your MOST pressing issue? Only select Multiple Crises if two or more challenges are equally critical.",
        ["Supply Shortage", "Affordability Crisis", "Housing Quality", "Multiple Crises"]
    )

    st.divider()
    st.markdown("### 🔍 Review your selections before submitting")
    with st.expander("View Summary of Your Responses"):
        st.write(f"**Legal Authority:** {authority}")
        st.write(f"**Municipal Capacity:** {capacity}")
        st.write(f"**Housing Market:** {market}")
        st.write(f"**Primary Challenge:** {challenge}")

    st.divider()

    # -------------------------
    # Core Logic Functions
    # -------------------------
    def normalize_inputs(authority, capacity, market, challenge):
        a = "Unsure" if "Unsure" in authority else ("Limited" if "Limited" in authority else "Strong")
        c = "Minimal" if "Minimal" in capacity else ("Moderate" if "Moderate" in capacity else "Strong")
        m = "Weak" if "Weak" in market else ("Stable" if "Stable" in market else "Hot")
        ch = ("Multiple" if "Multiple" in challenge else
              ("Quality" if "Quality" in challenge else
               ("Affordability" if "Affordability" in challenge else "Supply")))
        return a, c, m, ch

    def determine_buckets(authority, capacity, market, challenge):
        buckets = set()
        if capacity == "Minimal":
            return ["Foundation-Building (FB)"], "Minimal capacity: prioritize low-cost/no-cost foundation-building activities."
        if market == "Weak":
            buckets.add("Foundation-Building (FB)")
            if capacity in ["Moderate", "Strong"] and challenge in ["Quality", "Multiple"]:
                buckets.add("Preservation & Stabilization (PS)")
            return sorted(buckets), "Weak market: prioritize foundation-building; add preservation if capacity and quality risk exist."
        limited_authority = (authority == "Limited")
        if challenge == "Supply":
            if limited_authority:
                buckets.add("Development Incentives (DI)")
            else:
                buckets.update(["Regulatory Supply (RS)", "Development Incentives (DI)"])
        if challenge == "Affordability":
            buckets.add("Financial Assistance (FA)")
            if authority == "Strong":
                buckets.add("Tenant Protections (TP)")
            if not limited_authority:
                buckets.add("Regulatory Supply (RS)")
            buckets.add("Development Incentives (DI)")
        if challenge == "Quality":
            buckets.add("Preservation & Stabilization (PS)")
            if authority == "Strong":
                buckets.add("Regulatory Supply (RS)")
            buckets.add("Development Incentives (DI)")
        if challenge == "Multiple":
            if capacity in ["Moderate", "Strong"]:
                buckets.add("Preservation & Stabilization (PS)")
            buckets.add("Financial Assistance (FA)")
            if authority == "Strong":
                buckets.update(["Regulatory Supply (RS)", "Development Incentives (DI)", "Tenant Protections (TP)"])
            else:
                buckets.add("Development Incentives (DI)")
        base_order = [
            "Foundation-Building (FB)",
            "Preservation & Stabilization (PS)",
            "Regulatory Supply (RS)",
            "Development Incentives (DI)",
            "Financial Assistance (FA)",
            "Tenant Protections (TP)"
        ]
        ordered = [b for b in base_order if b in buckets]
        return ordered, "Recommendation generated using core logic."

    def apply_priority_overlay(challenge_code, buckets):
        bucket_set = set(buckets)
        priority_order = []
        final_order = []
        if challenge_code == "Affordability":
            if "Financial Assistance (FA)" in bucket_set:
                priority_order.append("Financial Assistance (FA)")
            if "Tenant Protections (TP)" in bucket_set:
                priority_order.append("Tenant Protections (TP)")
        elif challenge_code == "Supply":
            if "Regulatory Supply (RS)" in bucket_set:
                priority_order.append("Regulatory Supply (RS)")
            if "Development Incentives (DI)" in bucket_set:
                priority_order.append("Development Incentives (DI)")
        for p in priority_order:
            if p not in final_order:
                final_order.append(p)
        for b in buckets:
            if b not in final_order:
                final_order.append(b)
        return final_order, priority_order

    # -------------------------
    # Guidance Dictionary (same as before)
    # -------------------------
    GUIDANCE = {
    "Foundation-Building (FB)": (
        "These strategies lay the groundwork for future housing initiatives and strengthen the "
        "local housing ecosystem. Examples include zoning code reviews, ADU enabling, "
        "manufactured housing code reform, and property tax relief pilots. "
        "They are low-cost, easy to implement, and help communities with limited capacity address affordability "
        "and quality concerns without requiring extensive funding or staff. Ideal for small towns, weak markets, or minimal capacity scenarios."
    ),
    "Preservation & Stabilization (PS)": (
        "These tools help maintain and improve the existing housing stock, protecting residents "
        "from displacement and preserving affordable units. Examples include community land trusts, "
        "acquisition/rehab grants, housing trust funds, and code enforcement/rehab loan programs. "
        "Effective in communities with aging housing or moderate funding/staff capacity. "
        "They prevent further deterioration and can stabilize neighborhoods, but require upfront capital and ongoing management."
    ),
    "Regulatory Supply (RS)": (
        "Regulatory strategies increase housing supply through zoning and planning changes. "
        "Examples: upzoning, inclusionary zoning (if legally allowed), ADU allowances, density bonuses. "
        "These tools are most effective in hot or stable markets with development pressure. "
        "Constraints include state preemption, potential local opposition, and administrative complexity. "
        "They help create long-term housing availability, but poorly designed programs may slow development or trigger NIMBY pushback."
    ),
    "Development Incentives (DI)": (
        "Incentive programs encourage private developers to build housing that meets community goals. "
        "Examples: fee waivers, expedited permitting, tax abatements, public land disposition, gap financing. "
        "Most effective in active development markets where additional subsidies or process speed-ups can overcome cost barriers. "
        "These tools can be politically sensitive, require financial resources, and may benefit developers more than residents directly."
    ),
    "Financial Assistance (FA)": (
        "Direct financial support helps residents afford housing in the short term and reduces displacement. "
        "Examples: rental subsidies, down payment assistance, property tax circuit breakers, mortgage assistance. "
        "Effective in communities with affordability pressures and moderate or strong fiscal/admin capacity. "
        "Trade-offs include ongoing funding commitment and limited reach per program, but they provide immediate relief to households."
    ),
    "Tenant Protections (TP)": (
        "Legal protections for renters stabilize households and reduce displacement risk. "
        "Examples: just-cause eviction, rent stabilization, right to counsel, junk fee limits. "
        "Most effective in hot markets with strong tenant organizing or advocacy. "
        "Constraints include state preemption in some areas, potential impact on rental supply if overly restrictive, "
        "and administrative/enforcement costs. These tools complement financial assistance and preserve housing stability."
    )
}

    if st.button("📊 Generate Policy Recommendations"):
        a, c, m, ch = normalize_inputs(authority, capacity, market, challenge)
        if a == "Unsure":
            st.warning("Please check state law before proceeding.")
            st.stop()
        base_buckets, note = determine_buckets(a, c, m, ch)
        final_buckets, priority_list = apply_priority_overlay(ch, base_buckets)
        st.success("✅ Policy Recommendation Complete!")
        st.markdown("## 🧭 Recommended Policy Categories")
        if priority_list:
            st.subheader("🌟 Start Here — Priority Actions")
            for p in priority_list:
                st.markdown(f"**{p}**")
                st.caption(GUIDANCE.get(p, ""))
        remaining = [b for b in final_buckets if b not in priority_list]
        if remaining:
            st.subheader("✅ Also Recommended")
            for r in remaining:
                st.markdown(f"- {r}")
                st.caption(GUIDANCE.get(r, ""))
        st.divider()
        st.subheader("Rationale & Notes")
        st.write(f"**Inputs:** Authority={a} | Capacity={c} | Market={m} | Challenge={ch}")
        st.write(note)
        df = pd.DataFrame([{
            'authority': a, 'capacity': c, 'market': m, 'challenge': ch,
            'recommendations': '; '.join(final_buckets),
            'priority_order': '; '.join(priority_list),
            'note': note
        }])
        csv = df.to_csv(index=False)
        st.download_button('Download Recommendation (CSV)', data=csv,
                           file_name='policy_recommendation_v4.csv', mime='text/csv')

# -------------------------
# PAGE 2: Literature Dataset Viewer
# -------------------------
elif page == "📚 Literature Dataset":
    st.title("📚 Literature Dataset Viewer")
    st.markdown("Below are the files used to synthesize research behind this tool.")

    folder_path = "Literature Dataset"
    if not os.path.exists(folder_path):
        st.warning(f"Folder not found: `{folder_path}`. Please make sure it exists in the app directory.")
    else:
        files = os.listdir(folder_path)
        if not files:
            st.info("No files found in the Literature Dataset folder.")
        else:
            for f in sorted(files):
                file_path = os.path.join(folder_path, f)
                st.markdown(f"**📄 {f}**")
                with open(file_path, "rb") as file:
                    st.download_button(
                        label=f"Download {f}",
                        data=file,
                        file_name=f,
                        mime="application/octet-stream"
                    )
                st.divider()
