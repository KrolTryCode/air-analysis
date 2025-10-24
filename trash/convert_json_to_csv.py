# import json
# import pandas as pd
# from pathlib import Path

# # 🔹 Укажи путь к твоему файлу steamgames.json
# INPUT = Path(r"C:\Users\amals\Downloads\steam-sales\steam-sales-analysis\data\raw\steamgames.json")
# OUTPUT = Path(r"C:\Users\amals\Downloads\steam-sales\steam-sales-analysis\data\raw\steam_sales_clean.csv")

# def clean_text(s):
#     if isinstance(s, str):
#         return s.replace("\r", "").replace("\n", "").strip()
#     return s

# def main():
#     print(f"📂 Чтение: {INPUT}")
#     with open(INPUT, "r", encoding="utf-8") as f:
#         text = f.read()

#     # Если JSON записан в виде набора объектов без скобок []
#     if not text.strip().startswith("["):
#         text = "[" + text.strip().rstrip(",") + "]"

#     data = json.loads(text)

#     df = pd.DataFrame(data)
#     df["discount"] = pd.to_numeric(df["discount"], errors="coerce")
#     df["orig_price"] = pd.to_numeric(df["orig_price"], errors="coerce")
#     df["disc_price"] = pd.to_numeric(df["disc_price"], errors="coerce")

#     for col in ["name", "tags", "reviews"]:
#         df[col] = df[col].apply(clean_text)

#     df.to_csv(OUTPUT, index=False, encoding="utf-8-sig")
#     print(f"✅ CSV сохранён в {OUTPUT}")
#     print(f"📊 {len(df)} строк, {len(df.columns)} колонок")

# if __name__ == "__main__":
#     main()
