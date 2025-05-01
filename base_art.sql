-- Удаляем таблицы, если они существуют
DROP TABLE IF EXISTS Contracts;
DROP TABLE IF EXISTS Roles;
DROP TABLE IF EXISTS Actors;
DROP TABLE IF EXISTS Performances;

-- Создаем таблицы
CREATE TABLE Performances (
    PerformanceID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Budget DECIMAL(10, 2) NOT NULL,
    Year INT NOT NULL,
    INDEX(Year)
) ENGINE=InnoDB;

CREATE TABLE Actors (
    ActorID INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(255) NOT NULL,
    Experience INT NOT NULL,
    Awards VARCHAR(255)
) ENGINE=InnoDB;

CREATE TABLE Roles (
    RoleID INT AUTO_INCREMENT PRIMARY KEY,
    PerformanceID INT,
    RoleName VARCHAR(255) NOT NULL,
    FOREIGN KEY (PerformanceID) REFERENCES Performances(PerformanceID) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE Contracts (
    ContractID INT AUTO_INCREMENT PRIMARY KEY,
    ActorID INT,
    RoleID INT,
    Year INT NOT NULL, 
    BaseSalary DECIMAL(10, 2) NOT NULL,
    PerformanceCount INT DEFAULT 0, 
    Bonus DECIMAL(10, 2) DEFAULT 0.00,
    FOREIGN KEY (ActorID) REFERENCES Actors(ActorID) ON DELETE CASCADE,
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Вставка данных в Performances
INSERT INTO Performances (Title, Budget, Year) VALUES
('Hamlet', 150000.00, 2023),
('Macbeth', 130000.00, 2024),
('Othello', 140000.00, 2023);

-- Вставка данных в Actors
INSERT INTO Actors (Name, Experience, Awards) VALUES
('Maria Petrova', 8, 'Best Dramatic Role'),
('Ivan Smirnov', 12, NULL),
('Anna Kuznetsova', 7, 'Audience Choice Award');

-- Вставка данных в Roles
INSERT INTO Roles (PerformanceID, RoleName) VALUES
(1, 'Hamlet'), -- Role for "Hamlet"
(1, 'Ophelia'), -- Role for "Hamlet"
(2, 'Macbeth'), -- Role for "Macbeth"
(2, 'Lady Macbeth'), -- Role for "Macbeth"
(3, 'Othello'), -- Role for "Othello"
(3, 'Desdemona'); -- Role for "Othello"

-- Вставка данных в Contracts
INSERT INTO Contracts (ActorID, RoleID, Year, BaseSalary, PerformanceCount, Bonus) VALUES
(1, 1, 2023, 55000.00, 11, 4000.00), -- Maria Petrova as Hamlet
(2, 2, 2023, 45000.00, 9, 2000.00), -- Ivan Smirnov as Ophelia
(3, 3, 2024, 65000.00, 13, 5000.00), -- Anna Kuznetsova as Macbeth
(1, 4, 2024, 60000.00, 12, 4500.00), -- Maria Petrova as Lady Macbeth
(2, 5, 2023, 50000.00, 10, 3500.00), -- Ivan Smirnov as Othello
(3, 6, 2023, 55000.00, 11, 4000.00); -- Anna Kuznetsova as Desdemona


-- Просмотр всех записей из Performances
SELECT * FROM Performances;

-- Просмотр всех записей из Actors
SELECT * FROM Actors;

-- Просмотр всех записей из Roles
SELECT * FROM Roles;

-- Просмотр всех записей из Contracts
SELECT * FROM Contracts;