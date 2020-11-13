
CREATE TABLE Buyers
(userID INTEGER NOT NULL PRIMARY KEY,
email VARCHAR(256) NOT NULL,
password VARCHAR(256) NOT NULL,
currentBalance DECIMAL(10,2) NOT NULL,
first_name VARCHAR(256) NOT NULL,
last_name VARCHAR(256) NOT NULL,
image VARCHAR(256)); -- Store reference to image or file name here; file names must be unique

CREATE TABLE Sellers
(userID INTEGER NOT NULL PRIMARY KEY REFERENCES Buyers(userID),
organization VARCHAR(256) NOT NULL, -- Organization/Store name displayed; 
				    -- the user can set it to their own name, 
				    -- but this is the name displayed on the seller page
image VARCHAR(256), -- Optional, image for organization not for personal user profile
description VARCHAR(1250), -- Optional
avg_rating DECIMAL(10,2) NOT NULL);

CREATE TABLE Items
(itemID INTEGER NOT NULL PRIMARY KEY,
sellerID INTEGER NOT NULL REFERENCES Sellers(userID),
name VARCHAR(256) NOT NULL,
price DECIMAL(10,2) NOT NULL,
avg_rating DECIMAL(10,2) NOT NULL,
num INTEGER NOT NULL, -- Number of items available
description VARCHAR(1250), -- Optional
image VARCHAR(256));

CREATE TABLE Category
(name VARCHAR(256) NOT NULL PRIMARY KEY,
topItemOne INTEGER REFERENCES Items(itemID), -- item ID for most popular item in category 
					     -- (NULL only if no items in category)
topItemTwo INTEGER REFERENCES Items(itemID), -- item ID for 2nd most popular in category
topItemThree INTEGER REFERENCES Items(itemID) -- item ID for 3rd most popular in category
);					-- if all 3 items null: show 3 alphabetically first items

CREATE TABLE ItemInCategory
(itemID INTEGER NOT NULL REFERENCES Items(itemID),
category VARCHAR(256) NOT NULL REFERENCES Category(name),
PRIMARY KEY(itemID, category)
);

CREATE TABLE Cart
(buyerID INTEGER NOT NULL REFERENCES Buyers(userID),
itemID INTEGER NOT NULL REFERENCES Items(itemID),
PRIMARY KEY(buyerID, itemID)
);

CREATE TABLE Purchase
(buyerID INTEGER NOT NULL REFERENCES Buyers(userID),
itemID INTEGER NOT NULL REFERENCES Items(itemID),
dayTime TIMESTAMP NOT NULL, -- Date, Time, Timezone data
num INTEGER NOT NULL, -- Quantity purchased
PRIMARY KEY(buyerID, itemID, dayTime)
);

CREATE TABLE ItemReview
(buyerID INTEGER NOT NULL REFERENCES Buyers(userID), -- Field set by website
itemID INTEGER NOT NULL REFERENCES Items(itemID), -- Field set by website
numStars INTEGER NOT NULL, -- Field for User to input
comments VARCHAR(1250), -- Optional, field for User to input
dayTime TIMESTAMP NOT NULL, -- Field set by website (current time of submission)
PRIMARY KEY(buyerID, itemID)
);

CREATE TABLE SellerReview
(buyerID INTEGER NOT NULL REFERENCES Buyers(userID), -- Field set by website
sellerID INTEGER NOT NULL REFERENCES Sellers(userID), -- Field set by website
numStars INTEGER NOT NULL, -- Field for User to input
comments VARCHAR(1250), -- Optional, field for User to input
dayTime TIMESTAMP NOT NULL, -- Field set by website (current time of submission)
PRIMARY KEY(buyerID, sellerID)
);


