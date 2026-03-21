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
I successfully refactored the entire codebase into a modular, maintainable **Layered Architecture**. `main.py` is now a clean router (~500 lines), delegating responsibilities to isolated layers.

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
* **Over-The-Air (OTA) Updates:** Built-in secure application updater communicating with GitHub Releases API.

---

## 📂 Comprehensive Project Structure
The repository strictly adheres to Separation of Concerns (SoC), isolating business logic from presentation.

```text
KWIEKLLC/
├── main.py                     # Entry point & View Router (UI Controller)
├── requirements.txt            # Core project dependencies
├── LICENSE                     # MIT License
├── core/                       # Business Logic Layer (Pure Python, UI-agnostic)
│   ├── converter.py            # Data format conversion logic
│   ├── cost_updater.py         # Dynamic cost calculation algorithms
│   ├── expiration_processor.py # Web scraping & DOM parsing (BS4/Requests)
│   ├── future_price_updater.py # Predictive pricing logic
│   ├── invoice_finder.py       # PDF/Data matching engine
│   ├── invoice_processor.py    # Invoice data extraction
│   ├── order_creator.py        # Automated order allocation
│   ├── restock_processor.py    # Heavy Pandas/NumPy dataframe operations
│   ├── shipment_creator.py     # Shipment data aggregation
│   ├── tsv_converter.py        # TSV to Excel parsing
│   └── updater_service.py      # Network IO & OTA update management
├── gui/                        # Presentation Layer (MVC Views & Components)
│   ├── components/             # Reusable Object-Oriented UI widgets
│   │   ├── animated_image.py
│   │   ├── choosers.py
│   │   ├── custom_buttons.py   # Master button class with hover/click states
│   │   ├── drag_drop.py        # TkinterDnD wrappers
│   │   ├── option_menu.py
│   │   ├── round_button.py
│   │   └── scrollbar.py        # Custom kinetic scrollbar
│   └── views/                  # Isolated UI screens (No business logic)
│       ├── converter_view.py
│       ├── costupdater_view.py
│       ├── expration_view.py
│       ├── futureprice_view.py
│       ├── invoice_view.py
│       ├── invoicefinder_view.py
│       ├── ordercreate_view.py
│       ├── restock_view.py
│       ├── shipmentcreater_view.py
│       ├── tsv_view.py
│       └── updater_view.py
├── utils/                      # Helper Layer (DRY Compliance)
│   ├── event_handlers.py       # Centralized UI event tracking
│   ├── file_operations.py      # OS-level file/directory IO
│   └── gui_helpers.py          # Coordinate & rendering math
└── assets/                     # Static resources (Icons, UI imagery)