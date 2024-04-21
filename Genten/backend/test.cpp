#include "gtest/gtest.h"
#include "server.cpp"  // Include the implementation file

// Test the initial state of the model
TEST(ModelTest, DefaultModel) {
    EXPECT_EQ(getModel(), "default_model.obj");
}

// Test setting the model
TEST(ModelTest, SetModel) {
    setModel("new_model.obj");
    EXPECT_EQ(getModel(), "new_model.obj");
    setModel("default_model.obj");  // Reset to default for other tests
}

// Test the reset to default
TEST(ModelTest, ResetModel) {
    setModel("temporary_model.obj");
    EXPECT_EQ(getModel(), "temporary_model.obj");
    setModel("default_model.obj");
    EXPECT_EQ(getModel(), "default_model.obj");
}