delimiter //
CREATE TRIGGER no_itempurchase_no_review BEFORE INSERT OR UPDATE ON ItemReview
       FOR EACH ROW
       BEGIN
	DECLARE msg varchar(128);
	IF NOT EXISTS(SELECT *
		      FROM Purchase
		      WHERE NEW.buyerID = Purchase.buyerID
			AND NEW.itemID = Purchase.itemID)
		-- THEN RAISE EXCEPTION 'Cannot review an item you have never purchased.';
	THEN
		SET msg = concat('Error: Cannot review an item you have never purchased.';
       		signal sqlstate '45000' set message_text = msg;
	END IF;
       END;
//
delimiter;


delimiter //
CREATE TRIGGER no_sellerpurchase_no_review BEFORE INSERT OR UPDATE ON SellerReview
       FOR EACH ROW
       BEGIN
	DECLARE msg varchar(128);
	IF NOT EXISTS(SELECT *
		      FROM Purchase, Items
		      WHERE NEW.buyerID = Purchase.buyerID
			AND PURCHASE.itemID = Items.ID
			AND Items.sellerID = NEW.sellerID)
	THEN
		SET msg = concat('Error: Cannot review a seller from whom you have never purchased an item.';
       		signal sqlstate '45000' set message_text = msg;
	END IF;
       END;
//
delimiter;


delimiter //
CREATE TRIGGER updAveSellerRatings AFTER INSERT OR UPDATE ON SellerReview
       FOR EACH ROW
       BEGIN

	WITH X AS (SELECT sellerID, AVG(numStars) AS avgR
                   FROM SellerReview, Sellers
                   WHERE Sellers.sellerID = SellerReview.sellerID
                   GROUP BY sellerID)
	UPDATE Sellers SET avg_rating = X.avgR
	WHERE X.sellerID = NEW.sellerID
	  AND NEW.sellerID = Sellers.sellerID;

       END;
//
delimiter;


delimiter //
CREATE TRIGGER updAveSellerRatings AFTER INSERT OR UPDATE ON ItemReview
       FOR EACH ROW
       BEGIN
	WITH X AS (SELECT itemID, AVG(numStars) AS avgR
                        FROM ItemReview, Items
                        WHERE Items.itemID = ItemReview.itemID
                        GROUP BY itemID)
		UPDATE Items SET avg_rating = X.avgR
		WHERE X.itemID = NEW.itemID;

	-- Updating Top Item in Category
	WITH Y AS (SELECT Items.itemID AS item, Category.name AS category, Items.avg_rating AS top
		   FROM ItemInCategory, Items, Category
		   WHERE Items.itemID = ItemInCategory.itemID
		     AND ItemInCategory.category = Category.name
		     AND (Category.name, Items.avg_rating) IN (
			SELECT Category.name, max(Items.avg_rating)
			FROM Category, Items
			WHERE Items.itemID = ItemInCategory.itemID
			  AND ItemInCategory.category = Category.name
			GROUP BY Category.name
			)
		   )
	UPDATE Category SET topItemOne = Y.item
	WHERE Y.category = Category.name;

	-- Updating Second Top-Rated Item in Category
	WITH Z AS (SELECT Items.itemID AS item, Category.name AS category, Items.avg_rating AS second
		   FROM ItemInCategory, Items, Category
		   WHERE Items.itemID = ItemInCategory.itemID
		     AND ItemInCategory.category = Category.name
		     AND (Category.name, Items.avg_rating) IN (
			SELECT Category.name, max(Items.avg_rating)
			FROM Category, Items, Y
			WHERE Items.itemID = ItemInCategory.itemID
			  AND ItemInCategory.category = Category.name
			  AND Y.category = Category.name
			  AND Items.avg_rating <= Y.top
			  AND Items.itemID <> Category.topItemOne
			GROUP BY Category.name
			)
		   )
	UPDATE Category SET topItemTwo = Z.item
	WHERE Z.category = Category.name;

	-- Updating Third Top-Rated Item in Category
	WITH L AS (SELECT Items.itemID AS item, Category.name AS category, Items.avg_rating AS third
		   FROM ItemInCategory, Items, Category
		   WHERE Items.itemID = ItemInCategory.itemID
		     AND ItemInCategory.category = Category.name
		     AND (Category.name, Items.avg_rating) IN (
			SELECT Category.name, max(Items.avg_rating)
			FROM Category, Items, Z
			WHERE Items.itemID = ItemInCategory.itemID
			  AND ItemInCategory.category = Category.name
			  AND Z.category = Category.name
			  AND Items.avg_rating <= Z.second
			  AND Items.itemID <> (Category.topItemOne OR Category.topItemTwo)
			GROUP BY Category.name
			)
		   )
	UPDATE Category SET topItemThree = L.item
	WHERE L.category = Category.name;

       END;
//
delimiter;



-- TODO: Troubleshoot triggers (especially for updating top in category); there are definitely some errors in here
-- TODO: Fix load.sql to fit new schemas
