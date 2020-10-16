CREATE TABLE Users
(userID INTEGER NOT NULL PRIMARY KEY,
email VARCHAR(256) NOT NULL,
password VARCHAR(256) NOT NULL,
currentBalance DECIMAL(10,2) NOT NULL,
first_name VARCHAR(256) NOT NULL,
last_name VARCHAR(256) NOT NULL,
image VARCHAR(256) -- Store images in directories in file system & store reference to image or file name here; file names must be unique
);

CREATE TABLE Buyers
(userID INTEGER NOT NULL PRIMARY KEY,
email VARCHAR(256) NOT NULL,
password VARCHAR(256) NOT NULL,
currentBalance DECIMAL(10,2) NOT NULL,
first_name VARCHAR(256) NOT NULL,
last_name VARCHAR(256) NOT NULL,
image VARCHAR(256) -- Store images in directories in file system & store reference to image or file name here; file names must be unique
);

CREATE TABLE Sellers
(userID INTEGER NOT NULL PRIMARY KEY,
email VARCHAR(256) NOT NULL,
password VARCHAR(256) NOT NULL,
currentBalance DECIMAL(10,2) NOT NULL,
first_name VARCHAR(256) NOT NULL,
last_name VARCHAR(256) NOT NULL,
image VARCHAR(256), -- Store images in directories in file system & store reference to image or file name here; file names must be unique
description VARCHAR(1250), -- (Optional?) if this is too small/big, we can change it!
avg_rating DECIMAL(10,2) NOT NULL
);

CREATE TABLE Items
(itemID INTEGER NOT NULL PRIMARY KEY,
sellerID INTEGER NOT NULL REFERENCES Sellers(userID),
name VARCHAR(256) NOT NULL,
price DECIMAL(10,2) NOT NULL,
num INTEGER NOT NULL, --this is the count, but count is a keyword, so I changed it
description VARCHAR(1250), -- Optional?
image VARCHAR(256)
);

CREATE TABLE Category
(name VARCHAR(256) NOT NULL PRIMARY KEY,
topItemOne INTEGER REFERENCES Items(itemID), --item ID for most popular item in category (NULL only if no items in category)
topItemTwo INTEGER REFERENCES Items(itemID), --item ID for 2nd most popular in category
topItemThree INTEGER REFERENCES Items(itemID) --item ID for 3rd most popular in category
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
dayTime TIMESTAMP NOT NULL, --combines date & time data (and adds time zone),
num INTEGER NOT NULL, --replaces count bc count is a keyword
PRIMARY KEY(buyerID, itemID, dayTime)
);

CREATE TABLE ItemReview
(buyerID INTEGER NOT NULL REFERENCES Buyers(userID),
itemID INTEGER NOT NULL REFERENCES Items(itemID),
numStars INTEGER NOT NULL,
comments VARCHAR(1250), --Optional
dayTime TIMESTAMP NOT NULL,
PRIMARY KEY(buyerID, itemID)
);

CREATE TABLE SellerReview
(buyerID INTEGER NOT NULL REFERENCES Buyers(userID),
sellerID INTEGER NOT NULL REFERENCES Sellers(userID),
numStars INTEGER NOT NULL,
comments VARCHAR(1250), --Optional
dayTime TIMESTAMP NOT NULL,
PRIMARY KEY(buyerID, sellerID)
);

-- TODO for Zoe: 
	-- CONSTRAINTS TO ADD
		-- Can't review an item you havent purchased at least once in the past
	-- Double-check syntax
	-- Fix load.sql file syntax
	-- Add a ton more synthetic data with randomized script
