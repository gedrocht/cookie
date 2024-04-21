#include "crow.h"
#include "crow/json.h"
#include <string>

std::string currentModel = "default_model.obj";  // Default model filename

std::string getModel() {
    return currentModel;
}

void setModel(const std::string& model) {
    currentModel = model;
}

void startServer() {
    crow::SimpleApp app;

    auto add_cors = [](crow::response &res) {
        res.add_header("Access-Control-Allow-Origin", "*");
        res.add_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
        res.add_header("Access-Control-Allow-Headers", "Content-Type");
    };

    CROW_ROUTE(app, "/api/model").methods("OPTIONS"_method)([&](const crow::request&, crow::response &res){
        add_cors(res);
        res.end();
    });

    /**
     * @api {get} /api/model Request Model Filename
     * @apiName GetModel
     * @apiGroup Model
     *
     * @apiSuccess {String} model Filename of the current 3D model.
    */
    CROW_ROUTE(app, "/api/model").methods("GET"_method)([&](const crow::request&, crow::response &res){
        add_cors(res);
        res.write(getModel());
        res.end();
    });

    /**
     * @api {post} /api/model Update Model Filename
     * @apiName SetModel
     * @apiGroup Model
     *
     * @apiParam {String} model New filename of the 3D model.
     *
     * @apiSuccess (200) Successfully updated the model filename.
     */
    CROW_ROUTE(app, "/api/model").methods("POST"_method)([&](const crow::request& req, crow::response &res){
        auto json_body = crow::json::load(req.body);
        if (!json_body || !json_body.has("model")) {
            res.code = 400;
            res.end("Invalid request");
            return;
        }

        setModel(json_body["model"].s());
        add_cors(res);
        res.code = 200;
        res.end();
    });

    app.port(3001).multithreaded().run();
}
