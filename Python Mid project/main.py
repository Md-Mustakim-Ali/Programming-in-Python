
import json
import os

import numpy as np

# 1. IMMUTABLE CONFIGURATION DATA (TUPLES & DICTIONARIES)

VALID_TIERS = ("Monthly", "Quarterly", "Yearly")


VALID_STATUSES = ("Active", "Overdue")

MAIN_MENU_OPTIONS = (
    "1. Add New Member",
    "2. View All Members",
    "3. Search Member (by ID or Name)",
    "4. Update Member Profile / Fee Status",
    "5. Delete Member Record",
    "6. Manage Supplement Inventory (Add / Restock / Sell / View)",
    "7. Run NumPy Statistical & Revenue Analysis",
    "8. Save Data & Exit Application",
)

SUPPLEMENT_MENU_OPTIONS = (
    "1. View Supplement Inventory",
    "2. Add New Supplement Item",
    "3. Update Stock Quantity (Restock)",
    "4. Record Supplement Sale",
    "5. Delete Supplement Item",
    "6. Return to Main Menu",
)


TIER_MONTHLY_RATES_BDT = {
    "Monthly": 1500.0,
    "Quarterly": 1333.33,
    "Yearly": 1200.0,
}


TIER_PACKAGE_FEES_BDT = {
    "Monthly": 1500.0,
    "Quarterly": 4000.0,
    "Yearly": 14400.0,
}

DATA_FILE_PATH = "alis_gym_data.json"



# 2. DATA MODEL CLASSES

class Member:

    def __init__(self, member_id, name, contact, plan_tier, fee_status, duration_months):
        self.member_id = str(member_id).strip().upper()
        self.name = str(name).strip()
        self.contact = str(contact).strip()
        self.plan_tier = str(plan_tier).strip()
        self.fee_status = str(fee_status).strip()
        self.duration_months = int(duration_months)

    def get_monthly_rate(self):
        return TIER_MONTHLY_RATES_BDT.get(self.plan_tier, 1500.0)

    def get_package_fee(self):
        return TIER_PACKAGE_FEES_BDT.get(self.plan_tier, 1500.0)

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "contact": self.contact,
            "plan_tier": self.plan_tier,
            "fee_status": self.fee_status,
            "duration_months": self.duration_months,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            member_id=data.get("member_id", "UNKNOWN"),
            name=data.get("name", "Unknown"),
            contact=data.get("contact", "N/A"),
            plan_tier=data.get("plan_tier", "Monthly"),
            fee_status=data.get("fee_status", "Active"),
            duration_months=int(data.get("duration_months", 1)),
        )

    def display_row(self):
        monthly_bdt = self.get_monthly_rate()
        return (
            f"{self.member_id:<8} | {self.name:<22} | {self.contact:<13} | "
            f"{self.plan_tier:<10} | {self.fee_status:<8} | "
            f"{self.duration_months:<8} | {monthly_bdt:>10,.2f} BDT"
        )


class Supplement:

    def __init__(self, item_id, item_name, brand, stock_qty, unit_price_bdt, units_sold=0):
        self.item_id = str(item_id).strip().upper()
        self.item_name = str(item_name).strip()
        self.brand = str(brand).strip()
        self.stock_qty = int(stock_qty)
        self.unit_price_bdt = float(unit_price_bdt)
        self.units_sold = int(units_sold)

    def get_stock_valuation(self):
        return self.stock_qty * self.unit_price_bdt

    def get_sales_revenue(self):
        return self.units_sold * self.unit_price_bdt

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "item_name": self.item_name,
            "brand": self.brand,
            "stock_qty": self.stock_qty,
            "unit_price_bdt": self.unit_price_bdt,
            "units_sold": self.units_sold,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            item_id=data.get("item_id", "SUP-00"),
            item_name=data.get("item_name", "Unknown Item"),
            brand=data.get("brand", "Generic"),
            stock_qty=int(data.get("stock_qty", 0)),
            unit_price_bdt=float(data.get("unit_price_bdt", 0.0)),
            units_sold=int(data.get("units_sold", 0)),
        )

    def display_row(self):
        valuation = self.get_stock_valuation()
        return (
            f"{self.item_id:<7} | {self.item_name:<25} | {self.brand:<16} | "
            f"{self.stock_qty:<6} | {self.unit_price_bdt:>10,.2f} | "
            f"{self.units_sold:<5} | {valuation:>12,.2f} BDT"
        )


