db.createUser(
    {
        user: "test",
        pwd: "test",
        roles: [
            {
                role: "dbOwner",
                db: "testDB"
            }
        ]
    }
);
db.createCollection("logs");