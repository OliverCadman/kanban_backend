db.createUser(
    {
        user: "flaskuser",
        pwd: "changeme",
        roles: [
            {
                role: "readWrite",
                db: "flaskdb"
            }
        ]
    }
);
db.createCollection("test"); //MongoDB creates the database when you first store data in that database