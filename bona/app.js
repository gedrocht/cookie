const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const swaggerUi = require('swagger-ui-express');
const YAML = require('yamljs');
const swaggerDocument = YAML.load('./swagger.yaml');

const app = express();
const port = process.env.PORT || 3000;

app.use(cors());
app.use(bodyParser.json());
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

app.post('/reverse', (req, res) => {
    const { text } = req.body;
    const reversed = text.split('').reverse().join('');
    res.json({ reversed });
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});

module.exports = app; // Export for testing
