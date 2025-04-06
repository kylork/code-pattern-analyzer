"""
Sample file with various code smells to test detection.
"""

import random
import time


# Long method code smell
def process_data(data, options, config, debug=False):
    """
    A very long method that does too many things.
    """
    results = []
    errors = []
    start_time = time.time()
    
    # Initialize processing
    if debug:
        print("Starting data processing")
    
    # Validate input data
    if not isinstance(data, list):
        if debug:
            print("Invalid data type")
        raise ValueError("Data must be a list")
    
    if not data:
        if debug:
            print("Empty data")
        return [], []
    
    # Apply options
    filtered_data = []
    for item in data:
        if options.get("min_value") is not None and item < options["min_value"]:
            continue
        if options.get("max_value") is not None and item > options["max_value"]:
            continue
        filtered_data.append(item)
    
    # Apply transformations
    transformed_data = []
    for item in filtered_data:
        try:
            # Apply scaling if configured
            if config.get("scale"):
                item = item * config["scale"]
            
            # Apply offset if configured
            if config.get("offset"):
                item = item + config["offset"]
            
            # Apply rounding if configured
            if config.get("round"):
                item = round(item, config["round"])
            
            # Apply custom transformation if configured
            if config.get("transform"):
                if config["transform"] == "square":
                    item = item * item
                elif config["transform"] == "sqrt":
                    item = item ** 0.5
                elif config["transform"] == "log":
                    if item <= 0:
                        raise ValueError("Cannot take log of non-positive number")
                    item = math.log(item)
            
            transformed_data.append(item)
        except Exception as e:
            if debug:
                print(f"Error transforming item {item}: {e}")
            errors.append({"item": item, "error": str(e)})
    
    # Calculate statistics
    if transformed_data:
        mean = sum(transformed_data) / len(transformed_data)
        
        # Calculate variance
        variance = 0
        for item in transformed_data:
            variance += (item - mean) ** 2
        variance /= len(transformed_data)
        
        # Calculate min, max, median
        sorted_data = sorted(transformed_data)
        min_val = sorted_data[0]
        max_val = sorted_data[-1]
        
        if len(sorted_data) % 2 == 0:
            median = (sorted_data[len(sorted_data) // 2 - 1] + sorted_data[len(sorted_data) // 2]) / 2
        else:
            median = sorted_data[len(sorted_data) // 2]
        
        stats = {
            "mean": mean,
            "variance": variance,
            "std_dev": variance ** 0.5,
            "min": min_val,
            "max": max_val,
            "median": median,
            "count": len(transformed_data)
        }
        
        # Add percentiles if requested
        if config.get("percentiles"):
            percentiles = {}
            for p in config["percentiles"]:
                index = int(p / 100 * len(sorted_data))
                percentiles[f"p{p}"] = sorted_data[min(index, len(sorted_data) - 1)]
            stats["percentiles"] = percentiles
        
        results.append({"data": transformed_data, "stats": stats})
    
    # Calculate processing time
    end_time = time.time()
    processing_time = end_time - start_time
    
    if debug:
        print(f"Processing completed in {processing_time:.4f} seconds")
    
    return results, errors


# Deep nesting code smell
def validate_user_input(data):
    """
    A function with excessive nesting.
    """
    if data:
        if isinstance(data, dict):
            if "user" in data:
                if "name" in data["user"]:
                    if len(data["user"]["name"]) > 0:
                        if "age" in data["user"]:
                            if isinstance(data["user"]["age"], int):
                                if data["user"]["age"] >= 18:
                                    if data["user"]["age"] <= 120:
                                        if "email" in data["user"]:
                                            if "@" in data["user"]["email"]:
                                                if "." in data["user"]["email"]:
                                                    return True
                                                else:
                                                    return False  # Email must have a dot
                                            else:
                                                return False  # Email must have @
                                        else:
                                            return False  # Email is required
                                    else:
                                        return False  # Age must be <= 120
                                else:
                                    return False  # Age must be >= 18
                            else:
                                return False  # Age must be an integer
                        else:
                            return False  # Age is required
                    else:
                        return False  # Name cannot be empty
                else:
                    return False  # Name is required
            else:
                return False  # User data is required
        else:
            return False  # Data must be a dictionary
    else:
        return False  # Data is required


# Complex condition code smell
def check_eligibility(user, products, settings, promotions, restrictions):
    """
    A function with overly complex conditions.
    """
    if ((user["age"] >= 18 and user["age"] <= 65) or 
        (user["vip_status"] and user["age"] >= 15) or 
        (user["special_approval"] and user["parent_consent"])) and \
       ((user["country"] in settings["allowed_countries"] and not user["country"] in restrictions["blocked_countries"]) or 
        (user["country"] in promotions["promotion_countries"] and user["signed_promotion_terms"])) and \
       ((len(products) > 0 and any(p["category"] in settings["eligible_categories"] for p in products)) or 
        (user["cart_value"] >= settings["minimum_order_value"] and user["payment_verified"])) and \
       (not user["is_banned"] and not user["account_suspended"] and user["email_verified"]) and \
       ((time.time() - user["registration_time"] >= settings["minimum_account_age"]) or 
        (user["referral_count"] >= settings["minimum_referrals"])):
        return True
    else:
        return False


# Long class with too many methods
class Mega:
    """
    A class that does way too many things.
    """
    
    def __init__(self):
        self.data = []
        self.config = {}
        self.users = []
        self.products = []
        self.orders = []
        self.reports = []
        self.stats = {}
        self.cache = {}
        self.errors = []
        self.notifications = []
    
    def load_data(self, source):
        """Load data from a source."""
        # Implementation...
        pass
    
    def save_data(self, destination):
        """Save data to a destination."""
        # Implementation...
        pass
    
    def validate_data(self, data):
        """Validate the data."""
        # Implementation...
        pass
    
    def process_data(self, data):
        """Process the data."""
        # Implementation...
        pass
    
    def transform_data(self, data, transformation):
        """Apply a transformation to the data."""
        # Implementation...
        pass
    
    def add_user(self, user):
        """Add a user."""
        # Implementation...
        pass
    
    def remove_user(self, user_id):
        """Remove a user."""
        # Implementation...
        pass
    
    def get_user(self, user_id):
        """Get a user by ID."""
        # Implementation...
        pass
    
    def update_user(self, user_id, data):
        """Update a user."""
        # Implementation...
        pass
    
    def add_product(self, product):
        """Add a product."""
        # Implementation...
        pass
    
    def remove_product(self, product_id):
        """Remove a product."""
        # Implementation...
        pass
    
    def get_product(self, product_id):
        """Get a product by ID."""
        # Implementation...
        pass
    
    def update_product(self, product_id, data):
        """Update a product."""
        # Implementation...
        pass
    
    def create_order(self, user_id, products):
        """Create a new order."""
        # Implementation...
        pass
    
    def cancel_order(self, order_id):
        """Cancel an order."""
        # Implementation...
        pass
    
    def ship_order(self, order_id):
        """Mark an order as shipped."""
        # Implementation...
        pass
    
    def process_payment(self, order_id, payment_method):
        """Process payment for an order."""
        # Implementation...
        pass
    
    def refund_order(self, order_id):
        """Refund an order."""
        # Implementation...
        pass
    
    def get_order_status(self, order_id):
        """Get the status of an order."""
        # Implementation...
        pass
    
    def generate_report(self, report_type):
        """Generate a report."""
        # Implementation...
        pass
    
    def export_report(self, report_id, format):
        """Export a report in a specific format."""
        # Implementation...
        pass
    
    def calculate_statistics(self):
        """Calculate statistics."""
        # Implementation...
        pass
    
    def send_notification(self, user_id, message):
        """Send a notification to a user."""
        # Implementation...
        pass
    
    def clear_cache(self):
        """Clear the cache."""
        # Implementation...
        pass
    
    def log_error(self, error):
        """Log an error."""
        # Implementation...
        pass
    
    # ... and many more methods