# 3. MANAGER / CONTROLLER CLASS

class GymManager:

    def __init__(self, file_path=DATA_FILE_PATH):
        self.file_path = file_path
        self.members = []
        self.supplements = []
        self.member_ids_set = set()
        self.supplement_ids_set = set()
        self.load_data()

    def _rebuild_id_sets(self):
        self.member_ids_set = {m.member_id for m in self.members}
        self.supplement_ids_set = {s.item_id for s in self.supplements}

    def initialize_sample_data(self):
        sample_members = [
            Member("M-101", "Tanvir Ahmed", "01711-234567", "Yearly", "Active", 14),
            Member("M-102", "Nusrat Jahan", "01819-876543", "Quarterly", "Active", 6),
            Member("M-103", "Rafiqul Islam", "01912-345678", "Monthly", "Overdue", 2),
            Member("M-104", "Sadia Rahman", "01675-112233", "Yearly", "Active", 18),
            Member("M-105", "Mehedi Hasan", "01552-998877", "Monthly", "Active", 4),
            Member("M-106", "Farhana Yasmin", "01722-445566", "Quarterly", "Overdue", 3),
            Member("M-107", "Kamrul Hasan", "01833-667788", "Monthly", "Active", 1),
            Member("M-108", "Tasnim Zara", "01944-556677", "Yearly", "Active", 12),
            Member("M-109", "Ashraful Alam", "01755-889900", "Quarterly", "Active", 9),
            Member("M-110", "Mahmudul Haque", "01611-223344", "Monthly", "Overdue", 5),
        ]

        sample_supplements = [
            Supplement("S-201", "Gold Standard Whey 5lbs", "Optimum Nutr.", 12, 9500.0, 18),
            Supplement("S-202", "Micronized Creatine 300g", "MuscleTech", 25, 2400.0, 34),
            Supplement("S-203", "ISO 100 Hydrolyzed 5lbs", "Dymatize", 8, 11200.0, 9),
            Supplement("S-204", "BCAA Energy Powder 30sv", "EVLution", 15, 2800.0, 21),
            Supplement("S-205", "Serious Mass Gainer 12lbs", "Optimum Nutr.", 10, 7800.0, 14),
            Supplement("S-206", "Omega-3 Fish Oil 100ct", "Now Foods", 30, 1350.0, 40),
        ]

        self.members = sample_members
        self.supplements = sample_supplements
        self._rebuild_id_sets()
        self.save_data()


    # PERSISTENT FILE HANDLING (JSON) WITH EXCEPTION HANDLING

    def save_data(self):
        data_dict = {
            "members": [m.to_dict() for m in self.members],
            "supplements": [s.to_dict() for s in self.supplements],
        }
        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(data_dict, file, indent=4)
            return True
        except OSError as e:
            print(f"\n[FILE ERROR] Could not save data to '{self.file_path}': {e}")
            return False

    def load_data(self):

        if not os.path.exists(self.file_path):
            print(f"[INFO] Data file '{self.file_path}' not found. Initializing default sample records...")
            self.initialize_sample_data()
            return

        try:
            if os.path.getsize(self.file_path) == 0:
                print(f"[WARNING] Data file '{self.file_path}' is empty. Loading sample records...")
                self.initialize_sample_data()
                return

            with open(self.file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)

            if not isinstance(raw_data, dict):
                raise TypeError("Root JSON element must be a dictionary.")

            loaded_members = []
            for m_dict in raw_data.get("members", []):
                loaded_members.append(Member.from_dict(m_dict))

            loaded_supplements = []
            for s_dict in raw_data.get("supplements", []):
                loaded_supplements.append(Supplement.from_dict(s_dict))

            self.members = loaded_members
            self.supplements = loaded_supplements
            self._rebuild_id_sets()

            if len(self.members) == 0 and len(self.supplements) == 0:
                self.initialize_sample_data()

        except (json.JSONDecodeError, ValueError, KeyError, TypeError) as e:
            print(f"\n[FILE WARNING] Corrupted or malformed data in '{self.file_path}' ({e}).")
            print("[INFO] Restoring clean sample records so the program can continue safely...")
            self.initialize_sample_data()
        except OSError as e:
            print(f"\n[FILE ERROR] Could not read '{self.file_path}': {e}")
            self.initialize_sample_data()

  
    def add_member(self, member_obj):
        if member_obj.member_id in self.member_ids_set:
            return False
        self.members.append(member_obj)
        self.member_ids_set.add(member_obj.member_id)
        self.save_data()
        return True

    def find_member_by_id(self, member_id):
        target_id = str(member_id).strip().upper()
        if target_id not in self.member_ids_set:
            return None
        for member in self.members:
            if member.member_id == target_id:
                return member
        return None

    def search_members(self, query):
        q = str(query).strip().lower()
        results = []
        for member in self.members:
            if q in member.member_id.lower() or q in member.name.lower():
                results.append(member)
        return results

    def delete_member(self, member_id):
        member = self.find_member_by_id(member_id)
        if member is None:
            return False
        self.members.remove(member)
        self.member_ids_set.discard(member.member_id)
        self.save_data()
        return True


    # SUPPLEMENT INVENTORY OPERATIONS

    def add_supplement(self, supp_obj):
        if supp_obj.item_id in self.supplement_ids_set:
            return False
        self.supplements.append(supp_obj)
        self.supplement_ids_set.add(supp_obj.item_id)
        self.save_data()
        return True

    def find_supplement_by_id(self, item_id):
        target_id = str(item_id).strip().upper()
        if target_id not in self.supplement_ids_set:
            return None
        for supp in self.supplements:
            if supp.item_id == target_id:
                return supp
        return None

    def delete_supplement(self, item_id):
        supp = self.find_supplement_by_id(item_id)
        if supp is None:
            return False
        self.supplements.remove(supp)
        self.supplement_ids_set.discard(supp.item_id)
        self.save_data()
        return True

   
    # NUMPY STATISTICAL & REVENUE ANALYSIS

    def run_numpy_analytics(self):
        print("\n" + "=" * 78)
        print("       ALI'S GYM NUMPY STATISTICAL & FINANCIAL ANALYTICS REPORT")
        print("=" * 78)

        if len(self.members) == 0:
            print("\n[!] No member records available for analysis.")
        else:
            durations_arr = np.array([m.duration_months for m in self.members], dtype=np.float64)
            monthly_fees_arr = np.array([m.get_monthly_rate() for m in self.members], dtype=np.float64)
            statuses_arr = np.array([m.fee_status for m in self.members])

            active_mask = statuses_arr == "Active"
            overdue_mask = statuses_arr == "Overdue"

            total_expected_monthly_rev = np.sum(monthly_fees_arr)
            active_collected_monthly_rev = np.sum(monthly_fees_arr[active_mask])
            overdue_pending_monthly_rev = np.sum(monthly_fees_arr[overdue_mask])

            avg_duration = np.mean(durations_arr)
            median_duration = np.median(durations_arr)
            min_duration = np.min(durations_arr)
            max_duration = np.max(durations_arr)
            std_duration = np.std(durations_arr)

            total_members = len(self.members)
            active_count = int(np.sum(active_mask))
            overdue_count = int(np.sum(overdue_mask))
            active_pct = (active_count / total_members) * 100.0
            overdue_pct = (overdue_count / total_members) * 100.0

            tier_counts = {}
            for tier in VALID_TIERS:
                tier_counts[tier] = sum(1 for m in self.members if m.plan_tier == tier)

            print("\n[1] MONTHLY GYM MEMBERSHIP REVENUE (NUMPY VECTORIZED):")
            print(f"    * Total Expected Monthly Revenue   : {total_expected_monthly_rev:>12,.2f} BDT")
            print(f"    * Active (Collected) Monthly Rev   : {active_collected_monthly_rev:>12,.2f} BDT")
            print(f"    * Overdue (Pending) Monthly Dues   : {overdue_pending_monthly_rev:>12,.2f} BDT")

            print("\n[2] MEMBER RETENTION DURATION ANALYSIS (IN MONTHS):")
            print(f"    * Average Retention Duration (Mean): {avg_duration:>8.2f} months")
            print(f"    * Median Retention Duration        : {median_duration:>8.2f} months")
            print(f"    * Minimum / Maximum Duration       : {min_duration:.0f} mo  /  {max_duration:.0f} mo")
            print(f"    * Standard Deviation (Spread)      : {std_duration:>8.2f} months")

            print("\n[3] FEE STATUS & PLAN TIER BREAKDOWN:")
            print(f"    * Total Registered Members         : {total_members}")
            print(f"    * Active Fee Status                : {active_count} members ({active_pct:.1f}%)")
            print(f"    * Overdue Fee Status               : {overdue_count} members ({overdue_pct:.1f}%)")
            print(
                f"    * Plan Tier Breakdown              : "
                f"Monthly: {tier_counts['Monthly']} | "
                f"Quarterly: {tier_counts['Quarterly']} | "
                f"Yearly: {tier_counts['Yearly']}"
            )

        if len(self.supplements) == 0:
            print("\n[!] No supplement inventory records available for analysis.")
        else:
            stock_arr = np.array([s.stock_qty for s in self.supplements], dtype=np.float64)
            price_arr = np.array([s.unit_price_bdt for s in self.supplements], dtype=np.float64)
            sold_arr = np.array([s.units_sold for s in self.supplements], dtype=np.float64)

            item_valuations_arr = stock_arr * price_arr
            item_sales_rev_arr = sold_arr * price_arr

            total_inventory_valuation = np.sum(item_valuations_arr)
            total_sales_revenue = np.sum(item_sales_rev_arr)
            total_units_in_stock = int(np.sum(stock_arr))
            total_units_sold = int(np.sum(sold_arr))
            avg_unit_price = np.mean(price_arr)
            max_valued_idx = int(np.argmax(item_valuations_arr))
            top_valued_item = self.supplements[max_valued_idx]

            print("\n[4] SUPPLEMENT INVENTORY VALUATION & SALES (NUMPY VECTORIZED):")
            print(f"    * Total Unique Supplement Products : {len(self.supplements)} items")
            print(f"    * Total Units Currently in Stock   : {total_units_in_stock} units")
            print(f"    * Total Units Sold to Date         : {total_units_sold} units")
            print(f"    * Average Supplement Unit Price    : {avg_unit_price:>12,.2f} BDT")
            print(f"    * Total Current Stock Valuation    : {total_inventory_valuation:>12,.2f} BDT")
            print(f"    * Total Supplement Sales Revenue   : {total_sales_revenue:>12,.2f} BDT")
            print(
                f"    * Highest Value Inventory Item     : {top_valued_item.item_name} "
                f"({item_valuations_arr[max_valued_idx]:,.2f} BDT)"
            )

        print("=" * 78)



