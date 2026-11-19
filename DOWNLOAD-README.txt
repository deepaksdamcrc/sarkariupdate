SARKARI UPDATE — WEBSITE SOURCE ZIP

1. index.html ko browser mein open karke saved website preview dekhein.
   Yeh offline preview hai; admin login aur automatic updates ke liye backend chahiye.

2. worker/ mein original HTML, CSS, JavaScript aur Cloudflare Worker backend hai.
   Backend build: node worker/server.mjs
   Is build ke liye Node.js aur Python 3 installed hone chahiye.

3. export/published-articles.json mein ZIP banate waqt ke published articles hain.
   covers/ mein unke illustrated cover images hain. Draft articles shamil nahi hain.
   Live website ke articles aur password is ZIP ko download karne se nahi badalte.

4. .env.example sirf environment-variable names aur instructions hai.
   Aapka asli password, password hash, account records, service tokens,
   login sessions aur Git credentials ZIP mein shamil NAHI hain.

5. Nayi hosting par admin credentials, R2 storage aur hosting project alag
   configure karne honge. .openai/hosting.example.json ek template hai.
   Purani live website ka hosting project ID is ZIP se remove kiya gaya hai.

6. Existing automatic-update schedule ChatGPT/Sites par chalti hai.
   Dusri hosting par sirf ZIP upload karne se woh schedule transfer nahi hoti.
   AUTOMATION.md aur README.md mein backend aur automation details hain.

7. Saved content ko naye database mein restore karna alag step hai.
   export/published-articles.json ko source data samjhein; live R2 security
   records aur passwords export nahi kiye gaye hain.
