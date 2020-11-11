CREATE TABLE Users
(userID INTEGER NOT NULL PRIMARY KEY,
email VARCHAR(256),
password VARCHAR(256),
currentBalance DECIMAL(10,2),
first_name VARCHAR(256),
last_name VARCHAR(256),
image VARCHAR(256)); 

CREATE TABLE Buyers
(userID INTEGER NOT NULL PRIMARY KEY,
email VARCHAR(256) NOT NULL,
password VARCHAR(256) NOT NULL,
currentBalance DECIMAL(10,2) NOT NULL,
first_name VARCHAR(256) NOT NULL,
last_name VARCHAR(256) NOT NULL,
image VARCHAR(256)); 

CREATE TABLE Sellers
(userID INTEGER NOT NULL PRIMARY KEY,
email VARCHAR(256) NOT NULL,
password VARCHAR(256) NOT NULL,
currentBalance DECIMAL(10,2) NOT NULL,
first_name VARCHAR(256) NOT NULL,
last_name VARCHAR(256) NOT NULL,
organization VARCHAR(256) NOT NULL, 

image VARCHAR(256), -- Optional
description VARCHAR(1250), -- Optional
avg_rating DECIMAL(10,2) NOT NULL);

CREATE TABLE Items
(itemID INTEGER NOT NULL PRIMARY KEY,
sellerID INTEGER NOT NULL REFERENCES Sellers(userID),
name VARCHAR(256) NOT NULL,
price DECIMAL(10,2) NOT NULL,
num INTEGER NOT NULL, 
description VARCHAR(1250), 
image VARCHAR(256));

CREATE TABLE Category
(name VARCHAR(256) NOT NULL PRIMARY KEY,
topItemOne INTEGER REFERENCES Items(itemID), 

topItemTwo INTEGER REFERENCES Items(itemID), 
topItemThree INTEGER REFERENCES Items(itemID) 
);

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
dayTime TIMESTAMP NOT NULL, 
num INTEGER NOT NULL,
PRIMARY KEY(buyerID, itemID, dayTime)
);

CREATE TABLE ItemReview
(buyerID INTEGER NOT NULL REFERENCES Buyers(userID),
itemID INTEGER NOT NULL REFERENCES Items(itemID), 
numStars INTEGER NOT NULL, 
comments VARCHAR(1250), 
dayTime TIMESTAMP NOT NULL, 
PRIMARY KEY(buyerID, itemID)
);

CREATE TABLE SellerReview
(buyerID INTEGER NOT NULL REFERENCES Buyers(userID),
sellerID INTEGER NOT NULL REFERENCES Sellers(userID), 
numStars INTEGER NOT NULL, 
comments VARCHAR(1250), 
dayTime TIMESTAMP NOT NULL, 
PRIMARY KEY(buyerID, sellerID)
);

CREATE FUNCTION no_itempurchase_no_review() RETURNS TRIGGER AS $$
	BEGIN
		IF NOT EXISTS(SELECT *
			      FROM Purchase
			      WHERE NEW.buyerID = Purchase.buyerID
				AND NEW.itemID = Purchase.itemID)
			THEN RAISE EXCEPTION 'Cannot review an item you have never purchased.';
		END IF;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER no_itempurchase_no_review
  BEFORE INSERT OR UPDATE ON ItemReview
  FOR EACH ROW
  EXECUTE PROCEDURE no_itempurchase_no_review();

CREATE FUNCTION no_sellerpurchase_no_review() RETURNS TRIGGER AS $$
	BEGIN
		IF NOT EXISTS(SELECT *
			      FROM Purchase
			      WHERE NEW.buyerID = Purchase.buyerID
				AND PURCHASE.itemID = Items.ID
				AND Items.sellerID = NEW.sellerID)
			THEN RAISE EXCEPTION 'Cannot review a seller from whom you have never purchased an item.';
		END IF;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_sellerpurchase_no_review
  BEFORE INSERT OR UPDATE ON SellerReview
  FOR EACH ROW
  EXECUTE PROCEDURE no_sellerpurchase_no_review();


CREATE FUNCTION updAveSellerRatings() RETURNS TRIGGER AS $$
	BEGIN
		WITH X AS (SELECT sellerID, AVG(numStars) AS avgR
                        FROM SellerReview
                        WHERE Sellers.sellerID = SellerReview.sellerID
                        GROUP BY sellerID)
		UPDATE Sellers SET avg_rating = X.avgR
		WHERE X.sellerID = NEW.sellerID;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER updAveSellerRatings
  AFTER INSERT OR UPDATE ON SellerReview
  FOR EACH ROW
  EXECUTE PROCEDURE updAveSellerRatings();