# 4. INPUT & VALIDATION HELPER FUNCTIONS

def get_non_empty_string(prompt):
    while True:
        user_input = input(prompt).strip()
        if len(user_input) > 0:
            return user_input
        print("  [VALIDATION ERROR] Input cannot be empty. Please try again.")


def get_valid_int(prompt, min_val=0, max_val=None):
    while True:
        raw_val = input(prompt).strip()
        try:
            val = int(raw_val)
            if val < min_val:
                print(f"  [VALIDATION ERROR] Value must be at least {min_val}. Please try again.")
                continue
            if max_val is not None and val > max_val:
                print(f"  [VALIDATION ERROR] Value cannot exceed {max_val}. Please try again.")
                continue
            return val
        except ValueError:
            print("  [INPUT ERROR] Invalid numeric input! Please enter a whole number (integer).")


def get_valid_float(prompt, min_val=0.0):
    while True:
        raw_val = input(prompt).strip()
        try:
            val = float(raw_val)
            if val < min_val:
                print(f"  [VALIDATION ERROR] Amount cannot be less than {min_val:.2f}. Please try again.")
                continue
            return val
        except ValueError:
            print("  [INPUT ERROR] Invalid number! Please enter a valid numeric amount (e.g., 2500 or 2500.50).")


def select_from_tuple(prompt_title, options_tuple):
    print(f"\n  {prompt_title}")
    for idx, option in enumerate(options_tuple, start=1):
        print(f"    {idx}. {option}")
    choice = get_valid_int(f"  Select option (1-{len(options_tuple)}): ", min_val=1, max_val=len(options_tuple))
    return options_tuple[choice - 1]


