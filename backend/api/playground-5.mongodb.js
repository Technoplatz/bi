
use('bidb');
db.getCollection("_collection").aggregate([
    {
        "$project": {
            "col_id": 1,
            "views": { $objectToArray: "$col_structure.views" }
        }
    }, {
        "$match": {
            "views": {
                "$elemMatch": {
                    "v.enabled": true,
                    "v._tags": {
                        "$elemMatch": { "$in": ["#Technoplatz"] }
                    },
                }
            }
        }
    }
]);

db.getCollection("_collection").findOne({
    "col_structure.views.dn-git-view.enabled": true,
    "col_structure.views.dn-git-view._tags": {
        "$elemMatch": { "$in": ["#Technoplatz"] }
    }
});