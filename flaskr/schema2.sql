DROP TABLE IF EXISTS obslog;
DROP TABLE IF EXISTS proglog;

CREATE TABLE obslog{
    dateprog VARCHAR(12) NOT NULL,
    obsdate date NOT NULL,
    prog VARCHAR(4) NOT NULL,
    instrument VARCHAR(20) NOT NULL,
    PIObs VARCHAR(20) NOT NULL,
    Obs TEXT NOT NULL,
    starttime time NOT NULL,
    endtime time NOT NULL,

    PRIMARY KEY dateprog,
}

CREATE TABLE proglog{
    dateprog VARCHAR(12) NOT NULL,
    progid VARCHAR(4) NOT NULL,
    progloc VARCHAR(1) NOT NULL,
    progdtn VARCHAR(1) NOT NULL,
    schedstart time NOT NULL,
    schedend time NOT NULL,
    weatherd float NOT NULL,
    weatherb float NOT NULL,
    equipd float NOT NULL,
    equipb float NOT NULL,
    obsd float NOT NULL,
    obsb float NOT NULL,
    notusedd float NOT NULL,
    notusedb float NOT NULL,
    note TEXT NOT NULL,

    PRIMARY KEY (dateprog),
    FOREIGN KEY (dateprog) REFERENCES obslog(dateprog),
    FOREIGN KEY (progid) REFERENCES obslog(prog),
};