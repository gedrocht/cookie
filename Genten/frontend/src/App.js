// File: src/App.js
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
  const [file, setFile] = useState(null);

  const handleFileChange = event => {
    setFile(event.target.files[0]);
  };

  const uploadModel = () => {
    const formData = new FormData();
    formData.append('file', file);
    axios.post('http://localhost:8080/api/model', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(response => console.log(response))
      .catch(error => console.error('Error:', error));
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* Ensures that the background color is correct for dark mode */}
      <Container component="main" maxWidth="xs" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100vh', justifyContent: 'center' }}>
        <input
          accept="model/*" // Ensure it accepts model files
          style={{ display: 'none' }}
          id="raised-button-file"
          multiple
          type="file"
          onChange={handleFileChange}
        />
        <label htmlFor="raised-button-file">
          <Button variant="contained" color="primary" component="span">
            Choose File
          </Button>
        </label>
        <Button variant="contained" color="primary" onClick={uploadModel} style={{ marginTop: 20 }}>
          Upload Model
        </Button>
      </Container>
    </ThemeProvider>
  );
}

export default App;

