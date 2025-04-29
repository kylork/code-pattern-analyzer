"""
Sample code that shows an opportunity for applying the Strategy pattern.

This file contains code that selects different behaviors using conditional
logic (if-else statements), which is a good candidate for refactoring
using the Strategy pattern.
"""

import math


class ShippingCalculator:
    """Calculate shipping costs for different shipping methods."""
    
    def calculate_shipping(self, order_amount, shipping_method, distance_km, weight_kg):
        """
        Calculate the shipping cost based on the shipping method.
        
        Args:
            order_amount: The total amount of the order
            shipping_method: The shipping method (standard, express, overnight)
            distance_km: Distance in kilometers
            weight_kg: Weight in kilograms
            
        Returns:
            The calculated shipping cost
        """
        # Calculate shipping cost based on the shipping method
        if shipping_method == "standard":
            # Standard shipping: $5 base + $0.5 per kg + $0.1 per km
            base_cost = 5.0
            weight_cost = 0.5 * weight_kg
            distance_cost = 0.1 * distance_km
            
            # Free shipping for orders over $100
            if order_amount >= 100:
                return 0
                
            return base_cost + weight_cost + distance_cost
            
        elif shipping_method == "express":
            # Express shipping: $15 base + $0.8 per kg + $0.15 per km
            base_cost = 15.0
            weight_cost = 0.8 * weight_kg
            distance_cost = 0.15 * distance_km
            
            # 20% discount for orders over $150
            if order_amount >= 150:
                return 0.8 * (base_cost + weight_cost + distance_cost)
                
            return base_cost + weight_cost + distance_cost
            
        elif shipping_method == "overnight":
            # Overnight shipping: $25 base + $1 per kg + $0.25 per km
            base_cost = 25.0
            weight_cost = 1.0 * weight_kg
            distance_cost = 0.25 * distance_km
            
            # 10% discount for orders over $200
            if order_amount >= 200:
                return 0.9 * (base_cost + weight_cost + distance_cost)
                
            return base_cost + weight_cost + distance_cost
            
        else:
            raise ValueError(f"Unknown shipping method: {shipping_method}")


class TaxCalculator:
    """Calculate taxes for different tax regions."""
    
    def calculate_tax(self, amount, region, item_type=None, is_digital=False):
        """
        Calculate the tax amount based on the region.
        
        Args:
            amount: The order amount
            region: The tax region (us, eu, asia)
            item_type: Type of item (optional)
            is_digital: Whether the item is digital (optional)
            
        Returns:
            The calculated tax amount
        """
        if region == "us":
            # US tax: flat 8.5%
            # Digital goods have special tax of 6%
            if is_digital:
                return amount * 0.06
            return amount * 0.085
            
        elif region == "eu":
            # EU tax: 21% VAT
            # Different VAT rates for different item types
            if item_type == "book":
                return amount * 0.09  # 9% VAT for books
            elif item_type == "food":
                return amount * 0.06  # 6% VAT for food
            else:
                return amount * 0.21  # 21% standard VAT
            
        elif region == "asia":
            # Asia tax varies by amount
            if amount < 100:
                return amount * 0.05  # 5% for small amounts
            elif amount < 1000:
                return amount * 0.08  # 8% for medium amounts
            else:
                return amount * 0.1   # 10% for large amounts
            
        else:
            raise ValueError(f"Unknown tax region: {region}")


# Usage example
def process_order(items, shipping_method, shipping_distance, shipping_weight, tax_region):
    """Process an order with shipping and taxes."""
    # Calculate order total
    order_total = sum(item['price'] * item['quantity'] for item in items)
    
    # Calculate shipping
    shipping_calculator = ShippingCalculator()
    shipping_cost = shipping_calculator.calculate_shipping(
        order_total, shipping_method, shipping_distance, shipping_weight
    )
    
    # Calculate tax
    # Assume the first item's type and digital status for simplicity
    item_type = items[0].get('type') if items else None
    is_digital = items[0].get('is_digital', False) if items else False
    
    tax_calculator = TaxCalculator()
    tax_amount = tax_calculator.calculate_tax(
        order_total, tax_region, item_type, is_digital
    )
    
    # Calculate final total
    final_total = order_total + shipping_cost + tax_amount
    
    return {
        'items_total': order_total,
        'shipping_cost': shipping_cost,
        'tax_amount': tax_amount,
        'final_total': final_total
    }


# Test with different scenarios
if __name__ == "__main__":
    # Test order 1: Standard shipping, US tax
    order1 = [
        {'name': 'Product 1', 'price': 50.0, 'quantity': 2, 'type': 'electronics', 'is_digital': False}
    ]
    result1 = process_order(order1, "standard", 50, 2, "us")
    print("Order 1 Result:", result1)
    
    # Test order 2: Express shipping, EU tax
    order2 = [
        {'name': 'Book', 'price': 25.0, 'quantity': 3, 'type': 'book', 'is_digital': False}
    ]
    result2 = process_order(order2, "express", 100, 3, "eu")
    print("Order 2 Result:", result2)
    
    # Test order 3: Overnight shipping, Asia tax
    order3 = [
        {'name': 'Premium Product', 'price': 500.0, 'quantity': 1, 'type': 'luxury', 'is_digital': False}
    ]
    result3 = process_order(order3, "overnight", 200, 5, "asia")
    print("Order 3 Result:", result3)