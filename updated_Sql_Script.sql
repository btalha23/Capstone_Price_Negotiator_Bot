-- Create Vendors table
CREATE TABLE Vendors (
    vendor_name VARCHAR(255),
    vendor_id INT PRIMARY KEY,
    vendor_location VARCHAR(255),
    num_listings INT
);

-- Create Brand table
CREATE TABLE Brand (
    brand_id INT PRIMARY KEY,
    brand_name VARCHAR(255)
);

-- Create Category table
CREATE TABLE Category (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(100)
);

-- Create Product table
CREATE TABLE Product (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    vendor_id INT,
    product_price INT,
    product_description VARCHAR(1000),
    product_margin_percent INT,
    reduced_product_price INT,
    product_image VARCHAR(1000),
    brand_id INT,
    category_id INT,
    units_available INT,
    FOREIGN KEY (brand_id) REFERENCES Brand(brand_id),
    FOREIGN KEY (vendor_id) REFERENCES Vendors(vendor_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

-- Populate Vendors table with real names
INSERT INTO Vendors (vendor_id, vendor_name, vendor_location, num_listings) VALUES
(1, 'Williams Sonoma', 'San Francisco, CA', 10),
(2, 'Bed Bath & Beyond', 'Union, NJ', 8),
(3, 'Sur La Table', 'Seattle, WA', 12),
(4, 'Crate & Barrel', 'Northbrook, IL', 15),
(5, 'Macy\'s', 'New York, NY', 7),
(6, 'Bloomingdale\'s', 'New York, NY', 9),
(7, 'Kohl\'s', 'Menomonee Falls, WI', 11),
(8, 'Target', 'Minneapolis, MN', 6),
(9, 'Walmart', 'Bentonville, AR', 14),
(10, 'Amazon', 'Seattle, WA', 5);

-- Populate Brand table with real names
INSERT INTO Brand (brand_id, brand_name) VALUES
(1, 'Cuisinart'),
(2, 'KitchenAid'),
(3, 'OXO'),
(4, 'Breville'),
(5, 'Ninja');

-- Populate Category table
INSERT INTO Category (category_id, category_name) VALUES
(1, 'Kitchen Items');



-- Populate Product table with 20 products in Kitchen Items category, each with multiple vendors
INSERT INTO Product (product_id, product_name, vendor_id, product_price, product_description, product_margin_percent, reduced_product_price, product_image, brand_id, category_id, units_available) VALUES
(1, 'Chef Knife', 1, 50, 'High quality stainless steel knife with wooden handle', 20, 40, '/static/images/chef_knifeimage1.jpg', 1, 1, 100 ),
(2, 'Chef Knife', 2, 52, 'High quality chef knife.', 18, 42, '/static/images/chef_knifeimage2.jpg', 2, 1, 100),
(3, 'Chef Knife', 3, 48, 'High quality chef knife.', 22, 38, '/static/images/chef_knifeimage3.jpg', 1, 1, 100),
(4, 'Cutting Board', 4, 25, 'Durable cutting board.', 15, 20, '/static/images/cutting_board_image1.jpg', 2, 1, 150),
(5, 'Cutting Board', 5, 27, 'Durable cutting board.', 12, 23, '/static/images/cutting_board_image2.jpg', 2, 1, 150),
(6, 'Cutting Board', 6, 24, 'Durable cutting board.', 18, 19, '/static/images/cutting_board_image3.jpg', 2, 1, 150),
(7, 'Saucepan', 7, 40, 'Non-stick saucepan.', 25, 30, '/static/images/saucepan_image1.jpg', 3, 1, 80),
(8, 'Saucepan', 8, 42, 'Non-stick saucepan.', 23, 32, '/static/images/saucepan_image2.jpg', 3, 1, 80),
(9, 'Saucepan', 9, 38, 'Non-stick saucepan.', 28, 28, '/static/images/saucepan_image3.jpg', 3, 1, 80),
(10, 'Blender', 10, 70, 'High power blender.', 30, 50, '/static/images/blender_image1.jpg', 4, 1, 60),
(11, 'Blender', 1, 68, 'High power blender.', 32, 48, '/static/images/blender_image2.jpg', 4, 1, 60),
(12, 'Blender', 2, 72, 'High power blender.', 28, 52, '/static/images/blender_image3.jpg', 4, 1, 60),
(13, 'Toaster', 3, 30, '4-slice toaster.', 10, 25, '/static/images/toaster_image1.jpg', 5, 1, 120),
(14, 'Toaster', 4, 32, '4-slice toaster.', 8, 27, '/static/images/toaster_image2.jpg', 5, 1, 120),
(15, 'Toaster', 5, 28, '4-slice toaster.', 12, 24, '/static/images/toaster_image3.jpg', 5, 1, 120),
(19, 'Coffee Maker', 9, 60, 'Programmable coffee maker.', 15, 50, '/static/images/coffee_maker_image1.jpg', 2, 1, 90),
(20, 'Coffee Maker', 10, 58, 'Programmable coffee maker.', 17, 48, '/static/images/coffee_maker_image2.jpg', 2, 1, 90),
(21, 'Coffee Maker', 10, 58, 'Programmable coffee maker.', 17, 48, '/static/images/coffee_maker_image3.jpg', 2, 1, 90);


CREATE TABLE CustomerPreferences (
    preference_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    category_id INT,
    brand_id INT,
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id),
    FOREIGN KEY (brand_id) REFERENCES Brand(brand_id)
);

CREATE TABLE CustomerInteractions (
    interaction_id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    product_id INT,
    interaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    interaction_type ENUM('view', 'purchase', 'cart_add', 'wishlist_add'),
    FOREIGN KEY (customer_id) REFERENCES customer(customer_id),
    FOREIGN KEY (product_id) REFERENCES Product(product_id)
);

CREATE TABLE Customer (
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    customer_id INT PRIMARY KEY AUTO_INCREMENT,
    num_products_bought INT,
    customer_email VARCHAR(100),
    customer_location VARCHAR(100)
);