import pandas as pd
import json

print("Loading Global_Superstore_Cleaned_2.csv...")
df = pd.read_csv("/mnt/hades/HadesData/AI-visual/Global_Superstore_Cleaned_2.csv", encoding="utf-8-sig")

# 1. Cube data for interactive dashboard
cube = df.groupby(["Order Year", "Market", "Category", "Sub-Category"]).agg({
    "Sales": "sum",
    "Profit": "sum",
    "Shipping Cost": "sum",
    "Discount": "mean",
    "Global Order ID": "count"
}).reset_index().rename(columns={"Global Order ID": "Orders"})
cube["Sales"] = cube["Sales"].round(2)
cube["Profit"] = cube["Profit"].round(2)
cube["Shipping Cost"] = cube["Shipping Cost"].round(2)
cube["Discount"] = cube["Discount"].round(4)
cube_json = cube.to_dict(orient="records")

# 2. Monthly trend data
monthly = df.groupby(["Order Year", "Order Year-Month"]).agg({
    "Sales": "sum",
    "Profit": "sum",
    "Discount": "mean"
}).reset_index()
monthly["Sales"] = monthly["Sales"].round(2)
monthly["Profit"] = monthly["Profit"].round(2)
monthly["Margin"] = (monthly["Profit"] / monthly["Sales"] * 100).round(2)
monthly["Discount"] = (monthly["Discount"] * 100).round(2)
monthly_json = monthly.to_dict(orient="records")

# 3. Country data
country = df.groupby(["Market", "Country"]).agg({
    "Sales": "sum",
    "Profit": "sum",
    "Discount": "mean",
    "Global Order ID": "count"
}).reset_index().rename(columns={"Global Order ID": "Orders"})
country["Sales"] = country["Sales"].round(2)
country["Profit"] = country["Profit"].round(2)
country["Margin"] = (country["Profit"] / country["Sales"] * 100).round(2)
country["Discount"] = (country["Discount"] * 100).round(2)
country_json = country.to_dict(orient="records")

# 4. Discount Tier summary
df["Discount Tier"] = pd.cut(df["Discount"], bins=[-0.01, 0.0, 0.1, 0.2, 0.3, 0.5, 1.0], labels=["0% ราคาเต็ม", "1-10%", "11-20%", "21-30%", "31-50%", "51-80%"])
disc = df.groupby("Discount Tier", observed=False)[["Sales", "Profit", "Shipping Cost"]].agg({"Sales": "sum", "Profit": "sum", "Shipping Cost": "sum"}).reset_index()
disc["Orders"] = df.groupby("Discount Tier", observed=False)["Sales"].count().values
disc["Sales"] = disc["Sales"].round(2)
disc["Profit"] = disc["Profit"].round(2)
disc["Margin"] = (disc["Profit"] / disc["Sales"] * 100).round(2)
disc_json = disc.to_dict(orient="records")

# 5. Top 50 Drain / Bleeding Orders for table preview
drain_df = df[(df["Is Shipping Cost Draining Profit"] == True) | (df["Profit"] < -1000)].sort_values(by="Profit").head(50)
drain_cols = ["Global Order ID", "Order Year", "Market", "Country", "Sub-Category", "Product Name", "Sales", "Profit", "Discount", "Shipping Cost", "Ship Mode"]
drain_records = drain_df[drain_cols].copy()
drain_records["Sales"] = drain_records["Sales"].round(2)
drain_records["Profit"] = drain_records["Profit"].round(2)
drain_records["Shipping Cost"] = drain_records["Shipping Cost"].round(2)
drain_records["Discount"] = (drain_records["Discount"] * 100).round(0)
drain_json = drain_records.to_dict(orient="records")

db_data = {
    "cube": cube_json,
    "monthly": monthly_json,
    "country": country_json,
    "discount_tiers": disc_json,
    "drain_orders": drain_json
}

json_str = json.dumps(db_data, ensure_ascii=False)
print("Data JSON generated, length:", len(json_str))

