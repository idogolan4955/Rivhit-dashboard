# 📊 Rivhit Business Dashboard

דשבורד עסקי מבוסס Web לניהול מכירות וגבייה, מחובר ל-API של **ריווחית אונליין**.

---

## ✨ תכונות

| עמוד | תכונות |
|------|---------|
| **📈 מכירות** | טבלה מלאה עם סינון לפי חודש, סוג מסמך, סוכן וחיפוש חופשי. KPI עליונים (סה״כ, ללא מע״מ, כמות, ממוצע). גרפים: מכירות לפי יום, סוג מסמך, וסוכן. |
| **💰 גבייה** | יתרות לקוחות עם checkbox לסימון, סינון לפי סוכן ויתרה חיובית. KPI: סה״כ, לקוחות עם יתרה, סכום מסומנים. גרף חלוקה לפי סוכן. |

---

## 🏗️ מבנה הפרויקט

```
rivhit-dashboard/
├── app.py                  # דף ראשי + ניווט
├── config.py               # הגדרות (קורא ממשתני סביבה)
├── pages/
│   ├── 1_sales.py          # עמוד מכירות
│   └── 2_collection.py     # עמוד גבייה
├── services/
│   ├── rivhit_api.py       # שכבת תקשורת מול API
│   └── data_processor.py   # נרמול נתונים ל-DataFrame
├── components/
│   ├── kpi_cards.py        # כרטיסי KPI
│   ├── charts.py           # גרפים (Plotly)
│   └── filters.py          # רכיבי סינון
├── utils/
│   └── formatters.py       # עיצוב מספרים ותאריכים
├── requirements.txt
├── render.yaml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 הרצה מקומית

### 1. שכפול הפרויקט
```bash
git clone https://github.com/YOUR_USER/rivhit-dashboard.git
cd rivhit-dashboard
```

### 2. התקנת תלויות
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
# venv\Scripts\activate    # Windows
pip install -r requirements.txt
```

### 3. הגדרת משתני סביבה
```bash
cp .env.example .env
# ערוך את .env והזן את ה-API Token שלך:
# RIVHIT_API_TOKEN=your_real_token_here
```

### 4. הפעלה
```bash
streamlit run app.py
```
הדפדפן יפתח בכתובת `http://localhost:8501`

---

## ☁️ פריסה ל-Render

### שלב 1: העלאה ל-Git
```bash
git init
git add .
git commit -m "Initial commit — Rivhit Dashboard"
git remote add origin https://github.com/YOUR_USER/rivhit-dashboard.git
git push -u origin main
```

### שלב 2: יצירת שירות ב-Render
1. היכנס ל-[dashboard.render.com](https://dashboard.render.com)
2. לחץ **New → Web Service**
3. חבר את הריפו מ-GitHub
4. Render יזהה אוטומטית את `render.yaml`

### שלב 3: הגדרת משתני סביבה ב-Render
ב-Render Dashboard → Service → **Environment**:

| Variable | Value |
|----------|-------|
| `RIVHIT_API_TOKEN` | ה-Token שקיבלת מריווחית |

### שלב 4: Deploy
Render יבנה ויפרוס אוטומטית. תוך כ-2-3 דקות האפליקציה תהיה זמינה.

---

## 🔑 משתני סביבה

| משתנה | חובה | ברירת מחדל | תיאור |
|-------|------|------------|-------|
| `RIVHIT_API_TOKEN` | ✅ | — | מפתח API של ריווחית |
| `RIVHIT_BASE_URL` | ❌ | `https://api.rivhit.co.il/online/RivhitOnlineAPI.svc` | כתובת בסיס ל-API |
| `API_TIMEOUT` | ❌ | `30` | Timeout לבקשות (שניות) |
| `API_MAX_RETRIES` | ❌ | `3` | מספר ניסיונות חוזרים |
| `SALES_DOC_TYPE_IDS` | ❌ | `1,2,3,9` | קודי סוגי מסמכים למכירות |
| `RIVHIT_DATE_FORMAT` | ❌ | `%d/%m/%Y` | פורמט תאריך של ריווחית |
| `APP_TITLE` | ❌ | `Rivhit Business Dashboard` | כותרת האפליקציה |

---

## ⚠️ הנחות לגבי Rivhit API

1. **קודי סוגי מסמכים**: ברירת המחדל היא 1=חשבונית מס, 2=חשבונית זיכוי, 3=חשבונית מס קבלה, 9=חשבונית מס קבלה קופה. אם הקודים שונים בחשבון שלך — עדכן דרך `SALES_DOC_TYPE_IDS`.

2. **שמות סוכנים**: ה-API מחזיר `agent_id` בלבד (לא שם סוכן). המערכת מציגה "סוכן X". ניתן להרחיב עם מיפוי ידני ב-`config.py`.

3. **פורמט תאריכים**: ברירת מחדל `dd/MM/yyyy`. אם ריווחית מחזירה פורמט אחר, עדכן את `RIVHIT_DATE_FORMAT`.

4. **יתרות לקוחות**: נטענות בקריאה נפרדת לכל לקוח (`Customer.Balance`). לחשבונות עם מאות לקוחות זה עלול להיות איטי — מומלץ לשקול שימוש ב-`Customer.OpenDocuments` כחלופה (הקוד כבר כולל תמיכה).

5. **amount_exempt**: ה-API מחזיר `amount_exempt` אבל לא ברור אם זה סכום ללא מע״מ או סכום פטור. המערכת מחשבת `amount - total_vat` כסכום ללא מע״מ.

---

## 🧪 בדיקות שבוצעו

- [x] כל הקבצים מתקמפלים ללא שגיאות syntax
- [x] כל ה-imports תקינים ומתאימים
- [x] אין משתנים שבורים או undefined
- [x] כל קובץ מתאים למבנה התיקיות
- [x] `requirements.txt` מכסה את כל התלויות
- [x] לוגיקת סינון, מיון וגרפים עקבית
- [x] טיפול ב-None values ושדות חסרים
- [x] טיפול בשגיאות API עם retry
- [x] אין API keys בקוד
- [x] `render.yaml` תקין
- [x] תמיכה ב-RTL עברית

---

## 📜 רישיון

פרויקט פרטי. כל הזכויות שמורות.