# 5. CONSOLE INTERFACE & MENU FUNCTIONS

def display_members_table(members_list, title="ALI'S GYM - REGISTERED MEMBERS"):
    print("\n" + "=" * 95)
    print(f"  {title} (Total: {len(members_list)})")
    print("=" * 95)
    if not members_list:
        print("  No member records found.")
        print("=" * 95)
        return

    header = (
        f"{'ID':<8} | {'Member Name':<22} | {'Contact':<13} | "
        f"{'Plan Tier':<10} | {'Status':<8} | {'Duration':<8} | {'Monthly Rate'}"
    )
    print(header)
    print("-" * 95)
    for member in members_list:
        print(member.display_row())
    print("=" * 95)


def display_supplements_table(supplements_list):
    print("\n" + "=" * 102)
    print(f"  ALI'S GYM - PROTEIN & FITNESS SUPPLEMENT INVENTORY (Total Items: {len(supplements_list)})")
    print("=" * 102)
    if not supplements_list:
        print("  No supplement items in inventory.")
        print("=" * 102)
        return

    header = (
        f"{'ID':<7} | {'Supplement Name':<25} | {'Brand':<16} | "
        f"{'Stock':<6} | {'Unit (BDT)':>10} | {'Sold':<5} | {'Stock Valuation'}"
    )
    print(header)
    print("-" * 102)
    for supp in supplements_list:
        print(supp.display_row())
    print("=" * 102)


