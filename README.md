# LinkedIn Easy Apply Bot 

This Python script automates the LinkedIn "Easy Apply" job application process using Selenium. It logs in with your credentials, navigates to a filtered job search page, and applies to job listings that can be completed in a single flow (i.e., ones that only require a phone number and a few clicks).

---

##  Features

- Logs into LinkedIn automatically  
- Iterates through job cards with the Easy Apply filter  
- Fills in your phone number if it's missing  
- Navigates multi-step Easy Apply forms  
- Submits the application if it reaches a "Review" screen  
- Skips or discards jobs with too many steps  

---

##  Installation & Usage

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/linkedin-auto-applier.git
cd linkedin-auto-applier
pip install -r requirements.txt
```

### 2. Install dependencies
Make sure you’re using Python 3.8+ and have `pip` installed.

```bash
pip install selenium python-dotenv
```

### 3. Set up your `.env` file
Create a `.env` file in the root directory with the following contents:

```
LINKEDIN_USERNAME=your_email@example.com
LINKEDIN_PASSWORD=your_password
LINKEDIN_PHONE=555-123-4567
```

### 4. Run the script
```bash
python main.py
```

Make sure your Chrome browser is installed and matches the version required by your ChromeDriver.

---

## ⚠️ Disclaimer

This script relies on the structure of LinkedIn's HTML and class names, which **may change at any time**. If the bot stops working, it's likely because:

- LinkedIn has updated their class names, IDs, or DOM structure  
- The Easy Apply modal behaves differently for some job listings  
- You're seeing A/B-tested layouts or personalized flows  
- The modal takes too long to load due to network speed  

This script **does not handle complex applications**, file uploads, or custom questions. It is designed only for quick, single-page Easy Apply jobs.

> Use this tool responsibly and at your own risk. This is **not affiliated with or endorsed by LinkedIn** in any way. Use of bots or automation on LinkedIn may violate their Terms of Service.

---

##  License

MIT License
