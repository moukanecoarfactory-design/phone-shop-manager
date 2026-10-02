from dataclasses import dataclass
from typing import Optional


@dataclass
class Product:
    id: Optional[int] = None
    name: str = ""
    category_id: Optional[int] = None
    brand: str = ""
    capacity: str = ""
    buying_price: float = 0.0
    selling_price: float = 0.0
    quantity: int = 0
    low_stock_alert: int = 5
    supplier_id: Optional[int] = None
    barcode: str = ""
    notes: str = ""
    image_path: str = ""

    @property
    def profit(self) -> float:
        return self.selling_price - self.buying_price

    @property
    def is_low_stock(self) -> bool:
        return self.quantity <= self.low_stock_alert


@dataclass
class Category:
    id: Optional[int] = None
    name_en: str = ""
    name_ar: str = ""
    name_fr: str = ""

    def display_name(self, lang: str = "en") -> str:
        if lang == "ar" and self.name_ar:
            return self.name_ar
        if lang == "fr" and self.name_fr:
            return self.name_fr
        return self.name_en


@dataclass
class Customer:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    address: str = ""
    notes: str = ""
    debt: float = 0.0   # ← NEW: total amount owed


@dataclass
class Supplier:
    id: Optional[int] = None
    name: str = ""
    phone: str = ""
    address: str = ""
    notes: str = ""


@dataclass
class PhoneUnit:
    id: Optional[int] = None
    product_id: Optional[int] = None
    imei: str = ""
    buying_price: float = 0.0
    selling_price: float = 0.0
    status: str = "in_stock"
    supplier_id: Optional[int] = None
    notes: str = ""

    @property
    def profit(self) -> float:
        return self.selling_price - self.buying_price


@dataclass
class Payment:
    """Payment made by a customer (partial or full)."""
    id: Optional[int] = None
    customer_id: Optional[int] = None
    sale_id: Optional[int] = None
    amount: float = 0.0
    payment_date: str = ""
    notes: str = ""