def handle_add_member(manager):
    print("\n--- [ ADD NEW GYM MEMBER - ALI'S GYM ] ---")
    while True:
        member_id = get_non_empty_string("Enter Unique Member ID (e.g., M-111): ").upper()
        if member_id in manager.member_ids_set:
            print(f"  [DUPLICATE ERROR] Member ID '{member_id}' already exists! Please enter a unique ID.")
        else:
            break

    name = get_non_empty_string("Enter Member Full Name: ")
    contact = get_non_empty_string("Enter Contact Number (e.g., 017XX-XXXXXX): ")

    print("\n  Ali's Gym Membership Plan Pricing Reference:")
    print("    * Monthly   :  1,500 BDT / month")
    print("    * Quarterly :  4,000 BDT package (~1,333.33 BDT / month)")
    print("    * Yearly    : 14,400 BDT package ( 1,200.00 BDT / month)")
    plan_tier = select_from_tuple("Choose Membership Plan Tier:", VALID_TIERS)
    fee_status = select_from_tuple("Select Current Fee Status:", VALID_STATUSES)
    duration_months = get_valid_int("Enter Membership Duration (in months, 1-120): ", min_val=1, max_val=120)

    new_member = Member(member_id, name, contact, plan_tier, fee_status, duration_months)
    if manager.add_member(new_member):
        print(f"\n  [SUCCESS] Member '{name}' (ID: {member_id}) added and saved to '{manager.file_path}'.")
    else:
        print("\n  [ERROR] Could not add member due to duplicate ID.")


def handle_search_member(manager):
    print("\n--- [ SEARCH GYM MEMBER - ALI'S GYM ] ---")
    query = get_non_empty_string("Enter Member ID or Name keyword to search: ")
    results = manager.search_members(query)
    if results:
        display_members_table(results, title=f"SEARCH RESULTS FOR '{query}'")
    else:
        print(f"\n  [NOT FOUND] No member records matched '{query}'.")


