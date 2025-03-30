// init mongodb

// Create collections
db.createCollection("issues");
db.createCollection("users");
db.createCollection("executive");
db.createCollection("articles");

// db.createCollection("legislative");
// db.createCollection("judicial");

// Optional: Create indexes if needed (e.g., issue_id as a unique field)
db.issues.createIndex({ issue_id: 1 }, { unique: true });
db.users.createIndex({ userid: 1 }, { unique: true });
db.executive.createIndex({ article_id: 1 }, { unique: true });
db.articles.createIndex({ article_id: 1 }, { unique: true });

// db.legislative.createIndex({ article_id: 1 }, { unique: true });
// db.judicial.createIndex({ article_id: 1 }, { unique: true });
