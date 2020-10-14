INSERT INTO Buyers VALUES(1, 'flanders@vegas.com', 'god', 50000.00, 'Ned Flanders', NULL);
INSERT INTO Buyers VALUES(2, 'marge@gmail.com', 'bartlisamaggie', 197.61, 'Marge Simpson', NULL);
INSERT INTO Buyers VALUES(3, 'homer.simpsons@gmail.com', 'MargeKnows', 0.00, 'Homer Simpson', NULL);
INSERT INTO Buyers VALUES(4, 'mvh@yahoo.com', 'BartisSoCool', 5.50, 'Milhouse van Houten', NULL);

INSERT INTO Sellers VALUES(5, 'apu@yahoo.com', 'pass', 15.76, 'Apu Nahasapeemapetilon', NULL, NULL, 0);
INSERT INTO Sellers VALUES(6, 'apu@yahoo.com', 'pass', 0.76, 'Apu''s Competition', NULL, NULL, 0);

INSERT INTO Users VALUES(7, 'vaclav@hotmail.com', 'KindaRich?', 11000.05, 'Crazy Vaclav', NULL);

INSERT INTO Category VALUES('Toys', NULL, NULL, NULL);
INSERT INTO Category VALUES('Entertainment', NULL, NULL, NULL);
INSERT INTO Category VALUES('Home Decor', NULL, NULL, NULL);
INSERT INTO Category VALUES('Clothing', NULL, NULL, NULL);
INSERT INTO Category VALUES('School Supplies', NULL, NULL, NULL);
INSERT INTO Category VALUES('Electronics/Technology', NULL, NULL, NULL);

INSERT INTO Items VALUES(100, 5, 'iPhone 12 Pro Max', 1200.00, 10, 'Yay new phone!', NULL);
INSERT INTO Items VALUES(101, 6, 'Notebook', 7.99, 0, 'How else would we take notes??', NULL);
INSERT INTO Items VALUES(102, 5, 'Good Vibes', 0.00, 10000, 'Crucial', NULL);

INSERT INTO ItemInCategory(102, 'School Supplies');
INSERT INTO ItemInCategory(100, 'Electronics/Technology');
INSERT INTO ItemInCategory(101, 'School Supplies');

INSERT INTO ItemReview(1, 102, 5, 'Exquisite vibes', CURRENT_TIME());
-- INSERT INTO ItemReview(3, 100, 5, 'Exquisite vibes', CURRENT_TIME());
