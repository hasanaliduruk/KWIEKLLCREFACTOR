# 📦 Kwiek LLC - E-Commerce Bulk Processing Platform

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![Architecture](https://img.shields.io/badge/architecture-Layered%20(MVC)-success)
![GUI](https://img.shields.io/badge/GUI-Tkinter-orange)
![License](https://img.shields.io/badge/license-MIT-green)

## 📖 About the Project
Kwiek LLC is a comprehensive desktop application designed to automate and streamline Amazon FBA and e-commerce operations. It handles complex data processing tasks including TSV/Excel conversions, restock calculations, invoice matching, and automated expiration date scraping from 3rd party web services (2D Workflow). 

This project was developed to eliminate manual data entry errors, reduce operational time, and provide a seamless User Interface (UI) for warehouse and logistics management.

---

## 🚀 The Refactoring Journey (Technical Debt to Clean Code)
*This project represents a significant milestone in my software engineering journey, demonstrating my ability to handle Technical Debt and apply SOLID principles.*

**The Before (Monolithic "God Object"):**
Originally, the application was a monolithic script (`main.py`) exceeding **8,000 lines of code**. UI components, business logic, network requests, and multithreading processes were tightly coupled. This led to UI freezing, memory leaks, and high maintenance difficulty.

**The After (Layered Architecture):**
I successfully refactored the entire codebase into a modular, maintainable **Layered Architecture**. `main.py` is now a clean router (~350 lines), delegating responsibilities to isolated layers:

- **`core/` (Business Logic Layer):** Pure, UI-agnostic modules for data processing (Pandas), network requests (Requests/BS4), and multithreading. Exception handling is strictly enforced here.
- **`gui/views/` (Presentation Layer):** Isolated UI screens. Modifying one screen no longer breaks the others.
- **`gui/components/` (Reusable UI):** Custom, object-oriented widgets (Custom Buttons, Drag & Drop interfaces, Scrollbars) preventing DRY (Don't Repeat Yourself) violations.
- **`utils/` (Helper Layer):** Centralized event handlers and file operations.

**Key Engineering Achievements:**
- Eliminated Tkinter `Multiple Root` and `Cross-Thread GUI Update` fallacies by implementing thread-safe callbacks (`window.after`).
- Replaced dangerous `multiprocessing` processes with isolated, daemonized `threading` structures for smooth background API calls and web scraping.
- Migrated from hardcoded UI scaling to an event-driven `Resize Manager` architecture.

---

## ✨ Features
* **Restock Processor:** Analyzes multiple Excel files, detects price/quantity mismatches, and generates merged restock reports using `pandas` and `numpy`.
* **Expiration Date Scraper:** Authenticates and scrapes shipment expiration dates from web panels using `requests` and `BeautifulSoup`, rendering results safely in background threads.
* **Smart Invoice Finder:** Matches UPCs with PDF invoices using advanced recursive/iterative search algorithms.
* **Shipment & Order Creator:** Allocates stocks dynamically and generates automated vendor-specific order forms.
* **Drag & Drop UI:** Built-in TkinterDnD support for seamless file imports.
* **Over-The-Air (OTA) Updates:** Built-in secure application updater communicating with GitHub Releases API.

---

## 📂 Project Structure
```text
KwiekLLC/
├── main.py                     # Entry point & View Router
├── core/                       # Business Logic & Services
│   ├── expiration_processor.py # Web scraping & API handling
│   ├── restock_processor.py    # Heavy Pandas calculations
│   └── updater_service.py      # OTA updates & Network IO
├── gui/
│   ├── components/             # Reusable custom widgets
│   └── views/                  # Isolated UI screens (MVC Views)
├── utils/                      # Shared helpers (Events, IO)
├── assets/                     # Images, Icons, and UI assets
└── requirements.txt            # Project dependencies