def handle_update_member(manager):
    print("\n--- [ UPDATE MEMBER PROFILE / FEE STATUS ] ---")
    member_id = get_non_empty_string("Enter Member ID to update (e.g., M-103): ").upper()
    member = manager.find_member_by_id(member_id)

    if member is None:
        print(f"\n  [NOT FOUND] Member with ID '{member_id}' does not exist.")
        return

    print("\n  Current Member Record:")
    display_members_table([member], title="SELECTED MEMBER")

    print("\n  What would you like to update?")
    print("    1. Fee Status (Active / Overdue)")
    print("    2. Membership Plan Tier (Monthly / Quarterly / Yearly)")
    print("    3. Retention Duration (Months)")
    print("    4. Contact Number & Name")
    print("    5. Cancel Update")

    choice = get_valid_int("  Enter choice (1-5): ", min_val=1, max_val=5)

    if choice == 1:
        member.fee_status = select_from_tuple("Select New Fee Status:", VALID_STATUSES)
    elif choice == 2:
        member.plan_tier = select_from_tuple("Select New Membership Tier:", VALID_TIERS)
    elif choice == 3:
        member.duration_months = get_valid_int("Enter updated duration (in months, 1-120): ", min_val=1, max_val=120)
    elif choice == 4:
        member.name = get_non_empty_string("Enter updated Full Name: ")
        member.contact = get_non_empty_string("Enter updated Contact Number: ")
    else:
        print("  [INFO] Update cancelled.")
        return

    manager.save_data()
    print(f"\n  [SUCCESS] Member '{member.member_id}' updated and saved successfully!")


def handle_delete_member(manager):
    print("\n--- [ DELETE MEMBER RECORD ] ---")
    member_id = get_non_empty_string("Enter Member ID to delete (e.g., M-110): ").upper()
    member = manager.find_member_by_id(member_id)

    if member is None:
        print(f"\n  [NOT FOUND] No member found with ID '{member_id}'.")
        return

    display_members_table([member], title="MEMBER TO BE DELETED")
    confirm = input(f"  Are you sure you want to permanently delete '{member.name}'? (y/n): ").strip().lower()
    if confirm == "y":
        manager.delete_member(member_id)
        print(f"  [SUCCESS] Member '{member_id}' has been removed and JSON file updated.")
    else:
        print("  [INFO] Deletion cancelled.")


