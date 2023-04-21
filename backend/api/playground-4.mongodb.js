
use('bidb');
db.getCollection("_collection").aggregate([
    {
        "$match": {
            "col_id": "delivery",
            "col_structure.views": {
                "$elemMatch": {
                    "id": "dnn-git-view",
                    "enabled": true,
                    "_tags": {
                        "$elemMatch": { "$in": ["#Technoplatz"] }
                    }
                }
            }
        }
    },
    {
        "$project": {
            "col_structure.views": 1
        }
    }
]);