html_content = f"""<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Global Superstore - Interactive Strategic BI & Executive Dashboard</title>
    <!-- Google Fonts & FontAwesome -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=Sarabun:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Chart.js -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    
    <style>
        :root {{
            --bg-obsidian: #07090e;
            --bg-surface: rgba(18, 24, 38, 0.75);
            --bg-surface-elevated: rgba(26, 35, 54, 0.85);
            --border-subtle: rgba(255, 255, 255, 0.08);
            --border-gold: rgba(245, 158, 11, 0.45);
            --border-glow: rgba(99, 102, 241, 0.45);
            --text-primary: #f8fafc;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            
            --gold: #f59e0b;
            --gold-light: #fde047;
            --indigo: #6366f1;
            --indigo-light: #a5b4fc;
            --emerald: #10b981;
            --emerald-light: #6ee7b7;
            --rose: #f43f5e;
            --rose-light: #fda4af;
            --cyan: #06b6d4;
            --purple: #a855f7;

            --gradient-luxury: linear-gradient(135deg, #f59e0b 0%, #fbbf24 50%, #d97706 100%);
            --gradient-primary: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
            --gradient-dark: linear-gradient(180deg, rgba(18, 24, 38, 0.85) 0%, rgba(10, 14, 23, 0.95) 100%);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Sarabun', 'Inter', sans-serif;
            background-color: var(--bg-obsidian);
            background-image: 
                radial-gradient(at 15% 15%, rgba(99, 102, 241, 0.12) 0px, transparent 45%),
                radial-gradient(at 85% 85%, rgba(245, 158, 11, 0.1) 0px, transparent 45%),
                radial-gradient(at 50% 50%, rgba(16, 185, 129, 0.05) 0px, transparent 50%);
            color: var(--text-primary);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
            letter-spacing: -0.01em;
        }}

        h1, h2, h3, h4, .font-heading {{
            font-family: 'Outfit', 'Sarabun', sans-serif;
            letter-spacing: -0.025em;
        }}

        code, pre, .font-mono {{
            font-family: 'Fira Code', monospace;
        }}

        /* Top Luxury Navbar */
        .navbar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.9rem 2.5rem;
            background: rgba(7, 9, 14, 0.9);
            backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border-subtle);
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }}

        .logo {{
            display: flex;
            align-items: center;
            gap: 0.85rem;
            font-weight: 700;
            font-size: 1.2rem;
            color: var(--text-primary);
        }}

        .logo-icon {{
            width: 36px;
            height: 36px;
            border-radius: 10px;
            background: var(--gradient-luxury);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #000;
            font-size: 1.15rem;
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.3);
        }}

        .logo-text {{
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        /* Mode Switcher Tabs in Navbar */
        .mode-switcher {{
            display: flex;
            background: rgba(255, 255, 255, 0.05);
            padding: 0.25rem;
            border-radius: 99px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}

        .mode-btn {{
            padding: 0.45rem 1.25rem;
            border-radius: 99px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-family: inherit;
            font-weight: 700;
            font-size: 0.88rem;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .mode-btn.active {{
            background: var(--gradient-luxury);
            color: #000;
            box-shadow: 0 4px 15px rgba(245, 158, 11, 0.35);
        }}

        .nav-controls {{
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .slide-counter {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-subtle);
            padding: 0.4rem 1.1rem;
            border-radius: 999px;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--indigo-light);
        }}

        .btn {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid var(--border-subtle);
            color: var(--text-primary);
            padding: 0.5rem 1.2rem;
            border-radius: 10px;
            font-family: inherit;
            font-weight: 600;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .btn:hover {{
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(255, 255, 255, 0.25);
            transform: translateY(-2px);
        }}

        .btn-gold {{
            background: var(--gradient-luxury);
            border: none;
            color: #000;
            font-weight: 700;
            box-shadow: 0 4px 20px rgba(245, 158, 11, 0.25);
        }}

        .btn-gold:hover {{
            box-shadow: 0 6px 25px rgba(245, 158, 11, 0.4);
            transform: translateY(-2px) scale(1.02);
            color: #000;
        }}

        /* Main Containers */
        .main-content {{
            flex: 1;
            padding: 5.5rem 2.5rem 4.5rem;
            max-width: 1550px;
            margin: 0 auto;
            width: 100%;
            display: flex;
            flex-direction: column;
        }}

        /* Slide Mode Area */
        .presentation-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
            flex: 1;
        }}

        .slide {{
            display: none;
            width: 100%;
            max-width: 1400px;
            background: var(--gradient-dark);
            border: 1px solid var(--border-subtle);
            border-radius: 24px;
            padding: 2.5rem 3rem;
            backdrop-filter: blur(25px);
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.6), 0 0 50px rgba(99, 102, 241, 0.08);
            animation: fadeIn 0.4s ease forwards;
            position: relative;
            overflow: hidden;
            max-height: calc(100vh - 10.5rem);
            overflow-y: auto;
        }}

        .slide::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #6366f1 0%, #f59e0b 50%, #10b981 100%);
        }}

        .slide.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(12px) scale(0.99); }}
            to {{ opacity: 1; transform: translateY(0) scale(1); }}
        }}

        /* Dashboard Mode Area */
        .dashboard-container {{
            display: none;
            width: 100%;
            background: var(--gradient-dark);
            border: 1px solid var(--border-subtle);
            border-radius: 24px;
            padding: 2rem 2.5rem;
            backdrop-filter: blur(25px);
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.6);
            animation: fadeIn 0.4s ease forwards;
        }}

        .dashboard-container.active {{
            display: block;
        }}

        /* Typography & Header Style */
        .slide-header {{
            margin-bottom: 1.75rem;
            position: relative;
        }}

        .slide-tag {{
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.12em;
            color: var(--gold-light);
            background: rgba(245, 158, 11, 0.12);
            border: 1px solid rgba(245, 158, 11, 0.35);
            padding: 0.35rem 0.9rem;
            border-radius: 999px;
            margin-bottom: 0.6rem;
        }}

        .slide-title {{
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.2;
            margin-bottom: 0.4rem;
            background: linear-gradient(135deg, #ffffff 0%, #cbd5e1 80%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .slide-subtitle {{
            font-size: 1.05rem;
            color: var(--text-secondary);
            line-height: 1.6;
        }}

        /* Grid Layouts */
        .grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 1.75rem; align-items: start; }}
        .grid-3 {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem; }}
        .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1.25rem; }}

        /* Cards */
        .card {{
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 18px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            position: relative;
        }}

        .card:hover {{
            background: rgba(255, 255, 255, 0.05);
            border-color: rgba(255, 255, 255, 0.18);
            transform: translateY(-3px);
        }}

        .card-icon {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            margin-bottom: 1rem;
        }}

        .icon-gold {{ background: rgba(245, 158, 11, 0.15); color: var(--gold-light); border: 1px solid rgba(245, 158, 11, 0.35); }}
        .icon-indigo {{ background: rgba(99, 102, 241, 0.15); color: var(--indigo-light); border: 1px solid rgba(99, 102, 241, 0.35); }}
        .icon-emerald {{ background: rgba(16, 185, 129, 0.15); color: var(--emerald-light); border: 1px solid rgba(16, 185, 129, 0.35); }}
        .icon-rose {{ background: rgba(244, 63, 94, 0.15); color: var(--rose-light); border: 1px solid rgba(244, 63, 94, 0.35); }}
        .icon-purple {{ background: rgba(168, 85, 247, 0.15); color: #d8b4fe; border: 1px solid rgba(168, 85, 247, 0.35); }}

        .card-title {{
            font-size: 1.15rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
            color: #ffffff;
        }}

        .card-text {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.6;
            margin-bottom: 0.5rem;
        }}

        .badge-pill {{
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .badge-danger {{ background: rgba(244, 63, 94, 0.15); color: #fda4af; border: 1px solid rgba(244, 63, 94, 0.3); }}
        .badge-success {{ background: rgba(16, 185, 129, 0.15); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3); }}
        .badge-gold {{ background: rgba(245, 158, 11, 0.15); color: #fde047; border: 1px solid rgba(245, 158, 11, 0.3); }}

        /* Interactive Filter Toolbar in Dashboard */
        .filter-toolbar {{
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            align-items: center;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem 1.5rem;
            border-radius: 16px;
            margin-bottom: 1.5rem;
        }}

        .filter-group {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .filter-label {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
        }}

        .filter-select {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #ffffff;
            padding: 0.45rem 1rem;
            border-radius: 8px;
            font-family: inherit;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            outline: none;
            transition: all 0.2s ease;
        }}

        .filter-select:hover, .filter-select:focus {{
            border-color: var(--gold);
            background: rgba(255, 255, 255, 0.1);
        }}

        .filter-select option {{
            background: #0d1117;
            color: #ffffff;
        }}

        .quick-btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: var(--text-secondary);
            padding: 0.45rem 0.9rem;
            border-radius: 8px;
            font-size: 0.82rem;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .quick-btn:hover, .quick-btn.active {{
            background: var(--gradient-luxury);
            color: #000;
            border-color: transparent;
            box-shadow: 0 2px 10px rgba(245, 158, 11, 0.3);
        }}

        /* KPI Cards in Dashboard */
        .kpi-card {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            padding: 1.25rem;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            position: relative;
            overflow: hidden;
        }}

        .kpi-card::after {{
            content: '';
            position: absolute;
            right: 0;
            bottom: 0;
            width: 80px;
            height: 80px;
            background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
            border-radius: 50%;
        }}

        .kpi-label {{
            font-size: 0.78rem;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.4rem;
        }}

        .kpi-val {{
            font-size: 1.85rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 0.25rem;
        }}

        .kpi-sub {{
            font-size: 0.75rem;
            color: var(--emerald-light);
            display: flex;
            align-items: center;
            gap: 0.3rem;
        }}

        /* Chart Canvas Boxes */
        .chart-box {{
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1.25rem;
            height: 350px;
            position: relative;
        }}

        .chart-title {{
            font-size: 1rem;
            font-weight: 700;
            color: #ffffff;
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        /* Table in Dashboard */
        .table-container {{
            background: rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1.25rem;
            margin-top: 1.5rem;
            max-height: 380px;
            overflow-y: auto;
        }}

        .data-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
        }}

        .data-table th, .data-table td {{
            padding: 0.75rem 1rem;
            text-align: left;
            font-size: 0.85rem;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
        }}

        .data-table th {{
            background: rgba(255, 255, 255, 0.06);
            color: var(--text-primary);
            font-weight: 700;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.05em;
            position: sticky;
            top: 0;
            z-index: 10;
        }}

        .data-table tr:hover td {{
            background: rgba(255, 255, 255, 0.04);
        }}

        /* Search Input */
        .search-input {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #ffffff;
            padding: 0.45rem 1rem;
            border-radius: 8px;
            font-family: inherit;
            font-size: 0.85rem;
            outline: none;
            width: 250px;
            transition: all 0.2s ease;
        }}

        .search-input:focus {{
            border-color: var(--gold);
            width: 280px;
        }}

        /* Speaking Script Drawer */
        .speaking-notes {{
            background: rgba(10, 14, 23, 0.95);
            border: 1px solid rgba(245, 158, 11, 0.35);
            border-radius: 18px;
            padding: 1.25rem 1.5rem;
            margin-top: 1.5rem;
            display: none;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5);
        }}

        .speaking-notes.show {{
            display: block;
            animation: slideUp 0.3s ease;
        }}

        @keyframes slideUp {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .notes-header {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            color: var(--gold-light);
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }}

        .notes-text {{
            color: #cbd5e1;
            font-size: 0.9rem;
            line-height: 1.7;
            padding-left: 1rem;
            border-left: 3px solid var(--gold);
        }}

        /* Footer Navigation */
        .footer-controls {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.8rem 2.5rem;
            background: rgba(7, 9, 14, 0.9);
            backdrop-filter: blur(20px);
            border-top: 1px solid var(--border-subtle);
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            z-index: 1000;
        }}

        .slide-dots {{ display: flex; gap: 0.4rem; }}

        .dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.2);
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .dot.active {{
            background: var(--gold);
            width: 26px;
            border-radius: 999px;
            box-shadow: 0 0 10px rgba(245, 158, 11, 0.6);
        }}

        /* Hero Style */
        .title-main {{
            font-size: 3.5rem;
            font-weight: 900;
            line-height: 1.15;
            margin-bottom: 1.25rem;
            background: linear-gradient(135deg, #ffffff 0%, #fde047 50%, #f59e0b 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        /* ========================================== */
        /* RESPONSIVE & MOBILE-FIRST DESIGN UTILITIES */
        /* ========================================== */

        /* Tablet & Smaller Laptops (max-width: 1024px) */
        @media (max-width: 1024px) {{
            .navbar {{
                padding: 0.8rem 1.5rem;
                flex-wrap: wrap;
                gap: 0.75rem;
                justify-content: space-between;
            }}
            .mode-switcher {{
                order: 3;
                width: 100%;
                justify-content: center;
                margin-top: 0.25rem;
            }}
            .main-content {{
                padding: 7.5rem 1.5rem 5rem;
            }}
            .grid-4 {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .grid-3 {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .slide {{
                padding: 2rem 2rem;
                max-height: calc(100vh - 12rem);
            }}
            .title-main {{
                font-size: 2.6rem;
            }}
            .slide-title {{
                font-size: 1.8rem;
            }}
            .chart-box {{
                height: 320px;
            }}
        }}

        /* Mobile Devices (max-width: 768px) */
        @media (max-width: 768px) {{
            .navbar {{
                padding: 0.75rem 1rem;
            }}
            .logo-text {{
                font-size: 1rem !important;
            }}
            .nav-controls {{
                gap: 0.5rem;
            }}
            .btn {{
                padding: 0.4rem 0.8rem;
                font-size: 0.78rem;
            }}
            .slide-counter {{
                padding: 0.35rem 0.8rem;
                font-size: 0.78rem;
            }}
            .mode-btn {{
                padding: 0.4rem 0.85rem;
                font-size: 0.8rem;
            }}
            .main-content {{
                padding: 8.5rem 1rem 5.5rem;
            }}
            .grid-4, .grid-3, .grid-2 {{
                grid-template-columns: 1fr;
                gap: 1.25rem;
            }}
            .slide {{
                padding: 1.5rem 1.25rem;
                border-radius: 18px;
                max-height: calc(100vh - 13.5rem);
            }}
            .dashboard-container {{
                padding: 1.5rem 1.25rem;
                border-radius: 18px;
            }}
            .title-main {{
                font-size: 2rem;
                margin-bottom: 0.85rem;
            }}
            .slide-title {{
                font-size: 1.5rem;
            }}
            .slide-subtitle {{
                font-size: 0.9rem;
            }}
            .card {{
                padding: 1.25rem;
            }}
            .kpi-val {{
                font-size: 1.5rem;
            }}
            .chart-box {{
                height: 280px;
                padding: 1rem;
            }}
            .chart-title {{
                font-size: 0.88rem;
                flex-direction: column;
                align-items: flex-start;
                gap: 0.3rem;
            }}
            .filter-toolbar {{
                padding: 1rem;
                gap: 0.75rem;
                flex-direction: column;
                align-items: stretch;
            }}
            .filter-group {{
                flex-direction: column;
                align-items: stretch;
                gap: 0.35rem;
            }}
            .filter-select {{
                width: 100%;
            }}
            .quick-btn {{
                flex: 1 1 auto;
                text-align: center;
            }}
            .table-container {{
                padding: 1rem;
                overflow-x: auto;
                -webkit-overflow-scrolling: touch;
            }}
            .data-table {{
                min-width: 600px;
            }}
            .search-input {{
                width: 100%;
            }}
            .search-input:focus {{
                width: 100%;
            }}
            .footer-controls {{
                padding: 0.6rem 1rem;
                gap: 0.5rem;
            }}
            .slide-dots {{
                display: none;
            }}
            .footer-controls .btn {{
                flex: 1;
                justify-content: center;
                padding: 0.55rem 0.5rem;
                font-size: 0.82rem;
            }}
        }}

        /* Small Phones (max-width: 480px) */
        @media (max-width: 480px) {{
            .main-content {{
                padding: 9rem 0.75rem 5.5rem;
            }}
            .slide, .dashboard-container {{
                padding: 1.25rem 1rem;
                border-radius: 14px;
            }}
            .title-main {{
                font-size: 1.65rem;
            }}
            .slide-title {{
                font-size: 1.3rem;
            }}
            .kpi-card {{
                padding: 1rem;
            }}
            .logo-icon {{
                width: 30px;
                height: 30px;
                font-size: 0.95rem;
            }}
            .mode-btn span {{
                font-size: 0.75rem;
            }}
        }}
    </style>
</head>
<body>

    <!-- Top Luxury Navigation -->
    <nav class="navbar">
        <div class="logo">
            <div class="logo-icon"><i class="fa-solid fa-crown"></i></div>
            <div>
                <span class="logo-text" style="font-weight: 800; font-size: 1.15rem;">Global Superstore BI</span>
                <div style="font-size: 0.7rem; color: var(--gold); text-transform: uppercase; letter-spacing: 0.1em; font-weight: 700;">Executive Visual & BI Suite</div>
            </div>
        </div>

        <!-- Mode Switcher -->
        <div class="mode-switcher">
            <button class="mode-btn active" id="modeBtnSlide" onclick="switchMode('slide')">
                <i class="fa-solid fa-person-chalkboard"></i>
                <span>🎯 สไลด์ผู้บริหาร (7 Slides)</span>
            </button>
            <button class="mode-btn" id="modeBtnDash" onclick="switchMode('dash')">
                <i class="fa-solid fa-chart-pie"></i>
                <span>📊 Interactive Decision Dashboard</span>
            </button>
        </div>

        <div class="nav-controls">
            <button class="btn" onclick="toggleNotes()" title="แสดง/ซ่อน สคริปต์คำพูด">
                <i class="fa-solid fa-scroll"></i>
                <span>สคริปต์พูด</span>
            </button>
            <div class="slide-counter" id="slideCounter">Slide 1 / 7</div>
            <button class="btn btn-gold" onclick="toggleFullScreen()">
                <i class="fa-solid fa-expand"></i>
                <span>Full Screen</span>
            </button>
        </div>
    </nav>

    <!-- Main Content Container -->
    <main class="main-content">

        <!-- ========================================== -->
        <!-- MODE 1: EXECUTIVE SLIDES (VISUAL FIRST) -->
        <!-- ========================================== -->
        <div class="presentation-container" id="presentationContainer">

            <!-- SLIDE 1: Title & Hero Visual Stats -->
            <div class="slide active" id="slide-1">
                <div style="text-align: center; padding: 1.5rem 0;">
                    <div class="slide-tag" style="margin-bottom: 1.25rem;"><i class="fa-solid fa-award"></i> Executive Strategic Report & Visual BI</div>
                    <h1 class="title-main">ผ่ากลยุทธ์พลิกกำไร Global Superstore<br>เพื่อเติบโตอย่างยั่งยืนด้วย Data-Driven BI</h1>
                    <p class="slide-subtitle" style="max-width: 850px; margin: 0 auto 2.5rem;">
                        วิเคราะห์ความลับ "ยอดขายโต แต่กำไรถดถอย" ผ่าน Interactive Visuals และ Live BI Dashboard พร้อมแผนยุทธศาสตร์จัดพอร์ตโฟลิโอและนโยบายเพิ่มกำไรกว่า $500,000 ต่อปี
                    </p>

                    <!-- Interactive Visual Gauges / KPI Boxes -->
                    <div class="grid-4" style="max-width: 1100px; margin: 0 auto; text-align: left;">
                        <div class="card" style="border-left: 4px solid var(--gold); padding: 1.25rem;">
                            <div style="font-size: 0.78rem; color: var(--text-secondary); text-transform: uppercase;">ยอดขายสะสม 4 ปี</div>
                            <div style="font-size: 2.2rem; font-weight: 800; color: #fff; margin: 0.2rem 0;">$12.64M</div>
                            <div style="font-size: 0.78rem; color: var(--emerald-light);"><i class="fa-solid fa-arrow-up-right-dots"></i> เติบโต +90% ใน 4 ปี</div>
                        </div>
                        <div class="card" style="border-left: 4px solid var(--emerald); padding: 1.25rem;">
                            <div style="font-size: 0.78rem; color: var(--text-secondary); text-transform: uppercase;">กำไรสุทธิปัจจุบัน</div>
                            <div style="font-size: 2.2rem; font-weight: 800; color: #fff; margin: 0.2rem 0;">$1.47M</div>
                            <div style="font-size: 0.78rem; color: var(--emerald-light);">Profit Margin 11.61%</div>
                        </div>
                        <div class="card" style="border-left: 4px solid var(--rose); padding: 1.25rem; background: rgba(244, 63, 94, 0.05);">
                            <div style="font-size: 0.78rem; color: #fda4af; text-transform: uppercase;">จุดรั่วไหลส่วนลด & ค่าส่ง</div>
                            <div style="font-size: 2.2rem; font-weight: 800; color: #fda4af; margin: 0.2rem 0;">-$648K</div>
                            <div style="font-size: 0.78rem; color: #fca5a5;"><i class="fa-solid fa-triangle-exclamation"></i> 20% ของออเดอร์ขาดทุน</div>
                        </div>
                        <div class="card" style="border-left: 4px solid var(--indigo); padding: 1.25rem;">
                            <div style="font-size: 0.78rem; color: var(--text-secondary); text-transform: uppercase;">โอกาสดึงกำไรคืน</div>
                            <div style="font-size: 2.2rem; font-weight: 800; color: var(--indigo-light); margin: 0.2rem 0;">+$500K+</div>
                            <div style="font-size: 0.78rem; color: var(--indigo-light);"><i class="fa-solid fa-wand-magic-sparkles"></i> ทำได้ทันทีผ่านกฎเหล็ก</div>
                        </div>
                    </div>

                    <div style="margin-top: 2.5rem; display: flex; justify-content: center; gap: 1.25rem;">
                        <button class="btn btn-gold" style="padding: 0.85rem 2.2rem; font-size: 1.05rem;" onclick="changeSlide(1)">
                            <span>เริ่มดูรายงานสไลด์ (Start Presentation)</span>
                            <i class="fa-solid fa-arrow-right"></i>
                        </button>
                        <button class="btn" style="padding: 0.85rem 2rem; font-size: 1.05rem; border-color: var(--gold); color: var(--gold-light);" onclick="switchMode('dash')">
                            <i class="fa-solid fa-chart-pie"></i>
                            <span>เปิด Interactive BI Dashboard ทันที</span>
                        </button>
                    </div>
                </div>

                <div class="speaking-notes">
                    <div class="notes-header"><i class="fa-solid fa-microphone-lines"></i> สคริปต์พูด (Slide 1: บทนำ)</div>
                    <div class="notes-text">"สวัสดีครับคณะผู้บริหาร วันนี้เรานำเสนอในรูปแบบ Visual & Interactive BI เพื่อให้ทุกท่านเห็นภาพชัดเจนที่สุดครับ ยอดขาย 4 ปีเราโตถึง 12.6 ล้าน แต่วันนี้ทีม Data ได้ค้นพบรอยรั่วสำคัญ 6.4 แสนเหรียญ จากโปรโมชั่นส่วนลดและค่าขนส่ง ในสไลด์ชุดนี้เราจะใช้ภาพและข้อมูลโชว์วิธีดึงกำไร 5 แสนเหรียญคืนมา พร้อม Interactive Dashboard ที่ให้ทุกท่านทดลองกรองข้อมูลจริงประกอบการตัดสินใจในวันนี้ได้ทันทีครับ"</div>
                </div>
            </div>

            <!-- SLIDE 2: Visual Data Readiness & 6-Step Pipeline -->
            <div class="slide" id="slide-2">
                <div class="slide-header">
                    <div class="slide-tag"><i class="fa-solid fa-check-to-slot"></i> Data Quality & Readiness</div>
                    <h2 class="slide-title">ความพร้อมของข้อมูล: 6 ขั้นตอนทำความสะอาด (Data Cleaning Pipeline)</h2>
                    <p class="slide-subtitle">เปลี่ยนข้อมูลดิบที่มีปัญหา ให้เป็นข้อมูลสะอาด 51,290 รายการ พร้อม 15 ฟีเจอร์วิศวกรรมสำหรับ BI Decision</p>
                </div>

                <div class="grid-3" style="row-gap: 1.25rem;">
                    <div class="card" style="padding: 1.25rem;">
                        <div class="card-icon icon-emerald" style="margin-bottom: 0.5rem;"><i class="fa-solid fa-key"></i></div>
                        <h3 class="card-title" style="font-size: 1.05rem;">1. รหัสคำสั่งซื้อ (PK)</h3>
                        <p class="card-text" style="font-size: 0.85rem;">สร้าง <code>Global Order ID</code> ปลดล็อกออเดอร์ซ้ำซ้อนข้ามประเทศ 659 รายการ นับยอดขายแม่นยำ 100%</p>
                    </div>
                    <div class="card" style="padding: 1.25rem;">
                        <div class="card-icon icon-emerald" style="margin-bottom: 0.5rem;"><i class="fa-solid fa-map-pin"></i></div>
                        <h3 class="card-title" style="font-size: 1.05rem;">2. ไปรษณีย์ & Non-US</h3>
                        <p class="card-text" style="font-size: 0.85rem;">แก้ทศนิยม <code>.0</code> และเติมค่าว่าง 80% ในต่างประเทศด้วย <code>"Non-US"</code> ป้องกัน BI กราฟพัง</p>
                    </div>
                    <div class="card" style="padding: 1.25rem;">
                        <div class="card-icon icon-emerald" style="margin-bottom: 0.5rem;"><i class="fa-solid fa-broom"></i></div>
                        <h3 class="card-title" style="font-size: 1.05rem;">3. มาตรฐานชื่อสินค้า</h3>
                        <p class="card-text" style="font-size: 0.85rem;">ตัดช่องว่าง (Whitespaces) ปัญหาเดิมที่ทำให้ชื่อสินค้าและเมืองถูกแบ่งซ้ำซ้อนในรายงาน</p>
                    </div>
                    <div class="card" style="padding: 1.25rem;">
                        <div class="card-icon icon-indigo" style="margin-bottom: 0.5rem;"><i class="fa-solid fa-boxes-stacked"></i></div>
                        <h3 class="card-title" style="font-size: 1.05rem;">4. ติดตาม Split Shipment</h3>
                        <p class="card-text" style="font-size: 0.85rem;">สร้างป้ายกำกับ <code>Is Split Shipment Item</code> เพื่อตรวจสอบออเดอร์ที่ทยอยส่งแยกกล่องและต้นทุนซ้ำซ้อน</p>
                    </div>
                    <div class="card" style="padding: 1.25rem;">
                        <div class="card-icon icon-indigo" style="margin-bottom: 0.5rem;"><i class="fa-solid fa-calendar-check"></i></div>
                        <h3 class="card-title" style="font-size: 1.05rem;">5. มิติเวลา & SLA Delay</h3>
                        <p class="card-text" style="font-size: 0.85rem;">สร้างมิติเวลา Year-Month, Quarter พร้อมคำนวณ <code>Shipping Delay (Days)</code> วัดประสิทธิภาพจัดส่ง</p>
                    </div>
                    <div class="card" style="padding: 1.25rem; border-color: var(--gold); background: rgba(245, 158, 11, 0.04);">
                        <div class="card-icon icon-gold" style="margin-bottom: 0.5rem;"><i class="fa-solid fa-triangle-exclamation"></i></div>
                        <h3 class="card-title" style="font-size: 1.05rem; color: var(--gold-light);">6. ระบบเตือนภัยความเสี่ยง</h3>
                        <p class="card-text" style="font-size: 0.85rem;">จัดกลุ่ม Tiering และสร้าง Red Flag <code>Is Shipping Cost Draining Profit</code> เพื่อกรองออเดอร์กินกำไรใน Dashboard</p>
                    </div>
                </div>

                <div style="margin-top: 1.25rem; background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 0.85rem 1.25rem; display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 0.88rem; color: #cbd5e1;">
                        <i class="fa-solid fa-circle-check" style="color: var(--emerald-light); font-size: 1.1rem; margin-right: 0.5rem;"></i>
                        ผลลัพธ์: บันทึกลงไฟล์ <strong><code>Global_Superstore_Cleaned_2.csv</code></strong> (39 คอลัมน์) เข้ารหัส <code>utf-8-sig</code> สมบูรณ์ 100%
                    </div>
                    <span class="badge-pill badge-success">Data Ready for Executive BI</span>
                </div>

                <div class="speaking-notes">
                    <div class="notes-header"><i class="fa-solid fa-microphone-lines"></i> สคริปต์พูด (Slide 2: ความพร้อมข้อมูล)</div>
                    <div class="notes-text">"ก่อนจะตัดสินใจกลยุทธ์ เราได้ล้างข้อผิดพลาดในข้อมูลดิบครบทั้ง 6 ขั้นตอนจนได้ไฟล์ Cleaned.csv ที่สะอาด 100% ครับ โดยหัวใจสำคัญคือขั้นตอนที่ 6 เราได้สร้างคอลัมน์ระบบเตือนภัยความเสี่ยง (Risk Alerting) ฝังไว้ในข้อมูล ทำให้ในสไลด์ต่อๆ ไป และใน Interactive Dashboard ผู้บริหารจะสามารถกดกรองหาจุดรั่วไหลทางการเงินได้ทันทีภายในคลิกเดียวครับ"</div>
                </div>
            </div>

            <!-- SLIDE 3: Why Sales Up, Profit Down? (Interactive Chart) -->
            <div class="slide" id="slide-3">
                <div class="slide-header">
                    <div class="slide-tag" style="color: #fda4af; background: rgba(244, 63, 94, 0.12); border-color: rgba(244, 63, 94, 0.35);"><i class="fa-solid fa-chart-line-down"></i> Strategic Problem Analysis</div>
                    <h2 class="slide-title">ไขข้อข้องใจ: ทำไม "ยอดขายโต แต่กำไรกลับถดถอย?"</h2>
                    <p class="slide-subtitle">กราฟแสดงความสัมพันธ์ 4 ปี (2011-2014): เมื่อยอดขายพุ่งสูงขึ้น แต่เส้นอัตรากำไร (Profit Margin %) เริ่มหดตัวลงจาก 11.95% เหลือ 11.73%</p>
                </div>

                <div class="grid-2" style="grid-template-columns: 1.3fr 0.7fr; align-items: center;">
                    <div class="chart-box" style="height: 380px;">
                        <div class="chart-title">
                            <span>📈 กราฟความขัดแย้ง: ยอดขายรวม ($) vs Profit Margin (%) รายปี</span>
                            <span style="font-size: 0.75rem; color: var(--gold-light);">*เอาเมาส์ชี้เพื่อดูข้อมูลจริง</span>
                        </div>
                        <canvas id="chartYearlyTrend"></canvas>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 1rem;">
                        <div class="card" style="border-left: 4px solid var(--rose); padding: 1.25rem;">
                            <h3 class="card-title" style="color: #fda4af; font-size: 1.05rem;"><i class="fa-solid fa-magnifying-glass-chart"></i> ต้นตอของปัญหา (Root Causes)</h3>
                            <p class="card-text" style="font-size: 0.85rem;">
                                ในปี 2014 ยอดขายโตขึ้นถึง <strong>+26%</strong> แต่อัตราทำกำไรกลับตกลง เพราะมีออเดอร์ถึง <strong>20% ขององค์กร</strong> ที่ตกอยู่ในสภาวะ "ยิ่งขายยิ่งขาดทุน" จาก 2 ปัจจัยลับ:
                            </p>
                        </div>

                        <div class="card" style="border-left: 4px solid var(--gold); padding: 1.25rem; background: rgba(245, 158, 11, 0.05);">
                            <div style="font-weight: 700; color: #fff; font-size: 0.95rem; margin-bottom: 0.3rem;">🔥 1. กับดักส่วนลดมรณะ (> 20%):</div>
                            <p class="card-text" style="font-size: 0.82rem;">เซลส์ใช้โปรโมชั่นลดราคา 30-80% เพื่อปั๊ม Sales Volume ทำให้กำไรติดลบระนาว</p>
                            
                            <div style="font-weight: 700; color: #fff; font-size: 0.95rem; margin-top: 0.75rem; margin-bottom: 0.3rem;">🚢 2. ค่าจัดส่ง Express กินกำไร:</div>
                            <p class="card-text" style="font-size: 0.82rem; margin-bottom: 0;">ออเดอร์ส่งด่วนข้ามทวีป 634 รายการ ค่าส่งแพงกว่ากำไรขั้นต้นของสินค้า</p>
                        </div>
                    </div>
                </div>

                <div class="speaking-notes">
                    <div class="notes-header"><i class="fa-solid fa-microphone-lines"></i> สคริปต์พูด (Slide 3: ยอดขายโตแต่กำไรลด)</div>
                    <div class="notes-text">"ทุกท่านดูที่กราฟ Interactive บนจอครับ แท่งสีฟ้าคือยอดขายของเราที่เติบโตขึ้นทุกปีจนทะลุ 4.3 ล้านเหรียญในปี 2014 แต่เมื่อดูเส้นสีทองที่เป็น Profit Margin จะเห็นว่าปี 2013 เราทำได้เกือบ 12% แต่ปี 2014 เส้นนี้ดิ่งหัวลงครับ เพราะอะไร? ข้อมูลชี้ชัดว่าปี 2014 เรามีออเดอร์ที่ 'ยิ่งขายยิ่งเจ็บตัว' เพิ่มขึ้นอย่างมีนัยสำคัญ จากการจัดโปรโมชั่นส่วนลดที่ลึกเกินไปและค่าขนส่งที่ควบคุมไม่ได้ครับ"</div>
                </div>
            </div>

            <!-- SLIDE 4: Root Cause 1 - Discount Trap (Interactive Chart) -->
            <div class="slide" id="slide-4">
                <div class="slide-header">
                    <div class="slide-tag" style="color: var(--gold-light); background: rgba(245, 158, 11, 0.12); border-color: rgba(245, 158, 11, 0.35);"><i class="fa-solid fa-tags"></i> Root Cause #1: Discount Policy Failure</div>
                    <h2 class="slide-title">เปิดโปงปัจจัยที่ 1: "กับดักส่วนลดมรณะ (The Death Discount Trap)"</h2>
                    <p class="slide-subtitle">สถิติยืนยัน: จุดคุ้มทุนอยู่ที่ไม่เกิน 20% ทันทีที่ให้ส่วนลดตั้งแต่ 21% ขึ้นไป อัตรากำไรสุทธิจะติดลบทันที (เฉลี่ย -42%)</p>
                </div>

                <div class="grid-2" style="grid-template-columns: 1.2fr 0.8fr; align-items: center;">
                    <div class="chart-box" style="height: 380px;">
                        <div class="chart-title">
                            <span>📊 อัตรากำไร (Profit Margin %) แบ่งตามระดับส่วนลด</span>
                            <span style="font-size: 0.75rem; color: #fda4af;">*ส่วนลด > 20% คือโซนขาดทุน</span>
                        </div>
                        <canvas id="chartDiscountTiers"></canvas>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.85rem;">
                        <div class="card" style="border-left: 4px solid var(--rose); padding: 1.1rem; background: rgba(244, 63, 94, 0.05);">
                            <div style="color: #fda4af; font-weight: 700; font-size: 0.9rem;"><i class="fa-solid fa-triangle-exclamation"></i> ความเสียหายจากโปรลดแหลก (> 30%):</div>
                            <div style="font-size: 1.5rem; font-weight: 800; color: #fff; margin: 0.2rem 0;">-$793,526</div>
                            <p class="card-text" style="font-size: 0.8rem; margin-bottom: 0;">จากออเดอร์ 10,361 รายการ (20% ขององค์กร) ที่ได้ส่วนลด 31-80% ดึงกำไรทั้งบริษัทลดลงอย่างหนัก!</p>
                        </div>

                        <div class="card" style="border-left: 4px solid var(--gold); padding: 1.1rem;">
                            <div style="color: var(--gold-light); font-weight: 700; font-size: 0.9rem;"><i class="fa-solid fa-box"></i> กรณีศึกษา: โต๊ะทำงาน (Tables) ปี 2014</div>
                            <p class="card-text" style="font-size: 0.8rem; margin-bottom: 0.2rem;">ยอดขายโตขึ้นเป็น <strong>$243K (+20%)</strong> แต่ขาดทุนหนักขึ้น 2 เท่าเป็น <strong style="color:#fda4af;">-$30,545</strong> เพราะลดราคาเฉลี่ยถึง 29.1%</p>
                        </div>

                        <div class="card" style="border-left: 4px solid var(--indigo); padding: 1.1rem;">
                            <div style="color: var(--indigo-light); font-weight: 700; font-size: 0.9rem;"><i class="fa-solid fa-earth-americas"></i> กรณีศึกษา: New Zealand & Thailand</div>
                            <p class="card-text" style="font-size: 0.8rem; margin-bottom: 0;">ปี 2014 นิวซีแลนด์ยอดขายโต +6% แต่เพราะ <strong>เพิ่มส่วนลดเป็น 25.3%</strong> กำไรจึงพลิกติดลบ <strong>-$504</strong> ส่วนไทยลด 35.6% ขาดทุน <strong>-$5,389</strong></p>
                        </div>
                    </div>
                </div>

                <div class="speaking-notes">
                    <div class="notes-header"><i class="fa-solid fa-microphone-lines"></i> สคริปต์พูด (Slide 4: กับดักส่วนลด)</div>
                    <div class="notes-text">"ดูกราฟแท่งสีแดงในจอครับ นี่คือหลักฐานที่ชัดเจนที่สุด เมื่อเราให้ส่วนลด 0-20% แท่งกำไรเป็นสีเขียวงดงาม แต่ทันทีที่ให้ส่วนลด 21% ขึ้นไป แท่งกราฟทิ่มลงดินติดลบทันที! โดยออเดอร์ที่ลดเกิน 30% สร้างผลขาดทุนรวมกันเกือบ 8 แสนเหรียญ นี่คือเหตุผลที่สินค้าอย่างโต๊ะทำงาน หรือตลาดนิวซีแลนด์และไทย ยอดขายโตแต่กำไรจริงกลับติดลบครับ"</div>
                </div>
            </div>

            <!-- SLIDE 5: Root Cause 2 - Shipping Drain (Interactive Donut & Preview Table) -->
            <div class="slide" id="slide-5">
                <div class="slide-header">
                    <div class="slide-tag" style="color: var(--cyan); background: rgba(6, 182, 212, 0.12); border-color: rgba(6, 182, 212, 0.35);"><i class="fa-solid fa-truck-fast"></i> Root Cause #2: Logistics Cost Outliers</div>
                    <h2 class="slide-title">เปิดโปงปัจจัยที่ 2: "วิกฤตค่าจัดส่งสุดขั้วกัดกินกำไร"</h2>
                    <p class="slide-subtitle">ค้นพบออเดอร์ส่งด่วนข้ามทวีป 634 รายการ ที่ค่าจัดส่งแพงกว่ากำไรขั้นต้นของสินค้า เปลี่ยนกำไรเป็นขาดทุน</p>
                </div>

                <div class="grid-2" style="grid-template-columns: 0.9fr 1.1fr; align-items: center;">
                    <div class="chart-box" style="height: 380px; display: flex; flex-direction: column; justify-content: center; align-items: center;">
                        <div class="chart-title" style="width: 100%;"><span>🚢 สัดส่วนกลุ่มค่าจัดส่ง Outliers</span></div>
                        <div style="width: 250px; height: 250px;"><canvas id="chartShippingDonut"></canvas></div>
                        <div style="font-size: 0.8rem; color: #cbd5e1; margin-top: 0.75rem; text-align: center;">
                            ออเดอร์ขาดทุนจากค่าส่ง (Red Drain) สูญเสียรวม <strong style="color:#fda4af;">-$236,784</strong>
                        </div>
                    </div>

                    <div style="display: flex; flex-direction: column; gap: 0.85rem;">
                        <div class="card" style="border-left: 4px solid var(--cyan); padding: 1.1rem;">
                            <h3 class="card-title" style="color: var(--cyan); font-size: 1rem;"><i class="fa-solid fa-shield-halved"></i> การแก้ปัญหา: ระบบเตือนภัย Is Shipping Cost Draining Profit</h3>
                            <p class="card-text" style="font-size: 0.82rem; margin-bottom: 0;">ตามหลัก 4-Mantra เราห้ามลบ 634 ออเดอร์นี้เพราะเป็นรายจ่ายจริง เราจึงสร้างป้ายเตือนภัย <code>True/False</code> ฝังใน Data เพื่อให้ฝ่าย Operation กรองตรวจสอบได้ทันทีใน Dashboard ด้านล่างนี้:</p>
                        </div>

                        <!-- Mini Preview Table -->
                        <div style="background: rgba(0,0,0,0.4); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 0.85rem; max-height: 200px; overflow-y: auto;">
                            <div style="font-size: 0.78rem; font-weight: 700; color: #fda4af; margin-bottom: 0.5rem;"><i class="fa-solid fa-list-check"></i> ตัวอย่างออเดอร์จริงที่ค่าส่งกินกำไร (Preview from Cleaned Data):</div>
                            <table class="data-table" style="font-size: 0.75rem;">
                                <thead>
                                    <tr>
                                        <th>Order ID</th>
                                        <th>ประเทศ</th>
                                        <th>Ship Mode</th>
                                        <th>ค่าส่ง ($)</th>
                                        <th>กำไร ($)</th>
                                    </tr>
                                </thead>
                                <tbody id="previewDrainTable">
                                    <!-- Populated by JS -->
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>

                <div class="speaking-notes">
                    <div class="notes-header"><i class="fa-solid fa-microphone-lines"></i> สคริปต์พูด (Slide 5: วิกฤตค่าขนส่ง)</div>
                    <div class="notes-text">"นอกจากเรื่องส่วนลดแล้ว ในกราฟโดนัทเราพบว่ามีออเดอร์ 6.7% ที่ค่าส่งแพงผิดปกติ และมีถึง 634 ออเดอร์ที่ค่าส่งแพงกว่ากำไรสินค้า ทำเราสูญเงินไป 2.36 แสนเหรียญ! ลองดูตัวอย่างในตารางจริงด้านขวาครับ เช่น ออเดอร์ส่งไปต่างประเทศด้วย First Class หรือ Same Day ค่าส่งหลักร้อยแต่กำไรติดลบ วิธีแก้คือเราสร้างระบบเตือนภัยให้ฝ่ายโลจิสติกส์เปิดตารางนี้ใน BI Dashboard และระงับการส่งด่วนที่ขาดทุนทันทีครับ"</div>
                </div>
            </div>

            <!-- SLIDE 6: Strategic Portfolio Matrix (Visual Winners vs Losers) -->
            <div class="slide" id="slide-6">
                <div class="slide-header">
                    <div class="slide-tag" style="color: var(--emerald-light); background: rgba(16, 185, 129, 0.12); border-color: rgba(16, 185, 129, 0.35);"><i class="fa-solid fa-compass"></i> Strategic Portfolio Matrix</div>
                    <h2 class="slide-title">ผ่าแผนกลยุทธ์: "ควรขายสินค้าอะไร? ที่ไหน? ให้ใคร?"</h2>
                    <p class="slide-subtitle">จัดทัพธุรกิจใหม่ แยกกลุ่ม "ทัพหน้าทำกำไร (Star Winners)" ออกจาก "หลุมดำดูดกำไร (Bleeding Assets)"</p>
                </div>

                <div class="grid-3" style="row-gap: 1.5rem;">
                    <div class="card" style="border-top: 4px solid var(--emerald); padding: 1.25rem;">
                        <div class="card-icon icon-emerald" style="margin-bottom: 0.6rem;"><i class="fa-solid fa-box-open"></i></div>
                        <h3 class="card-title" style="color: var(--emerald-light); font-size: 1.05rem;">1. ขายอะไร? (What to Sell)</h3>
                        <div style="font-size: 0.82rem; margin-bottom: 0.6rem;">
                            <div style="color: #fff; font-weight: 700;">🌟 ทัพหน้าทำกำไร (Focus):</div>
                            <div style="color: var(--emerald-light); font-weight: 800; font-size: 1rem; margin-top: 0.2rem;">Copiers & Phones</div>
                            <div style="color: var(--text-secondary);">กำไรอันดับ #1 $258K / $217K (Margin 13-17%)</div>
                        </div>
                        <div style="background: rgba(244, 63, 94, 0.1); padding: 0.6rem; border-radius: 8px; font-size: 0.78rem;">
                            <span style="color: #fda4af; font-weight: 700;">🛑 หลุมดำ:</span> <strong>Tables (โต๊ะทำงาน)</strong> ขาดทุนสะสม <strong>-$64,083</strong> ต้องปรับโครงสร้างราคาด่วน
                        </div>
                    </div>

                    <div class="card" style="border-top: 4px solid var(--gold); padding: 1.25rem;">
                        <div class="card-icon icon-gold" style="margin-bottom: 0.6rem;"><i class="fa-solid fa-earth-americas"></i></div>
                        <h3 class="card-title" style="color: var(--gold-light); font-size: 1.05rem;">2. ขายที่ไหน? (Where to Sell)</h3>
                        <div style="font-size: 0.82rem; margin-bottom: 0.6rem;">
                            <div style="color: #fff; font-weight: 700;">🏆 ตลาดทองคำ (Scale Up):</div>
                            <div style="color: var(--gold-light); font-weight: 800; font-size: 1rem; margin-top: 0.2rem;">USA, China & India</div>
                            <div style="color: var(--text-secondary);">จีน & อินเดีย Margin สูงถึง <strong>21.9%</strong> เพราะแทบไม่ลดราคาเลย!</div>
                        </div>
                        <div style="background: rgba(244, 63, 94, 0.1); padding: 0.6rem; border-radius: 8px; font-size: 0.78rem;">
                            <span style="color: #fda4af; font-weight: 700;">🛑 หลุมดำ:</span> <strong>Turkey (-$98K)</strong> ลด 60% ทุกชิ้น, <strong>Nigeria (-$80K)</strong> ลด 70%, <strong>Netherlands (-$41K)</strong>
                        </div>
                    </div>

                    <div class="card" style="border-top: 4px solid var(--purple); padding: 1.25rem;">
                        <div class="card-icon icon-purple" style="margin-bottom: 0.6rem;"><i class="fa-solid fa-users"></i></div>
                        <h3 class="card-title" style="color: #d8b4fe; font-size: 1.05rem;">3. ขายให้ใคร? (To Whom)</h3>
                        <div style="font-size: 0.82rem; margin-bottom: 0.6rem;">
                            <div style="color: #fff; font-weight: 700;">🎯 ลูกค้ากำไรสูง (Prioritize):</div>
                            <div style="color: #d8b4fe; font-weight: 800; font-size: 1rem; margin-top: 0.2rem;">Home Office & Corporate</div>
                            <div style="color: var(--text-secondary);">Home Office ให้ Margin สูงสุด <strong>11.99% ($277K)</strong> ขอส่วนลดน้อยที่สุด</div>
                        </div>
                        <div style="background: rgba(168, 85, 247, 0.1); padding: 0.6rem; border-radius: 8px; font-size: 0.78rem;">
                            <span style="color: #d8b4fe; font-weight: 700;">💡 กลยุทธ์:</span> ผลักดันสินค้า Technology ราคาสูงให้ 2 กลุ่มนี้ที่พร้อมจ่ายโดยไม่เน้นโปรลดแหลก
                        </div>
                    </div>
                </div>

                <div class="speaking-notes">
                    <div class="notes-header"><i class="fa-solid fa-microphone-lines"></i> สคริปต์พูด (Slide 6: กลยุทธ์พอร์ตโฟลิโอ)</div>
                    <div class="notes-text">"เมื่อเรารู้ปัญหาแล้ว นี่คือแผนปรับทัพครับ 1. ขายอะไร: อัดงบดัน Copiers และ Phones ที่กำไรดีสุด ส่วน Tables ต้องปรับแบบแผน 2. ขายที่ไหน: ตลาดทองคำเราคือ อเมริกา จีน และอินเดียครับ โดยเฉพาะจีนและอินเดีย Margin สูง 22% เพราะแทบไม่ลดราคาเลย ส่วนตุรกี ไนจีเรีย เนเธอร์แลนด์ ที่ขาดทุนรวม 2.2 แสนเหรียญต้องใช้กฎเหล็กทันที และ 3. ขายให้ใคร: โฟกัสลูกค้า Home Office และ Corporate ที่มีกำลังซื้อสูงและไม่อ่อนไหวต่อส่วนลดครับ"</div>
                </div>
            </div>

            <!-- SLIDE 7: 3 Immediate Actionable Policies (Visual Cards) -->
            <div class="slide" id="slide-7">
                <div class="slide-header">
                    <div class="slide-tag" style="color: var(--gold-light); background: rgba(245, 158, 11, 0.12); border-color: rgba(245, 158, 11, 0.35);"><i class="fa-solid fa-wand-magic-sparkles"></i> Executive Action Plan</div>
                    <h2 class="slide-title">3 นโยบายสั่งการเพิ่มกำไรอย่างเป็นรูปธรรม (Immediate Impact)</h2>
                    <p class="slide-subtitle">ข้อเสนอแนะเชิงกลยุทธ์ที่สามารถออกประกาศและสั่งการผ่านระบบ BI ได้ทันที เพื่อดึงกำไรกลับคืนมากว่า $500,000 ต่อปี</p>
                </div>

                <div class="grid-3" style="row-gap: 1.5rem;">
                    <div class="card" style="border-left: 4px solid var(--gold); padding: 1.35rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="background: var(--gold); color: #000; font-weight: 800; padding: 0.25rem 0.7rem; border-radius: 8px;">นโยบายที่ 1</span>
                            <span class="badge-pill badge-gold">+$500K+/Year</span>
                        </div>
                        <h3 class="card-title" style="color: var(--gold-light); font-size: 1.1rem;">ตั้งเพดานส่วนลดเหล็กไม่เกิน 20%</h3>
                        <p class="card-text" style="font-size: 0.85rem;">
                            ห้ามระบบให้ส่วนลดเกิน <strong>20% (Hard Cap)</strong> เพราะจากข้อมูลจริง <strong>20% คือ "จุดเปลี่ยนมรณะ (Tipping Point)"</strong>: กลุ่มลด ≤ 20% สร้างกำไรสูงถึง <strong>+$2.28M (Win Rate 92.5%)</strong> แต่หากลดเกิน 20% เมื่อไหร่ ระบบจะขาดทุนทันที (Win Rate ดิ่งเหลือเพียง 0% - 22.8%)
                        </p>
                        <div style="font-size: 0.78rem; color: #fde047; background: rgba(245, 158, 11, 0.1); padding: 0.5rem; border-radius: 8px; margin-top: 0.75rem; font-weight: 700;">
                            💰 ผลลัพธ์: ล็อกระบบไม่ให้ข้ามเส้น 20% เซฟเงินที่รั่วไหลกลับมาได้ทันทีกว่าปีละครึ่งล้านเหรียญ!
                        </div>
                    </div>

                    <div class="card" style="border-left: 4px solid var(--rose); padding: 1.35rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="background: var(--rose); color: #fff; font-weight: 800; padding: 0.25rem 0.7rem; border-radius: 8px;">นโยบายที่ 2</span>
                            <span class="badge-pill badge-danger">Stop Loss: -$64K</span>
                        </div>
                        <h3 class="card-title" style="color: #fda4af; font-size: 1.1rem;">ปฏิรูปโมเดลขายโต๊ะ (Bundle Selling)</h3>
                        <p class="card-text" style="font-size: 0.85rem;">
                            ยกเลิกการขายโต๊ะทำงานเดี่ยวแบบลดราคา 29% แต่เปลี่ยนเป็นบังคับขายแบบ <strong>Bundle Package</strong> คู่กับเก้าอี้หรือตู้หนังสือที่กำไรสูง
                        </p>
                        <div style="font-size: 0.78rem; color: #fda4af; background: rgba(244, 63, 94, 0.1); padding: 0.5rem; border-radius: 8px; margin-top: 0.75rem; font-weight: 700;">
                            📦 ผลลัพธ์: ถัวเฉลี่ยให้ Margin รวมของแพ็กเกจเป็นบวก หยุดขาดทุนสะสม -$64,083 ทันที!
                        </div>
                    </div>

                    <div class="card" style="border-left: 4px solid var(--emerald); padding: 1.35rem;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                            <span style="background: var(--emerald); color: #fff; font-weight: 800; padding: 0.25rem 0.7rem; border-radius: 8px;">นโยบายที่ 3</span>
                            <span class="badge-pill badge-success">Save: +$236K/Year</span>
                        </div>
                        <h3 class="card-title" style="color: var(--emerald-light); font-size: 1.1rem;">คุมเข้มส่งด่วน Express & ข้ามทวีป</h3>
                        <p class="card-text" style="font-size: 0.85rem;">
                            กำหนดเกณฑ์ <strong>Minimum Order Value (ยอดสั่งซื้อขั้นต่ำ)</strong> สำหรับส่ง Same Day / First Class หากไม่ถึงเกณฑ์ต้องส่งแบบ Standard
                        </p>
                        <div style="font-size: 0.78rem; color: var(--emerald-light); background: rgba(16, 185, 129, 0.1); padding: 0.5rem; border-radius: 8px; margin-top: 0.75rem; font-weight: 700;">
                            🚚 ผลลัพธ์: ระงับจุดรั่วไหลจาก 634 ออเดอร์อันตราย เซฟเงินคืนได้ $236,784 ต่อปี!
                        </div>
                    </div>
                </div>

                <div style="margin-top: 2rem; text-align: center;">
                    <button class="btn btn-gold" style="margin: 0 auto; padding: 0.85rem 2.5rem; font-size: 1.05rem;" onclick="switchMode('dash')">
                        <i class="fa-solid fa-chart-pie"></i>
                        <span>เปิดระบบ Interactive BI Dashboard เพื่อทดสอบกรองข้อมูลจริง</span>
                    </button>
                </div>

                <div class="speaking-notes">
                    <div class="notes-header"><i class="fa-solid fa-microphone-lines"></i> สคริปต์พูด (Slide 7: 3 นโยบายเพิ่มกำไร)</div>
                    <div class="notes-text">"นี่คือ 3 ข้อเสนอแนะที่ทำได้จริงทันทีในวันนี้ครับ 1. กฎเหล็กส่วนลด 20% ห้ามลดเกินนี้เด็ดขาด 2. เปลี่ยนโมเดลขายโต๊ะจากการลดราคา มาเป็นระบบ Bundle ซื้อโต๊ะต้องพ่วงเก้าอี้ และ 3. คุมเข้มค่าส่ง Express ข้ามประเทศ ต้องมียอดสั่งซื้อขั้นต่ำถึงเกณฑ์ ตอนนี้ผมขอเชิญทุกท่านกดสลับโหมดไปที่ Interactive BI Dashboard บนจอ เพื่อดูข้อมูลจริงที่สนับสนุน 3 นโยบายนี้ด้วยกันครับ"</div>
                </div>
            </div>

        </div> <!-- End Presentation Container -->


        <!-- ========================================== -->
        <!-- MODE 2: INTERACTIVE BI DECISION DASHBOARD -->
        <!-- ========================================== -->
        <div class="dashboard-container" id="dashboardContainer">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.25rem;">
                <div>
                    <div class="slide-tag" style="margin-bottom: 0.4rem;"><i class="fa-solid fa-layer-group"></i> Executive Decision Support BI</div>
                    <h2 class="slide-title" style="font-size: 1.85rem; margin-bottom: 0.2rem;">ระบบตัดสินใจและจำลองกลยุทธ์ (Interactive BI Dashboard)</h2>
                    <p class="slide-subtitle" style="font-size: 0.95rem;">เลือกตัวกรองด้านล่างเพื่อแสดงข้อมูลจริงที่สนับสนุนการตัดสินใจ หรือคลิกปุ่มกรองด่วนเพื่อตรวจจับจุดรั่วไหล</p>
                </div>
                <div style="display: flex; gap: 0.75rem;">
                    <button class="btn" style="border-color: var(--gold); color: var(--gold-light);" onclick="resetFilters()">
                        <i class="fa-solid fa-rotate-left"></i> รีเซ็ตตัวกรอง
                    </button>
                    <button class="btn btn-gold" onclick="switchMode('slide')">
                        <i class="fa-solid fa-arrow-left"></i> กลับไปสไลด์นำเสนอ
                    </button>
                </div>
            </div>

            <!-- Interactive Toolbar -->
            <div class="filter-toolbar">
                <div class="filter-group">
                    <span class="filter-label"><i class="fa-solid fa-calendar"></i> ปีคำสั่งซื้อ:</span>
                    <select class="filter-select" id="filterYear" onchange="applyDashboardFilters()">
                        <option value="all">ทั้งหมด (2011 - 2014)</option>
                        <option value="2011">2011</option>
                        <option value="2012">2012</option>
                        <option value="2013">2013</option>
                        <option value="2014">2014</option>
                    </select>
                </div>

                <div class="filter-group">
                    <span class="filter-label"><i class="fa-solid fa-globe"></i> ตลาด (Market):</span>
                    <select class="filter-select" id="filterMarket" onchange="applyDashboardFilters()">
                        <option value="all">ทุกตลาดทั่วโลก (All Markets)</option>
                        <option value="US">US (สหรัฐอเมริกา)</option>
                        <option value="APAC">APAC (เอเชียแปซิฟิก)</option>
                        <option value="EU">EU (ยุโรป)</option>
                        <option value="EMEA">EMEA (ตะวันออกกลาง & ตุรกี)</option>
                        <option value="Africa">Africa (แอฟริกา & ไนจีเรีย)</option>
                        <option value="LATAM">LATAM (ละตินอเมริกา)</option>
                    </select>
                </div>

                <div class="filter-group">
                    <span class="filter-label"><i class="fa-solid fa-folder-tree"></i> หมวดสินค้า:</span>
                    <select class="filter-select" id="filterCategory" onchange="applyDashboardFilters()">
                        <option value="all">ทุกหมวดสินค้า (All Categories)</option>
                        <option value="Technology">Technology (เทคโนโลยี)</option>
                        <option value="Furniture">Furniture (เฟอร์นิเจอร์)</option>
                        <option value="Office Supplies">Office Supplies (อุปกรณ์สำนักงาน)</option>
                    </select>
                </div>

                <div style="height: 24px; width: 1px; background: rgba(255,255,255,0.15); margin: 0 0.5rem;"></div>

                <!-- Quick Buttons -->
                <div style="display: flex; gap: 0.5rem; flex-wrap: wrap;">
                    <button class="quick-btn active" id="btnQuickAll" onclick="setQuickFilter('all')">👑 ภาพรวมทั้งหมด</button>
                    <button class="quick-btn" id="btnQuickWinners" onclick="setQuickFilter('winners')" style="color: var(--emerald-light);">🌟 สินค้าทำกำไรสูงสุด</button>
                    <button class="quick-btn" id="btnQuickDisc" onclick="setQuickFilter('disc')" style="color: var(--gold-light);">🚨 กลุ่มส่วนลดมรณะ (>20%)</button>
                    <button class="quick-btn" id="btnQuickDrain" onclick="setQuickFilter('drain')" style="color: #fda4af;">🚢 กลุ่มค่าจัดส่งกินกำไร (Drain)</button>
                </div>
            </div>

            <!-- Dynamic Live KPI Cards -->
            <div class="grid-4" style="margin-bottom: 1.5rem;">
                <div class="kpi-card" style="border-top: 3px solid var(--gold);">
                    <div class="kpi-label">ยอดขายที่กรองได้ (Filtered Sales)</div>
                    <div class="kpi-val" id="kpiSales">$0.00M</div>
                    <div class="kpi-sub" id="kpiOrders"><i class="fa-solid fa-cart-shopping"></i> 0 คำสั่งซื้อ</div>
                </div>
                <div class="kpi-card" style="border-top: 3px solid var(--emerald);">
                    <div class="kpi-label">กำไรสุทธิ (Filtered Profit)</div>
                    <div class="kpi-val" id="kpiProfit" style="color: var(--emerald-light);">$0.00M</div>
                    <div class="kpi-sub" style="color: var(--text-secondary);">ผลรวมกำไรตามเงื่อนไข</div>
                </div>
                <div class="kpi-card" style="border-top: 3px solid var(--cyan);">
                    <div class="kpi-label">อัตราทำกำไร (Profit Margin %)</div>
                    <div class="kpi-val" id="kpiMargin">0.00%</div>
                    <div class="kpi-sub" id="kpiMarginSub" style="color: var(--cyan);"><i class="fa-solid fa-chart-line"></i> ประสิทธิภาพทำกำไร</div>
                </div>
                <div class="kpi-card" style="border-top: 3px solid var(--rose); background: rgba(244, 63, 94, 0.04);">
                    <div class="kpi-label" style="color: #fda4af;">ยอดสูญเสียที่ต้องตรวจสอบ (Drain / Loss)</div>
                    <div class="kpi-val" id="kpiLoss" style="color: #fda4af;">-$0.00K</div>
                    <div class="kpi-sub" style="color: #fca5a5;"><i class="fa-solid fa-circle-exclamation"></i> รายการที่กำไรติดลบ</div>
                </div>
            </div>

            <!-- Dynamic Chart Grid -->
            <div class="grid-2" style="margin-bottom: 1.5rem;">
                <div class="chart-box">
                    <div class="chart-title">
                        <span>📦 กำไรแยกตาม Sub-Category (เรียงจากมากไปน้อย)</span>
                        <span style="font-size: 0.75rem; color: var(--emerald-light);">*เขียว=กำไร / แดง=ขาดทุน</span>
                    </div>
                    <canvas id="chartDashSubcat"></canvas>
                </div>

                <div class="chart-box">
                    <div class="chart-title">
                        <span>🌍 ผลการดำเนินงานแยกตามประเทศ (Top 7 Winners & Losers)</span>
                        <span style="font-size: 0.75rem; color: var(--gold-light);">*เปรียบเทียบตลาดทองคำ vs หลุมดำ</span>
                    </div>
                    <canvas id="chartDashCountry"></canvas>
                </div>
            </div>

            <!-- Interactive Decision Table -->
            <div class="table-container">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem; flex-wrap: wrap; gap: 1rem;">
                    <div style="font-size: 0.95rem; font-weight: 700; color: #fff; display: flex; align-items: center; gap: 0.5rem;">
                        <i class="fa-solid fa-table-list" style="color: var(--gold);"></i>
                        <span id="tableName">ตารางแสดงข้อมูลจริงที่สนับสนุนการตัดสินใจ (Active Records)</span>
                    </div>
                    <div>
                        <input type="text" class="search-input" id="tableSearch" placeholder="🔍 ค้นหาประเทศ, สินค้า, หรือ Order ID..." onkeyup="renderTable()">
                    </div>
                </div>

                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Order ID / ประเทศ</th>
                            <th>ตลาด (Market)</th>
                            <th>หมวดหมู่ / สินค้า</th>
                            <th>ยอดขาย ($)</th>
                            <th>กำไร ($)</th>
                            <th>ส่วนลด (%)</th>
                            <th>ค่าส่ง ($) / Ship Mode</th>
                        </tr>
                    </thead>
                    <tbody id="dashTableBody">
                        <!-- Populated by JavaScript -->
                    </tbody>
                </table>
            </div>

        </div> <!-- End Dashboard Container -->

    </main>

    <!-- Bottom Luxury Controls -->
    <footer class="footer-controls">
        <button class="btn" id="prevBtn" onclick="changeSlide(-1)">
            <i class="fa-solid fa-chevron-left"></i>
            <span>ก่อนหน้า (Prev)</span>
        </button>

        <div class="slide-dots" id="dotsContainer">
            <div class="dot active" onclick="goToSlide(1)"></div>
            <div class="dot" onclick="goToSlide(2)"></div>
            <div class="dot" onclick="goToSlide(3)"></div>
            <div class="dot" onclick="goToSlide(4)"></div>
            <div class="dot" onclick="goToSlide(5)"></div>
            <div class="dot" onclick="goToSlide(6)"></div>
            <div class="dot" onclick="goToSlide(7)"></div>
        </div>

        <button class="btn btn-gold" id="nextBtn" onclick="changeSlide(1)">
            <span>ถัดไป (Next)</span>
            <i class="fa-solid fa-chevron-right"></i>
        </button>
    </footer>

    <!-- INJECTED JSON DATA & JAVASCRIPT LOGIC -->
    <script>
        // Embedded Data from Python Data Analytics Engine
        const RAW_DATA = {json_str};

        let currentSlide = 1;
        const totalSlides = 7;
        let currentMode = 'slide'; // 'slide' or 'dash'
        let quickMode = 'all'; // 'all', 'winners', 'disc', 'drain'

        // Chart instances
        let chartYearly = null;
        let chartDisc = null;
        let chartDonut = null;
        let chartDashSub = null;
        let chartDashCtry = null;

        // Initialize on load
        window.onload = () => {{
            initSlideCharts();
            populatePreviewTable();
            applyDashboardFilters();
            updateSlideDisplay();
        }};

        // Mode Switching
        function switchMode(mode) {{
            currentMode = mode;
            if (mode === 'slide') {{
                document.getElementById('presentationContainer').style.display = 'flex';
                document.getElementById('dashboardContainer').classList.remove('active');
                document.getElementById('modeBtnSlide').classList.add('active');
                document.getElementById('modeBtnDash').classList.remove('active');
                document.querySelector('.footer-controls').style.display = 'flex';
                updateSlideDisplay();
            }} else {{
                document.getElementById('presentationContainer').style.display = 'none';
                document.getElementById('dashboardContainer').classList.add('active');
                document.getElementById('modeBtnSlide').classList.remove('active');
                document.getElementById('modeBtnDash').classList.add('active');
                document.querySelector('.footer-controls').style.display = 'none';
                applyDashboardFilters();
            }}
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        // Slide Presentation Navigation
        function updateSlideDisplay() {{
            if (currentMode !== 'slide') return;
            document.querySelectorAll('.slide').forEach(slide => slide.classList.remove('active'));
            const activeSlide = document.getElementById(`slide-${{currentSlide}}`);
            if (activeSlide) activeSlide.classList.add('active');

            document.getElementById('slideCounter').innerText = `Slide ${{currentSlide}} / ${{totalSlides}}`;

            document.querySelectorAll('.dot').forEach((dot, index) => {{
                if (index + 1 === currentSlide) dot.classList.add('active');
                else dot.classList.remove('active');
            }});

            document.getElementById('prevBtn').style.opacity = currentSlide === 1 ? '0.4' : '1';
            document.getElementById('prevBtn').style.pointerEvents = currentSlide === 1 ? 'none' : 'auto';
            
            if (currentSlide === totalSlides) {{
                document.getElementById('nextBtn').innerHTML = '<span>เปิด Interactive BI Dashboard</span> <i class="fa-solid fa-chart-pie"></i>';
            }} else {{
                document.getElementById('nextBtn').innerHTML = '<span>ถัดไป (Next)</span> <i class="fa-solid fa-chevron-right"></i>';
            }}
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}

        function changeSlide(direction) {{
            if (currentSlide === totalSlides && direction === 1) {{
                switchMode('dash');
                return;
            }}
            const next = currentSlide + direction;
            if (next >= 1 && next <= totalSlides) {{
                currentSlide = next;
                updateSlideDisplay();
            }}
        }}

        function goToSlide(slideNum) {{
            if (slideNum >= 1 && slideNum <= totalSlides) {{
                currentSlide = slideNum;
                updateSlideDisplay();
            }}
        }}

        function toggleNotes() {{
            if (currentMode === 'slide') {{
                const activeSlide = document.getElementById(`slide-${{currentSlide}}`);
                const notes = activeSlide.querySelector('.speaking-notes');
                if (notes) notes.classList.toggle('show');
            }}
        }}

        function toggleFullScreen() {{
            if (!document.fullscreenElement) {{
                document.documentElement.requestFullscreen().catch(err => alert(err.message));
            }} else {{
                if (document.exitFullscreen) document.exitFullscreen();
            }}
        }}

        // Initialize Slide Charts (Chart.js)
        function initSlideCharts() {{
            // 1. Slide 3: Yearly Trend Combo Chart
            const ctxYear = document.getElementById('chartYearlyTrend')?.getContext('2d');
            if (ctxYear) {{
                const years = ['2011', '2012', '2013', '2014'];
                const sales = [2259450, 2677438, 3405746, 4299865];
                const margins = [11.02, 11.48, 11.95, 11.73];

                chartYearly = new Chart(ctxYear, {{
                    type: 'bar',
                    data: {{
                        labels: years,
                        datasets: [
                            {{
                                label: 'ยอดขายรวม Sales ($)',
                                data: sales,
                                backgroundColor: 'rgba(99, 102, 241, 0.7)',
                                borderColor: '#6366f1',
                                borderWidth: 1,
                                borderRadius: 8,
                                yAxisID: 'y'
                            }},
                            {{
                                label: 'Profit Margin (%)',
                                data: margins,
                                type: 'line',
                                borderColor: '#f59e0b',
                                backgroundColor: 'rgba(245, 158, 11, 0.2)',
                                borderWidth: 3,
                                pointBackgroundColor: '#fde047',
                                pointRadius: 6,
                                yAxisID: 'y1'
                            }}
                        ]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ labels: {{ color: '#fff', font: {{ family: 'Sarabun' }} }} }},
                            tooltip: {{
                                callbacks: {{
                                    label: (ctx) => ctx.datasetIndex === 0 ? `ยอดขาย: $${{(ctx.raw/1000000).toFixed(2)}}M` : `Margin: ${{ctx.raw}}%`
                                }}
                            }}
                        }},
                        scales: {{
                            x: {{ ticks: {{ color: '#94a3b8', font: {{ weight: 'bold', size: 13 }} }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                            y: {{ type: 'linear', position: 'left', ticks: {{ color: '#a5b4fc', callback: v => '$' + (v/1000000).toFixed(1) + 'M' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }},
                            y1: {{ type: 'linear', position: 'right', min: 10, max: 13, ticks: {{ color: '#fde047', callback: v => v + '%' }}, grid: {{ drawOnChartArea: false }} }}
                        }}
                    }}
                }});
            }}

            // 2. Slide 4: Discount Tier Chart
            const ctxDisc = document.getElementById('chartDiscountTiers')?.getContext('2d');
            if (ctxDisc) {{
                const tiers = ['0% (เต็ม)', '1-10%', '11-20%', '21-30%', '31-50%', '51-80%'];
                const margins = [25.21, 16.47, 9.74, -5.61, -32.39, -111.02];
                const colors = margins.map(m => m >= 0 ? 'rgba(16, 185, 129, 0.75)' : 'rgba(244, 63, 94, 0.85)');

                chartDisc = new Chart(ctxDisc, {{
                    type: 'bar',
                    data: {{
                        labels: tiers,
                        datasets: [{{
                            label: 'Profit Margin (%)',
                            data: margins,
                            backgroundColor: colors,
                            borderRadius: 8
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{ callbacks: {{ label: ctx => `Margin: ${{ctx.raw}}%` }} }}
                        }},
                        scales: {{
                            x: {{ ticks: {{ color: '#94a3b8', font: {{ size: 12, weight: 'bold' }} }}, grid: {{ display: false }} }},
                            y: {{ ticks: {{ color: '#94a3b8', callback: v => v + '%' }}, grid: {{ color: 'rgba(255,255,255,0.06)' }} }}
                        }}
                    }}
                }});
            }}

            // 3. Slide 5: Shipping Donut Chart
            const ctxDonut = document.getElementById('chartShippingDonut')?.getContext('2d');
            if (ctxDonut) {{
                chartDonut = new Chart(ctxDonut, {{
                    type: 'doughnut',
                    data: {{
                        labels: ['ค่าส่งปกติ (Normal 93.3%)', 'ค่าส่ง Outliers ปกติ (4.8%)', '🚨 ขาดทุนจากค่าส่ง (Drain 1.9%)'],
                        datasets: [{{
                            data: [47875, 2781, 634],
                            backgroundColor: ['#6366f1', '#f59e0b', '#f43f5e'],
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{ callbacks: {{ label: ctx => `${{ctx.label}}: ${{ctx.raw}} ออเดอร์` }} }}
                        }},
                        cutout: '70%'
                    }}
                }});
            }}
        }}

        function populatePreviewTable() {{
            const tbody = document.getElementById('previewDrainTable');
            if (!tbody) return;
            tbody.innerHTML = RAW_DATA.drain_orders.slice(0, 5).map(r => `
                <tr>
                    <td><strong style="color:#fff;">${{r['Global Order ID'].split('_')[1] || r['Global Order ID']}}</strong></td>
                    <td>${{r['Country']}}</td>
                    <td><span style="color:#a5f3fc;">${{r['Ship Mode']}}</span></td>
                    <td>$${{r['Shipping Cost'].toLocaleString()}}</td>
                    <td style="color:#fda4af; font-weight:800;">-$${{Math.abs(r['Profit']).toLocaleString()}}</td>
                </tr>
            `).join('');
        }}

        // ==========================================
        // INTERACTIVE BI DASHBOARD LOGIC
        // ==========================================
        function resetFilters() {{
            document.getElementById('filterYear').value = 'all';
            document.getElementById('filterMarket').value = 'all';
            document.getElementById('filterCategory').value = 'all';
            setQuickFilter('all');
        }}

        function setQuickFilter(mode) {{
            quickMode = mode;
            document.querySelectorAll('.quick-btn').forEach(b => b.classList.remove('active'));
            if (mode === 'all') document.getElementById('btnQuickAll').classList.add('active');
            if (mode === 'winners') document.getElementById('btnQuickWinners').classList.add('active');
            if (mode === 'disc') document.getElementById('btnQuickDisc').classList.add('active');
            if (mode === 'drain') document.getElementById('btnQuickDrain').classList.add('active');
            applyDashboardFilters();
        }}

        function applyDashboardFilters() {{
            const yearVal = document.getElementById('filterYear').value;
            const marketVal = document.getElementById('filterMarket').value;
            const catVal = document.getElementById('filterCategory').value;

            // Filter Cube Data
            let filteredCube = RAW_DATA.cube.filter(r => {{
                if (yearVal !== 'all' && str(r['Order Year']) !== yearVal) return false;
                if (marketVal !== 'all' && r['Market'] !== marketVal) return false;
                if (catVal !== 'all' && r['Category'] !== catVal) return false;
                if (quickMode === 'winners' && r['Profit'] < 0) return false;
                if (quickMode === 'disc' && r['Discount'] <= 0.20) return false;
                if (quickMode === 'drain' && r['Profit'] >= 0) return false;
                return true;
            }});

            // Calculate KPI summary
            let tSales = 0, tProfit = 0, tOrders = 0, tLoss = 0;
            filteredCube.forEach(r => {{
                tSales += r['Sales'];
                tProfit += r['Profit'];
                tOrders += r['Orders'];
                if (r['Profit'] < 0) tLoss += r['Profit'];
            }});

            // Override if drain quick filter is active
            if (quickMode === 'drain') {{
                let drainOrders = RAW_DATA.drain_orders.filter(r => {{
                    if (yearVal !== 'all' && str(r['Order Year']) !== yearVal) return false;
                    if (marketVal !== 'all' && r['Market'] !== marketVal) return false;
                    return true;
                }});
                tSales = drainOrders.reduce((acc, r) => acc + r['Sales'], 0);
                tProfit = drainOrders.reduce((acc, r) => acc + r['Profit'], 0);
                tOrders = drainOrders.length;
                tLoss = tProfit;
            }}

            const margin = tSales > 0 ? (tProfit / tSales * 100) : 0;

            // Update DOM KPIs
            document.getElementById('kpiSales').innerText = `$${{(tSales/1000000).toFixed(2)}}M`;
            document.getElementById('kpiOrders').innerHTML = `<i class="fa-solid fa-cart-shopping"></i> ${{tOrders.toLocaleString()}} คำสั่งซื้อ`;
            
            const profitEl = document.getElementById('kpiProfit');
            profitEl.innerText = `$${{(tProfit/1000000).toFixed(2)}}M`;
            profitEl.style.color = tProfit >= 0 ? 'var(--emerald-light)' : 'var(--rose-light)';

            const marginEl = document.getElementById('kpiMargin');
            marginEl.innerText = `${{margin.toFixed(2)}}%`;
            marginEl.style.color = margin >= 0 ? 'var(--cyan)' : 'var(--rose-light)';

            document.getElementById('kpiLoss').innerText = `-$${{(Math.abs(tLoss)/1000).toFixed(1)}}K`;

            // Render Charts and Table
            renderDashCharts(filteredCube);
            renderTable();
        }}

        function str(val) {{ return String(val); }}

        function renderDashCharts(cubeData) {{
            // Sub-Category aggregation
            let subMap = {{}};
            cubeData.forEach(r => {{
                let s = r['Sub-Category'];
                if (!subMap[s]) subMap[s] = 0;
                subMap[s] += r['Profit'];
            }});
            let subEntries = Object.entries(subMap).sort((a,b) => b[1] - a[1]);
            let subLabels = subEntries.map(e => e[0]);
            let subVals = subEntries.map(e => Math.round(e[1]));
            let subColors = subVals.map(v => v >= 0 ? '#10b981' : '#f43f5e');

            const ctxSub = document.getElementById('chartDashSubcat')?.getContext('2d');
            if (ctxSub) {{
                if (chartDashSub) chartDashSub.destroy();
                chartDashSub = new Chart(ctxSub, {{
                    type: 'bar',
                    data: {{
                        labels: subLabels,
                        datasets: [{{ data: subVals, backgroundColor: subColors, borderRadius: 6 }}]
                    }},
                    options: {{
                        indexAxis: 'y',
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            x: {{ ticks: {{ color: '#94a3b8', callback: v => '$' + (v/1000).toFixed(0) + 'k' }}, grid: {{ color: 'rgba(255,255,255,0.06)' }} }},
                            y: {{ ticks: {{ color: '#fff', font: {{ weight: 'bold' }} }}, grid: {{ display: false }} }}
                        }}
                    }}
                }});
            }}

            // Country aggregation from RAW_DATA.country filtered by market
            const marketVal = document.getElementById('filterMarket').value;
            let ctryData = RAW_DATA.country.filter(r => marketVal === 'all' || r['Market'] === marketVal);
            if (quickMode === 'winners') ctryData = ctryData.filter(r => r['Profit'] > 0);
            if (quickMode === 'disc' || quickMode === 'drain') ctryData = ctryData.filter(r => r['Profit'] < 0);
            
            ctryData.sort((a,b) => b['Profit'] - a['Profit']);
            let topWin = ctryData.slice(0, 5);
            let topLose = ctryData.slice(-5).reverse();
            let combined = [...topWin, ...topLose];
            // remove duplicates if any
            let seen = new Set();
            combined = combined.filter(c => {{ if (seen.has(c['Country'])) return false; seen.add(c['Country']); return true; }});
            combined.sort((a,b) => b['Profit'] - a['Profit']);

            let cLabels = combined.map(c => c['Country']);
            let cVals = combined.map(c => Math.round(c['Profit']));
            let cColors = cVals.map(v => v >= 0 ? '#6366f1' : '#f59e0b');
            if (quickMode === 'drain') cColors = cVals.map(v => '#f43f5e');

            const ctxCtry = document.getElementById('chartDashCountry')?.getContext('2d');
            if (ctxCtry) {{
                if (chartDashCtry) chartDashCtry.destroy();
                chartDashCtry = new Chart(ctxCtry, {{
                    type: 'bar',
                    data: {{
                        labels: cLabels,
                        datasets: [{{ data: cVals, backgroundColor: cColors, borderRadius: 6 }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            x: {{ ticks: {{ color: '#fff', font: {{ weight: 'bold', size: 11 }} }}, grid: {{ display: false }} }},
                            y: {{ ticks: {{ color: '#94a3b8', callback: v => '$' + (v/1000).toFixed(0) + 'k' }}, grid: {{ color: 'rgba(255,255,255,0.06)' }} }}
                        }}
                    }}
                }});
            }}
        }}

        function renderTable() {{
            const query = (document.getElementById('tableSearch')?.value || '').toLowerCase();
            const yearVal = document.getElementById('filterYear').value;
            const marketVal = document.getElementById('filterMarket').value;
            const tbody = document.getElementById('dashTableBody');
            if (!tbody) return;

            let records = RAW_DATA.drain_orders;
            if (quickMode === 'all' || quickMode === 'winners') {{
                // Convert cube summary to readable records for table
                records = RAW_DATA.cube.map(r => ({{
                    'Global Order ID': `CUBE_${{r['Order Year']}}_${{r['Market']}}`,
                    'Country': `${{r['Market']}} Region`,
                    'Market': r['Market'],
                    'Sub-Category': r['Sub-Category'],
                    'Product Name': `สรุปยอดขายหมวด ${{r['Sub-Category']}} (${{r['Orders']}} ออเดอร์)`,
                    'Sales': r['Sales'],
                    'Profit': r['Profit'],
                    'Discount': Math.round(r['Discount'] * 100),
                    'Shipping Cost': r['Shipping Cost'],
                    'Ship Mode': 'Aggregated'
                }}));
            }}

            let filtered = records.filter(r => {{
                if (yearVal !== 'all' && !str(r['Global Order ID']).includes(yearVal) && !str(r['Product Name']).includes(yearVal)) return false;
                if (marketVal !== 'all' && r['Market'] !== marketVal) return false;
                if (query) {{
                    const match = str(r['Country']).toLowerCase().includes(query) ||
                                  str(r['Product Name']).toLowerCase().includes(query) ||
                                  str(r['Sub-Category']).toLowerCase().includes(query) ||
                                  str(r['Global Order ID']).toLowerCase().includes(query);
                    if (!match) return false;
                }}
                return true;
            }}).slice(0, 30); // show top 30 rows

            if (filtered.length === 0) {{
                tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; padding: 2rem; color: #64748b;">ไม่พบข้อมูลตามเงื่อนไขที่กรอง</td></tr>`;
                return;
            }}

            tbody.innerHTML = filtered.map(r => `
                <tr>
                    <td>
                        <strong style="color:#fff; display:block;">${{r['Country']}}</strong>
                        <span style="font-size:0.75rem; color:#64748b;">${{r['Global Order ID'].replace('CUBE_','')}}</span>
                    </td>
                    <td><span style="background:rgba(255,255,255,0.06); padding:0.2rem 0.5rem; border-radius:4px;">${{r['Market']}}</span></td>
                    <td>
                        <div style="font-weight:700; color:#cbd5e1;">${{r['Sub-Category']}}</div>
                        <div style="font-size:0.75rem; color:#64748b; max-width: 250px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" title="${{r['Product Name']}}">${{r['Product Name']}}</div>
                    </td>
                    <td style="font-weight:700;">$${{r['Sales'].toLocaleString()}}</td>
                    <td style="font-weight:800; color: ${{r['Profit'] >= 0 ? '#6ee7b7' : '#fda4af'}};">${{r['Profit'] >= 0 ? '+' : ''}}$${{r['Profit'].toLocaleString()}}</td>
                    <td><span style="color: ${{r['Discount'] > 20 ? '#fda4af' : '#cbd5e1'}};">${{r['Discount']}}%</span></td>
                    <td>
                        <div>$${{r['Shipping Cost'].toLocaleString()}}</div>
                        <div style="font-size:0.75rem; color:#a5b4fc;">${{r['Ship Mode']}}</div>
                    </td>
                </tr>
            `).join('');
        }}

        // Keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (currentMode === 'slide') {{
                if (e.key === 'ArrowRight' || e.key === ' ' || e.key === 'PageDown') changeSlide(1);
                else if (e.key === 'ArrowLeft' || e.key === 'PageUp') changeSlide(-1);
                else if (e.key === 'n' || e.key === 'N') toggleNotes();
            }}
            if (e.key === 'f' || e.key === 'F') toggleFullScreen();
        }});
    </script>
</body>
</html>"""

with open("/mnt/hades/HadesData/AI-visual/global_superstore_eda_presentation.html", "w", encoding="utf-8") as f:
    f.write(html_content)

with open("/mnt/hades/HadesData/AI-visual/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("SUCCESS: global_superstore_eda_presentation.html AND index.html generated successfully!")