def handle_supplement_submenu(manager):
    while True:
        print("\n" + "-" * 58)
        print("   ALI'S GYM - SUPPLEMENT INVENTORY MANAGEMENT SUB-MENU")
        print("-" * 58)
        for option in SUPPLEMENT_MENU_OPTIONS:
            print(f"  {option}")
        print("-" * 58)

        choice = get_valid_int("Select an action (1-6): ", min_val=1, max_val=6)

        if choice == 1:
            display_supplements_table(manager.supplements)

        elif choice == 2:
            print("\n--- [ ADD NEW SUPPLEMENT ITEM ] ---")
            while True:
                item_id = get_non_empty_string("Enter Unique Supplement ID (e.g., S-207): ").upper()
                if item_id in manager.supplement_ids_set:
                    print(f"  [DUPLICATE ERROR] Supplement ID '{item_id}' already exists!")
                else:
                    break
            item_name = get_non_empty_string("Enter Supplement Name (e.g., Whey Isolate 2lbs): ")
            brand = get_non_empty_string("Enter Brand Name (e.g., MusclePharm): ")
            stock_qty = get_valid_int("Enter Initial Stock Quantity (0-1000): ", min_val=0, max_val=1000)
            unit_price = get_valid_float("Enter Unit Price in BDT (e.g., 5500): ", min_val=1.0)

            new_supp = Supplement(item_id, item_name, brand, stock_qty, unit_price, units_sold=0)
            manager.add_supplement(new_supp)
            print(f"\n  [SUCCESS] Supplement '{item_name}' added to inventory and saved.")

        elif choice == 3:
            print("\n--- [ RESTOCK SUPPLEMENT ITEM ] ---")
            display_supplements_table(manager.supplements)
            item_id = get_non_empty_string("Enter Supplement ID to restock: ").upper()
            supp = manager.find_supplement_by_id(item_id)
            if supp is None:
                print(f"  [NOT FOUND] Supplement ID '{item_id}' not found.")
            else:
                add_qty = get_valid_int(f"Enter quantity to add to '{supp.item_name}' (1-500): ", min_val=1, max_val=500)
                supp.stock_qty += add_qty
                manager.save_data()
                print(f"  [SUCCESS] Updated stock for '{supp.item_name}' is now {supp.stock_qty} units.")

        elif choice == 4:
            print("\n--- [ RECORD SUPPLEMENT SALE ] ---")
            display_supplements_table(manager.supplements)
            item_id = get_non_empty_string("Enter Supplement ID sold: ").upper()
            supp = manager.find_supplement_by_id(item_id)
            if supp is None:
                print(f"  [NOT FOUND] Supplement ID '{item_id}' not found.")
            elif supp.stock_qty <= 0:
                print(f"  [OUT OF STOCK] '{supp.item_name}' has 0 units available!")
            else:
                sell_qty = get_valid_int(
                    f"Enter units sold (Available: {supp.stock_qty}): ",
                    min_val=1,
                    max_val=supp.stock_qty,
                )
                supp.stock_qty -= sell_qty
                supp.units_sold += sell_qty
                total_bill = sell_qty * supp.unit_price_bdt
                manager.save_data()
                print(f"  [SALE RECORDED] Sold {sell_qty}x '{supp.item_name}' for {total_bill:,.2f} BDT.")
                print(f"  Remaining Stock: {supp.stock_qty} units.")

        elif choice == 5:
            print("\n--- [ DELETE SUPPLEMENT ITEM ] ---")
            item_id = get_non_empty_string("Enter Supplement ID to delete: ").upper()
            supp = manager.find_supplement_by_id(item_id)
            if supp is None:
                print(f"  [NOT FOUND] Supplement ID '{item_id}' not found.")
            else:
                confirm = input(f"  Delete '{supp.item_name}' from inventory? (y/n): ").strip().lower()
                if confirm == "y":
                    manager.delete_supplement(item_id)
                    print(f"  [SUCCESS] Supplement '{item_id}' deleted.")
                else:
                    print("  [INFO] Deletion cancelled.")

        elif choice == 6:
            break


# 6. MAIN APPLICATION ENTRY POINT
def main():
    print("=" * 78)
    print("  WELCOME TO ALI'S GYM: LOCAL FITNESS CENTER MEMBERSHIP & SUPPLEMENT TRACKER")
    print("                     (Dhaka, Bangladesh | Currency: BDT)")
    print("=" * 78)

    manager = GymManager(DATA_FILE_PATH)
    print(f"[SYSTEM READY] Loaded {len(manager.members)} members and {len(manager.supplements)} supplements from '{DATA_FILE_PATH}'.")

    while True:
        print("\n" + "=" * 58)
        print("                    ALI'S GYM MAIN MENU")
        print("=" * 58)
        for option in MAIN_MENU_OPTIONS:
            print(f"  {option}")
        print("=" * 58)

        choice = get_valid_int("Enter your choice (1-8): ", min_val=1, max_val=8)

        if choice == 1:
            handle_add_member(manager)
        elif choice == 2:
            display_members_table(manager.members)
        elif choice == 3:
            handle_search_member(manager)
        elif choice == 4:
            handle_update_member(manager)
        elif choice == 5:
            handle_delete_member(manager)
        elif choice == 6:
            handle_supplement_submenu(manager)
        elif choice == 7:
            manager.run_numpy_analytics()
        elif choice == 8:
            manager.save_data()
            print("\n" + "=" * 78)
            print(f"  [SAVED] All data has been safely persisted to '{DATA_FILE_PATH}'.")
            print("  Thank you for using Ali's Gym Tracker! Stay strong and healthy.")
            print("=" * 78)
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Program interrupted by user. Exiting safely...")
