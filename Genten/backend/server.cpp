#include "crow.h"
#include "crow/json.h"
#include <string>
#include "crow/middlewares/cors.h"
#include <iostream>
#include <fstream>
#include <mutex>
#include <curl/curl.h>

std::string currentModel = "default_model.obj";  // Default model filename

std::string getModel() {
    return currentModel;
}

void setModel(const std::string& model) {
    currentModel = model;
}

void sendLog(const std::string& message) {
    CURL* curl = curl_easy_init();
    if(curl) {
        const std::string json = "{\"message\": \"" + message + "\"}";

        curl_easy_setopt(curl, CURLOPT_URL, "http://logstash:8080");
        curl_easy_setopt(curl, CURLOPT_POSTFIELDS, json.c_str());

        CURLcode res = curl_easy_perform(curl);
        if(res != CURLE_OK) {
            fprintf(stderr, "curl_easy_perform() failed: %s\n", curl_easy_strerror(res));
        }

        curl_easy_cleanup(curl);
    }
}

void startServer() {
    // Enable CORS
    crow::App<crow::CORSHandler> app;
    app.loglevel(crow::LogLevel::Warning);

    // Customize CORS
    auto& cors = app.get_middleware<crow::CORSHandler>();

    // clang-format off
    cors
      .global()
        .headers("X-Custom-Header", "Upgrade-Insecure-Requests")
        .methods("POST"_method, "GET"_method)
      .prefix("/api")
        .origin("*");
    // clang-format on
    /**
     * @api {get} /api/model Request Model Filename
     * @apiName GetModel
     * @apiGroup Model
     *
     * @apiSuccess {String} model Filename of the current 3D model.
    */
    CROW_ROUTE(app, "/api/model").methods("GET"_method)([&](const crow::request&, crow::response &res){
        sendLog("Handling GET request");
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
        sendLog("Handling POST request");
        auto json_body = crow::json::load(req.body);
        if (!json_body || !json_body.has("model")) {
            res.code = 400;
            std::cout << "Invalid request\n";
            res.end("Invalid request");
            return;
        }
        setModel(json_body["model"].s());
        res.code = 200;
        res.end();
    });

    app.port(3001).multithreaded().run();
}