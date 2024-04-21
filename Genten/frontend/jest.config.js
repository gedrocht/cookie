module.exports = {
  transform: {
    '^.+\\.jsx?$': 'babel-jest',  // Transform JSX and JS files with babel-jest
  },
  moduleNameMapper: {
    "\\.(css|less|scss|sass)$": "<rootDir>/__mocks__/styleMock.js"
  }
};
