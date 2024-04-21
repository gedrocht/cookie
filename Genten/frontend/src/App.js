import React, { useState } from 'react';
import { Button, CssBaseline, Container, TextField, ThemeProvider, createTheme } from '@mui/material';
import axios from 'axios';

// Create a theme instance.
const theme = createTheme({
  palette: {
    mode: 'dark', // Switches the theme to dark mode
  },
});

function App() {
  const [modelName, setModelName] = useState('');
  const [currentModel, setCurrentModel] = useState('');

  const handleModelNameChange = event => {
    setModelName(event.target.value);
  };

  const apiBaseUrl = process.env.REACT_APP_API_BASE_URL; // Use environment variable

  const setModel = () => {
    axios.post(`${apiBaseUrl}/api/model`, { model: modelName }, {
      headers: {
        'Content-Type': 'application/json'
      }
    }).then(response => console.log(response))
      .catch(error => console.error('Error:', error));
  };

  const fetchModel = () => {
    axios.get(`${apiBaseUrl}/api/model`)
      .then(response => {
        setCurrentModel(response.data);
        console.log(response);
      })
      .catch(error => console.error('Error:', error));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container component="main" maxWidth="xs" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100vh', justifyContent: 'center' }}>
        <TextField
          label="Model Name"
          variant="outlined"
          value={modelName}
          onChange={handleModelNameChange}
          style={{ marginBottom: 20 }}
        />
        <Button variant="contained" color="primary" onClick={setModel}>
          Set Model
        </Button>
        <TextField
          label="Current Model"
          variant="outlined"
          value={currentModel}
          InputProps={{
            readOnly: true,
          }}
          style={{ marginTop: 20, marginBottom: 20 }}
        />
        <Button variant="contained" color="primary" onClick={fetchModel}>
          Fetch Current Model
        </Button>
      </Container>
    </ThemeProvider>
  );
}

export default App;
